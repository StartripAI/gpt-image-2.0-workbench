# SPDX-License-Identifier: Apache-2.0
"""`i2w batch` — sweep templates across quality tiers and submit batches.

Subcommands:
    sweep   — render a template, build (size x quality x n) BatchJobLines,
              submit either to ``images.generate`` immediately or to the
              Batch API (50% async discount).
    status  — fetch a batch's progress.
    fetch   — download completed batch outputs to ``--out-dir``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from ..compiler.loader import load_template, load_vars
from ..compiler.renderer import render
from ..costing.pricing import estimate_cost
from ..ledger import LedgerEntry, append_entry
from ..runtimes.batch_api import (
    BatchApiError,
    BatchJobLine,
    fetch_batch_results,
    get_batch_status,
    serialize_lines_jsonl,
    submit_batch,
)

# Soft import: errors module is owned by Agent X1 — be tolerant when the
# module hasn't landed.
try:  # pragma: no cover
    from ..errors import ExitCode, cli_dispatch
except ImportError:  # pragma: no cover
    ExitCode = None  # type: ignore[assignment]
    cli_dispatch = None  # type: ignore[assignment]


batch_app = typer.Typer(
    no_args_is_help=True,
    help="Run batch sweeps across quality tiers and variable matrices.",
)


_VALID_ROUTES = ("immediate", "batch-api")


def _exit(code: str | int, message: str) -> typer.Exit:
    if isinstance(code, str) and ExitCode is not None:
        code_int = int(getattr(ExitCode, code, 4))
    elif isinstance(code, str):
        code_int = {"VALIDATION": 4, "API": 5, "INTERNAL": 1}.get(code, 1)
    else:
        code_int = code
    typer.echo(message, err=True)
    return typer.Exit(code=code_int)


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _append_ledger(entry: LedgerEntry) -> None:
    try:
        append_entry(entry)
    except Exception:  # noqa: BLE001
        pass


def _resolve_template(template: str) -> Path:
    """Resolve a template id (or path) to a YAML file on disk.

    Accepts:
      * direct path (existing .yml file),
      * dotted/slashed id like ``business_swot_card`` or ``business/swot_card``.
    """
    candidate = Path(template)
    if candidate.exists() and candidate.is_file():
        return candidate

    # Locate the templates/ root by walking up from this module.
    here = Path(__file__).resolve()
    repo_root = here.parents[3]
    templates_dir = repo_root / "templates"
    if not templates_dir.exists():
        raise FileNotFoundError(
            f"templates dir not found at {templates_dir}; pass --template as a path"
        )

    # Try direct id-as-filename matches.
    target_id = template.replace("/", "_")
    for path in templates_dir.rglob("*.yml"):
        if path.stem == target_id or path.stem == template:
            return path
        # Also match by reading the file's id field — but that's expensive,
        # so only do it if filename matching failed and we have <50 files.
    candidates = list(templates_dir.rglob("*.yml"))
    if len(candidates) < 50:
        for path in candidates:
            try:
                spec = load_template(path)
                if spec.id == template:
                    return path
            except Exception:  # noqa: BLE001
                continue
    raise FileNotFoundError(f"could not resolve template {template!r}")


def _build_lines(
    template_id: str,
    rendered_prompt: str,
    sizes: list[str],
    qualities: list[str],
    n_per: int,
) -> list[BatchJobLine]:
    lines: list[BatchJobLine] = []
    for size in sizes:
        for quality in qualities:
            for k in range(n_per):
                custom_id = f"{template_id}__{size}__{quality}__{k:02d}"
                body: dict[str, Any] = {
                    "model": "gpt-image-2",
                    "prompt": rendered_prompt,
                    "size": size,
                    "quality": quality,
                    "n": 1,
                }
                lines.append(
                    BatchJobLine(
                        custom_id=custom_id,
                        method="POST",
                        url="/v1/images/generations",
                        body=body,
                    )
                )
    return lines


@batch_app.command("sweep")
def sweep(
    template: Annotated[str, typer.Option("--template", help="Template id or path")],
    vars: Annotated[Path, typer.Option("--vars", help="YAML vars file (matrix-aware)")],
    quality: Annotated[
        str,
        typer.Option("--quality", help="Comma-separated qualities"),
    ] = "low,medium",
    sizes: Annotated[
        str,
        typer.Option("--sizes", help="Comma-separated sizes"),
    ] = "1024x1024",
    n_per: Annotated[int, typer.Option("--n-per", help="Renders per (size, quality)")] = 1,
    route: Annotated[
        str,
        typer.Option("--route", help="immediate | batch-api"),
    ] = "immediate",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Print plan; do not submit")] = False,
    out_dir: Annotated[
        Path,
        typer.Option("--out-dir", help="Where Batch fetches will land"),
    ] = Path("out/batch"),
) -> None:
    """Compose a batch (size x quality x n) for the template+vars."""
    console = Console()

    if route not in _VALID_ROUTES:
        raise _exit(
            "VALIDATION",
            f"invalid --route {route!r}; expected one of {_VALID_ROUTES}",
        )
    if n_per <= 0:
        raise _exit("VALIDATION", f"--n-per must be > 0, got {n_per}")

    size_list = _split_csv(sizes)
    quality_list = _split_csv(quality)
    if not size_list or not quality_list:
        raise _exit(
            "VALIDATION", "must provide >= 1 size and >= 1 quality"
        )

    try:
        template_path = _resolve_template(template)
    except FileNotFoundError as exc:
        raise _exit("VALIDATION", str(exc)) from exc

    try:
        spec = load_template(template_path)
    except Exception as exc:  # noqa: BLE001
        raise _exit("VALIDATION", f"failed to load template {template_path}: {exc}") from exc

    if not vars.exists():
        raise _exit("VALIDATION", f"vars file not found: {vars}")

    try:
        vars_dict = load_vars(vars)
    except Exception as exc:  # noqa: BLE001
        raise _exit("VALIDATION", f"failed to load vars {vars}: {exc}") from exc

    lang = "en" if "en" in spec.language_targets else spec.language_targets[0]
    try:
        rendered_prompt = render(spec, vars_dict, lang)
    except Exception as exc:  # noqa: BLE001
        raise _exit("VALIDATION", f"render failed: {exc}") from exc

    try:
        lines = _build_lines(
            template_id=spec.id,
            rendered_prompt=rendered_prompt,
            sizes=size_list,
            qualities=quality_list,
            n_per=n_per,
        )
    except Exception as exc:  # noqa: BLE001
        raise _exit("VALIDATION", f"invalid batch request: {exc}") from exc

    # Cost forecast.
    total_usd = 0.0
    table = Table(title=f"Sweep plan: {spec.id} ({route})")
    table.add_column("custom_id", justify="left")
    table.add_column("size", justify="left")
    table.add_column("quality", justify="left")
    table.add_column("est_usd", justify="right")
    for size in size_list:
        for q in quality_list:
            for k in range(n_per):
                try:
                    est = estimate_cost(size=size, quality=q, n=1)  # type: ignore[arg-type]
                except ValueError as exc:
                    raise _exit(
                        "VALIDATION", f"invalid (size={size}, quality={q}): {exc}"
                    ) from exc
                total_usd += est.total_usd
                table.add_row(
                    f"{spec.id}__{size}__{q}__{k:02d}",
                    size,
                    q,
                    f"${est.total_usd:.4f}",
                )
    console.print(table)

    discount_note = ""
    if route == "batch-api":
        discounted = total_usd * 0.5
        discount_note = (
            f" (Batch API ~50% discount: ~${discounted:.4f})"
        )
    console.print(
        f"total_estimated=${total_usd:.4f}{discount_note}",
        markup=False,
    )
    console.print(
        f"jobs={len(lines)}  route={route}  dry_run={dry_run}",
        markup=False,
    )

    if dry_run:
        if route == "batch-api":
            typer.echo("batch_jsonl:")
            typer.echo(serialize_lines_jsonl(lines).rstrip())
        console.print("dry-run: not submitting any jobs.", markup=False)
        return

    if route == "batch-api":
        try:
            result = submit_batch(lines, dry_run=False)
        except (BatchApiError, ValueError) as exc:
            _append_ledger(
                LedgerEntry(
                    kind="batch_submit",
                    template_id=spec.id,
                    status="error",
                    cost_usd=total_usd,
                    n=len(lines),
                    error_code="batch_submission_failed",
                    error_exit_code=5,
                    extra={"route": route, "error": str(exc)},
                )
            )
            raise _exit("API", f"batch submission failed: {exc}") from exc
        _append_ledger(
            LedgerEntry(
                kind="batch_submit",
                template_id=spec.id,
                status="ok",
                cost_usd=total_usd * 0.5,
                n=len(lines),
                extra={
                    "batch_id": result.batch_id,
                    "batch_status": result.status,
                    "route": route,
                },
            )
        )
        console.print(
            f"submitted batch_id={result.batch_id}  status={result.status}  "
            f"requests={result.request_count}",
            markup=False,
        )
        console.print(
            f"results will land in {out_dir} after fetch.",
            markup=False,
        )
        return

    # Immediate route — call images.generate per request.
    out_dir.mkdir(parents=True, exist_ok=True)
    from ..runtimes.images_api import generate as images_generate
    from ..runtimes.types import GenerateRequest

    failures = 0
    succeeded = 0
    for line in lines:
        body = line.body
        try:
            req = GenerateRequest(
                prompt=body["prompt"],
                size=body["size"],
                quality=body["quality"],
                n=int(body.get("n", 1)),
            )
            images_generate(req)
            succeeded += 1
        except Exception as exc:  # noqa: BLE001
            failures += 1
            console.print(
                f"[red]{line.custom_id}: {exc}[/red]",
                markup=True,
            )

    console.print(
        f"immediate: succeeded={succeeded}  failed={failures}",
        markup=False,
    )
    _append_ledger(
        LedgerEntry(
            kind="batch_submit",
            template_id=spec.id,
            status="ok" if failures == 0 else "error",
            cost_usd=total_usd,
            n=len(lines),
            error_code=None if failures == 0 else "batch_immediate_failed",
            error_exit_code=None if failures == 0 else 5,
            extra={"route": route, "succeeded": succeeded, "failed": failures},
        )
    )
    if failures:
        raise _exit("API", f"{failures} requests failed")


@batch_app.command("status")
def status(
    batch_id: Annotated[str, typer.Argument(help="Batch id from `i2w batch sweep`")],
) -> None:
    """Print the current status of a batch."""
    console = Console()
    if not batch_id or not batch_id.strip():
        raise _exit("VALIDATION", "batch_id is required")
    try:
        st = get_batch_status(batch_id)
    except (BatchApiError, ValueError) as exc:
        _append_ledger(
            LedgerEntry(
                kind="batch_status",
                status="error",
                error_code="batch_status_failed",
                error_exit_code=5,
                extra={"batch_id": batch_id, "error": str(exc)},
            )
        )
        raise _exit("API", f"could not fetch status: {exc}") from exc
    _append_ledger(
        LedgerEntry(
            kind="batch_status",
            status="ok",
            n=st.total_count,
            extra={
                "batch_id": st.batch_id,
                "batch_status": st.status,
                "completed": st.completed_count,
                "failed": st.failed_count,
                "output_file_id": st.output_file_id,
            },
        )
    )
    console.print(
        f"batch_id={st.batch_id}  status={st.status}  "
        f"completed={st.completed_count}/{st.total_count}  failed={st.failed_count}",
        markup=False,
    )
    if st.output_file_id:
        console.print(f"output_file_id={st.output_file_id}", markup=False)


@batch_app.command("fetch")
def fetch(
    batch_id: Annotated[str, typer.Argument(help="Batch id from `i2w batch sweep`")],
    out_dir: Annotated[
        Path,
        typer.Option("--out-dir", help="Where to write image PNGs"),
    ] = Path("out/batch"),
) -> None:
    """Download completed batch results into ``--out-dir``."""
    console = Console()
    if not batch_id or not batch_id.strip():
        raise _exit("VALIDATION", "batch_id is required")
    try:
        written = fetch_batch_results(batch_id, out_dir)
    except (BatchApiError, ValueError) as exc:
        _append_ledger(
            LedgerEntry(
                kind="batch_fetch",
                status="error",
                error_code="batch_fetch_failed",
                error_exit_code=5,
                extra={"batch_id": batch_id, "out_dir": str(out_dir), "error": str(exc)},
            )
        )
        raise _exit("API", f"fetch failed: {exc}") from exc
    _append_ledger(
        LedgerEntry(
            kind="batch_fetch",
            status="ok",
            n=written,
            extra={"batch_id": batch_id, "out_dir": str(out_dir), "written": written},
        )
    )
    console.print(
        f"wrote {written} image(s) to {out_dir}",
        markup=False,
    )


__all__ = ["batch_app"]

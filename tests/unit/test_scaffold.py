# SPDX-License-Identifier: Apache-2.0
def test_package_imports():
    import image2_workbench

    assert image2_workbench.__version__ == "0.2.0"


def test_package_exports_version_only():
    import image2_workbench

    assert "__version__" in image2_workbench.__all__

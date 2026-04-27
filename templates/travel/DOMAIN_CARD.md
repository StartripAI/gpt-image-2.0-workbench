# travel — domain card

## FOR
- Destination marketing and wanderlust artifacts.
- Vintage-style destination posters, single-page itineraries, illustrated
  tourist maps.
- Hospitality / concierge-grade print and share-ready cards.

## NOT FOR
- Documentary photography of a place — route to `photography/`.
- Urban architecture concept renderings — route to `architecture/`.
- Casual social-media travel snaps and feed posts — route to `social_media/`.
- Real-city marketing using a real place name (Paris, Tokyo, NYC). All demo
  destinations are fictional or generic ("Costa Lumina coast", "hill village").

## Key axes
- Form: poster (hero illustration), itinerary (vertical card), map (top-down).
- Aspect: 2:3 portrait poster vs. 9:16 itinerary card vs. 16:9 wide map.
- Grader: posters and itineraries lean on `text_fidelity_dense` (named place +
  taglines + day items); the map relies on `layout` for its POI structure.

## Templates in domain
- `travel_destination_poster` — poster, 2:3 (1024x1536), `text_fidelity_dense`.
  Vintage screen-print vibe with destination, tagline, year.
- `travel_itinerary_card` — infographic, 9:16 (1088x1920), `text_fidelity_dense`.
  Vertical Day 1 / Day 2 / Day 3 timeline card.
- `travel_map_guide` — diagram, 16:9 (1920x1088), `layout`.
  Top-down illustrated map with three numbered POIs.

Demo destinations are fictional ("Costa Lumina") or generic descriptors;
never reference real cities, real landmarks, or real flags by name.

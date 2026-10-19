# Education Across the States — Public Feed

Public RSS feed and episode index pages for the **Education Across the States**
umbrella podcast: daily education coverage from Maine, Vermont, Massachusetts,
Connecticut, and Rhode Island, plus regional specials and a shared
"IDEA, Section by Section" series.

- **RSS feed:** `feed.xml` (served at
  `https://kerrycurtis.github.io/education-across-the-states-feed/feed.xml`)
- **State index pages:** `maine.html`, `vermont.html`, `massachusetts.html`,
  `connecticut.html`, `rhode-island.html`
- **Regional special pages:** `region-new-england.html`, `region-atlantic.html`,
  `region-mid-atlantic.html`, `region-midwest.html`, `region-west.html`,
  `region-southern.html`

## How it works

The `.github/workflows/update-feed.yml` Action runs daily (~8:20 AM ET) and on
manual dispatch. It:

1. Pulls the upstream author feed from
   `https://muse.ai/podcasts/feed/1337692426099284/ac5626cf-254c-4fb4-b4a4-7aa3dd422fa5`
2. Strips any GUIDs listed in `EXCLUDED_GUIDS` (used when a corrected
   "(Revised)" edition replaces an original episode)
3. Normalizes the iTunes author/category/owner tags and the self link
4. Writes `feed.xml`, then runs `build-index.py` to regenerate all index pages
5. Commits and pushes anything that changed (GitHub Pages serves the site)

## Setup notes

- GitHub Pages must be enabled on this repo (source: main branch, root).
- To pull an episode from the public feed, add its GUID to `EXCLUDED_GUIDS`
  in the workflow file and re-run the workflow.
- `build-index.py` groups episodes by their `[State]` / `[Region]` title
  prefix. Episode titles must keep that prefix format.

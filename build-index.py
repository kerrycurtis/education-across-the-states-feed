#!/usr/bin/env python3
"""Build per-state and per-region index pages for the Education Across the States
umbrella podcast feed.

Reads feed.xml in this directory, groups episodes by their [State] / [Region]
title prefix, and writes:
  index.html            - show homepage with latest episodes + links to every page
  <state-slug>.html     - one page per state (maine, vermont, massachusetts,
                          connecticut, rhode-island, new-hampshire)
  region-<slug>.html    - one page per regional special (new-england, atlantic,
                          mid-atlantic, midwest, west, southern)

Run after feed.xml is rebuilt. Safe to re-run; output is deterministic.
"""
import html
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FEED_FILE = os.path.join(HERE, "feed.xml")

STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming"
]
REGIONS = ["New England", "Atlantic", "Mid-Atlantic", "Midwest", "West", "Southern"]

# Episode titles carry a bracket prefix like [NH] or [New Mexico]; map it to
# the full state name used for grouping and page slugs.
PREFIX_TO_STATE = {
    "NH": "New Hampshire",
    "ME": "Maine",
    "VT": "Vermont",
    "MA": "Massachusetts",
    "CT": "Connecticut",
    "RI": "Rhode Island",
    "Alabama": "Alabama",
    "Alaska": "Alaska",
    "Arizona": "Arizona",
    "Arkansas": "Arkansas",
    "California": "California",
    "Colorado": "Colorado",
    "Connecticut": "Connecticut",
    "Delaware": "Delaware",
    "Florida": "Florida",
    "Georgia": "Georgia",
    "Hawaii": "Hawaii",
    "Idaho": "Idaho",
    "Illinois": "Illinois",
    "Indiana": "Indiana",
    "Iowa": "Iowa",
    "Kansas": "Kansas",
    "Kentucky": "Kentucky",
    "Louisiana": "Louisiana",
    "Maine": "Maine",
    "Maryland": "Maryland",
    "Massachusetts": "Massachusetts",
    "Michigan": "Michigan",
    "Minnesota": "Minnesota",
    "Mississippi": "Mississippi",
    "Missouri": "Missouri",
    "Montana": "Montana",
    "Nebraska": "Nebraska",
    "Nevada": "Nevada",
    "New Hampshire": "New Hampshire",
    "New Jersey": "New Jersey",
    "New Mexico": "New Mexico",
    "New York": "New York",
    "North Carolina": "North Carolina",
    "North Dakota": "North Dakota",
    "Ohio": "Ohio",
    "Oklahoma": "Oklahoma",
    "Oregon": "Oregon",
    "Pennsylvania": "Pennsylvania",
    "Rhode Island": "Rhode Island",
    "South Carolina": "South Carolina",
    "South Dakota": "South Dakota",
    "Tennessee": "Tennessee",
    "Texas": "Texas",
    "Utah": "Utah",
    "Vermont": "Vermont",
    "Virginia": "Virginia",
    "Washington": "Washington",
    "West Virginia": "West Virginia",
    "Wisconsin": "Wisconsin",
    "Wyoming": "Wyoming",
}

PAGE_CSS = """
body{font-family:-apple-system,system-ui,'Segoe UI',Roboto,sans-serif;max-width:860px;
margin:0 auto;padding:24px 16px;color:#1a1a1a;background:#fafafa}
header{border-bottom:3px solid #1a3a5c;margin-bottom:24px;padding-bottom:16px}
h1{color:#1a3a5c;margin:0 0 8px}
h2{color:#1a3a5c}
p.sub{color:#555;margin:0}
nav{margin:16px 0;padding:12px;background:#fff;border:1px solid #ddd;border-radius:8px}
nav a{margin-right:14px;color:#1a3a5c}
.ep{background:#fff;border:1px solid #ddd;border-radius:8px;padding:14px 16px;margin:0 0 14px}
.ep h3{margin:0 0 6px;font-size:1.05em}
.ep h3 a{color:#1a3a5c;text-decoration:none}
.ep .meta{color:#777;font-size:.85em;margin-bottom:6px}
.ep p{margin:6px 0 0;font-size:.92em;color:#333}
audio{width:100%;margin-top:8px}
.playbtn{display:inline-block;margin-top:10px;padding:9px 18px;background:#1a3a5c;color:#fff !important;border-radius:24px;text-decoration:none;font-weight:600;font-size:.95em}
.playbtn:hover{background:#2a5a8c}
footer{margin-top:32px;color:#888;font-size:.8em;border-top:1px solid #ddd;padding-top:12px}
"""


def slugify(name):
    return name.lower().replace(" ", "-")


def parse_feed():
    tree = ET.parse(FEED_FILE)
    channel = tree.getroot().find("channel")
    show_title = channel.findtext("title") or "Education Across the States"
    show_desc = (channel.findtext("description") or "").strip()
    items = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        desc = (item.findtext("description") or "").strip()
        guid_el = item.find("guid")
        guid = (guid_el.text or "").strip() if guid_el is not None else ""
        enc = item.find("enclosure")
        audio = enc.get("url", "") if enc is not None else ""
        dur = ""
        for child in item:
            if child.tag.endswith("}duration") or child.tag == "duration":
                dur = (child.text or "").strip()
        try:
            dt = parsedate_to_datetime(pub)
            datestr = dt.strftime("%B %d, %Y")
        except Exception:
            datestr = pub
            dt = None
        # Strip HTML tags from description for the listing blurb.
        blurb = re.sub(r"<[^>]+>", "", desc)
        blurb = html.unescape(blurb).strip()
        if len(blurb) > 400:
            blurb = blurb[:397] + "..."
        items.append({
            "title": title, "datestr": datestr, "blurb": blurb,
            "guid": guid, "audio": audio, "dur": dur,
            "ts": dt.timestamp() if dt is not None else 0,
        })
    return show_title, show_desc, items


def prefix_of(title):
    m = re.match(r"\[(.+?)\]", title)
    return m.group(1).strip() if m else ""


def episode_card(ep):
    t = html.escape(ep["title"])
    meta = html.escape(ep["datestr"])
    if ep["dur"]:
        meta += " &middot; " + html.escape(ep["dur"])
    blurb = html.escape(ep["blurb"])
    # Inline <audio> players can't follow the media host's redirect on iOS Safari,
    # so episode cards use a play button that opens the audio directly instead.
    player = (f'<a class="playbtn" href="{html.escape(ep["audio"])}" target="_blank" rel="noopener">'
              f'&#9654; Play episode</a>') if ep["audio"] else ""
    return (f'<div class="ep"><h3>{t}</h3>'
            f'<div class="meta">{meta}</div><p>{blurb}</p>{player}</div>')


def page(title, heading, sub, nav_links, body_html):
    nav = " ".join(f'<a href="{html.escape(href)}">{html.escape(label)}</a>'
                   for label, href in nav_links)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<header><h1>{html.escape(heading)}</h1><p class="sub">{html.escape(sub)}</p></header>
<nav>{nav}</nav>
{body_html}
<footer>Education Across the States &middot; episodes also available in the
<a href="feed.xml">RSS feed</a></footer>
</body>
</html>
"""


def main():
    show_title, show_desc, items = parse_feed()
    # Newest first (the upstream feed is oldest-first).
    items.sort(key=lambda e: e["ts"], reverse=True)
    groups = {s: [] for s in STATES}
    region_groups = {r: [] for r in REGIONS}
    other = []
    for ep in items:
        p = prefix_of(ep["title"])
        state = PREFIX_TO_STATE.get(p)
        if state:
            groups[state].append(ep)
        elif p.endswith("Special") and p[:-8].strip() in region_groups:
            region_groups[p[:-8].strip()].append(ep)
        elif p in region_groups:
            region_groups[p].append(ep)
        else:
            other.append(ep)

    state_pages = [(s, f"{slugify(s)}.html") for s in STATES]
    region_pages = [(r, f"region-{slugify(r)}.html") for r in REGIONS]
    nav_links = [("All episodes", "index.html")]
    nav_links += [(s, href) for s, href in state_pages]
    nav_links += [(f"{r} Special", href) for r, href in region_pages]

    # Per-state pages
    for state, href in state_pages:
        eps = groups[state]
        body = (f"<h2>{len(eps)} episode{'s' if len(eps) != 1 else ''}</h2>\n"
                + "\n".join(episode_card(ep) for ep in eps)
                if eps else "<p>No episodes yet.</p>")
        with open(os.path.join(HERE, href), "w", encoding="utf-8") as f:
            f.write(page(f"{state} Education \u2014 Education Across the States",
                         f"{state}", "Every episode for this state, newest first.",
                         nav_links, body))
        print(f"wrote {href} ({len(eps)} episodes)")

    # Per-region pages
    for region, href in region_pages:
        eps = region_groups[region]
        body = (f"<h2>{len(eps)} special episode{'s' if len(eps) != 1 else ''}</h2>\n"
                + "\n".join(episode_card(ep) for ep in eps)
                if eps else "<p>No specials yet.</p>")
        with open(os.path.join(HERE, href), "w", encoding="utf-8") as f:
            f.write(page(f"{region} Special \u2014 Education Across the States",
                         f"{region} Special",
                         "Multi-state special episodes for this region, newest first.",
                         nav_links, body))
        print(f"wrote {href} ({len(eps)} episodes)")

    # Homepage: latest 20 across everything
    latest = items[:20]
    body = "<h2>Latest episodes</h2>\n" + "\n".join(episode_card(ep) for ep in latest)
    if other:
        body += "<h2>More from the network</h2>\n" + "\n".join(episode_card(ep) for ep in other)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(show_title, show_title,
                     show_desc or "Daily education coverage across the states.",
                     nav_links, body))
    print(f"wrote index.html ({len(items)} total episodes)")


if __name__ == "__main__":
    main()

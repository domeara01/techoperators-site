# Tech Operators redesign — handoff for the Netlify build

Prepared 30 Sept 2026. This folder holds the approved lighter redesign ("Direction A · Quiet Confidence") of the **home page** and the **member directory**, ready to be built into the `techoperators-members` Netlify site by `deploy.sh`.

Nothing in `dist/`, `website/`, `snapshot/` or `deploy.sh` has been changed yet. That work is below.

## What's in this folder

| Path | What it is |
|---|---|
| `src/home.tpl.html` | Home page template (source of truth) |
| `src/members.tpl.html` | Member directory template (source of truth) |
| `build_redesign.py` | Fills the templates and writes the pages (no dependencies, Python 3) |
| `img/` | Logo (dark), mark, Meitheal photos, 4 board photos |
| `img/m/<member-id>.jpg` | 35 member headshots, 600×600, named by directory member id |
| `index.html`, `members.html` | Preview build with relative links; open locally in a browser |

Rebuild the preview after editing a template: `python3 build_redesign.py preview`

## Build into the site

```
python3 redesign/build_redesign.py prod dist
```

This writes:

- `dist/index.html` (new home page)
- `dist/members/index.html` (new directory)
- `dist/img/…` (all images, referenced as `/img/...`)

Links in prod mode:

- Home → directory: `/members/`
- Board tiles: `/members/#<member-id>`, which opens that profile
- Directory → home: `/`

The member data comes from `dist/members/snapshot.js` by default. Pass `SNAPSHOT=...` to use another path. So run it **after** `deploy.sh` has written the fresh snapshot.

### Changes needed in `deploy.sh`

1. Keep steps 1–2 as they are, including `patch-directory.mjs` and `patch-board.mjs`. `patch-directory.mjs` writes `dist/members/snapshot.js`, which the new build needs. `patch-board.mjs` still patches `dist/edit.html`. The old directory page they patch is simply overwritten in step 3.
2. **Remove** the `snapshot-home.mjs` step. It copies the old Squarespace home over `dist/index.html`.
3. After `cp -R website/. dist/`, add: `python3 redesign/build_redesign.py prod dist`.
4. Leave `/edit` alone. The editor's "View profile" links go to `/members/#<id>`, and the new directory opens a profile from that hash, so sign-in links keep working.

## How the directory works

- **Data:** the member list is embedded in the page at build time, from the snapshot. The browser then fetches the live Google Apps Script API (`?action=directory`) and re-renders if anything changed.
- **Rules carried over from the live directory:**
  - scoring and "Recommended" sort
  - search, Skill / Industry / Stage filters, Open to mentoring, A–Z sort
  - "Members with similar profiles"
  - search matches showing the matching past role on the tile
  - Brandfetch company logos, with a monogram fallback
- **Photos:** each member's `photo` URL from the directory (Google Drive) is used first. `/img/m/<id>.jpg` is the fallback, then initials.
- **Headshot cluster (top of directory):** built from the live member list. Joiners with a photo appear automatically, and leavers are swapped out when the live data loads.
- **Profiles:** open in a slide-in drawer (a bottom sheet on phones). The URL hash is the member id.
- **Empty fields:** empty "Interested in" sections are hidden. The old page showed a "Not added yet" prompt.
- **Styles:** everything is inline in each HTML file, so no `site.css` is needed for these two pages. Font: Plus Jakarta Sans from Google Fonts.

## Motion (all switched off under prefers-reduced-motion)

**Home**

- Headline lines slide up.
- The hero photo reveals through its arched frame while the pill outline draws; a small green dot then circles the outline slowly.
- A soft green glow sits behind the hero photo.
- The company-name banner scrolls continuously and pauses on hover.
- The header condenses into a floating bar on scroll.
- Sections fade up on scroll.
- Buttons lift on hover, and photos go from greyscale to colour.
- The closing panel has the same glow.

**Directory**

- The same header.
- The "done it before." highlight draws in, and the glow in the intro panel drifts.
- The headshot cluster swaps one face every 2.8 s.
- A "Browse all N members" cue scrolls to the filters. On desktop it also focuses search.
- Tiles fade in, one after another.

## Still to decide or do

- **Home links:** "Apply as a founder" and "Membership" currently jump to the closing section (`#join`). Point them at `/apply` and `/membership`. "For startups" should likely be `/startups`.
- **Other pages** (`startups`, `membership`, `apply`, policies, `404`, `thanks`) still use the old look from `website/assets/site.css`. They need the same treatment for a consistent site.
- **Board roles** on the home page are shortened from the bios in `build.py`. Confirm the wording.
- **Missing photos:** there are no photos for Edel Coen, Indu Sajeev or Tom Young. Add `img/m/edelcoen.jpg`, `indusajeev.jpg`, `tomyoungeida.jpg`.
- **Doug Orr:** `img/m/doorr.jpg` is a generic silhouette, not a headshot. Replace it, or exclude it from the headshot cluster.
- **Dark mode:** not built. The brief asks for dark and light versions.
- **Staging:** the home page footer has no "preview" or staging banner in prod mode. Keep the `noindex` header in `_headers` until cutover.
- **Page metadata:** `<meta name="description">` and Open Graph tags are not in the new pages yet. Copy them from `build.py`'s `page()`.

## Review links

- Home page: https://claude.ai/artifact/GGEY5hechoo9QuUsnSi8Gr (private; the online copy shows only a few member photos)
- Directory: https://claude.ai/artifact/4XWqHKDK6UJyx2ZKa9QTZs (private)
- Design canvas with the three directions and motion options: https://claude.ai/code/artifact/34b2a4c5-3baa-429e-8b85-ba8c4cf8fe6c

## Update, 2 Oct 2026: form pages added

The founder application, membership application and thank-you pages are now in the same design.

- **New sources:** `src/apply.body.html`, `src/membership.body.html`, `src/thanks.body.html`. They share `src/_shell.css`, `src/_header.html`, `src/_footer.html` and `src/_shell.js`.
- **Build output:** `prod` mode now also writes `apply.html`, `membership.html` and `thanks.html` to the output folder. These replace the same-named pages copied in from `website/`, so run the build **after** `cp -R website/. dist/`.
- **Forms are unchanged underneath.** Same form names (`founder-application`, `membership-application`), same field names, same Netlify attributes and honeypot, posting to `/thanks`. `netlify/functions/submission-created.mts` keeps working without changes.
- **Preview mode:** the forms show a confirmation and send nothing.
- **Links now resolved:** "Apply as a founder" goes to `/apply`, "Membership" and "Become a member" go to `/membership`, "For startups" goes to `/startups`, and footer links go to the policy pages. Remove those from the "Still to decide or do" list above.
- **Page descriptions** are now written into every page built in `prod` and `preview` mode. Open Graph tags are still missing.
- **Founder form overhaul is still to come.** The board's requirements are due Monday 5 Oct. Edit `src/apply.body.html`, and add any new field names to the `LABELS` list in `submission-created.mts` so they appear in the Attio note.
- **Membership submit button is dark green, not orange,** to keep orange for founder actions.
- **Still on the old look:** `startups`, the three policy pages and `404`.

Review copies (private): founder form https://claude.ai/artifact/FuqyTr8fiJrXP58hJYHASm · membership form https://claude.ai/artifact/DxKzir1Fe3v5mUG49PZLf3

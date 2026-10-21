# Tech Operators website: house rules

Read this before any change in this repository. For an edit request, also follow the `update-website` skill.

## Who is asking and how to talk to them
- The people asking (mostly Fiona, the Tech Operators admin, and other board members) are not technical.
- Reply in plain English. No jargon, no file names or code unless they ask. Say "the Portfolio page", not "portfolio.body.html".
- Before changing anything, say back in one or two sentences exactly what will change, on which page, and wait for a yes.
- If the request is unclear, ask. Don't guess at wording, names, links or logos.
- Anything this file says to "check with Dave" means stop and tell the person that Dave needs to confirm it.

## Workflow (every change)
1. Start from an up-to-date `main` and create a new branch, e.g. `edit/portfolio-add-acme`. Never commit to `main` directly.
2. Edit only the source files listed in the page map below.
3. Build locally to check: `OUT=/tmp/to-check ./deploy-redesign.sh`
   - The script only builds; it never deploys. Netlify runs the same script on every push (see `netlify.toml`) and publishes the result.
   - `OUT` is deleted and recreated, so always point it at a throwaway folder under `/tmp`, never at the repository or a real folder.
   - The script fetches the member directory from Google. With no network it prints "Could not fetch the live directory" and uses `redesign/snapshot.last.js`. That is fine.
   - A successful build ends with "Built into /tmp/to-check." Any "looks wrong, stopping" message means a page lost a phrase the script checks for (see Hard rules).
   - The build rewrites `redesign/snapshot.last.js` when it gets live data. Don't commit that file as part of a website edit: `git checkout -- redesign/snapshot.last.js` before committing.
   - Don't run `python3 redesign/build_redesign.py preview`; it writes stray HTML files into `redesign/`.
4. Commit with a short plain message, push the branch. Netlify builds a deploy preview for the branch (or its pull request). Give the person the preview link and tell them which page to look at.
   - Netlify builds every push by running `deploy-redesign.sh` and publishing the `dist/` folder it creates (`dist/` is not in the repo). If a preview fails to build, comes up blank or shows "Page not found", stop and tell Dave rather than changing `netlify.toml` or the script.
5. Publish (merge to `main`) only after the person explicitly says to publish. Every merge to `main` is a production deploy, and each production deploy uses Netlify credits. Where sensible, collect several small changes on one branch and publish them together. Mention this if someone asks for a series of tiny changes.
6. After publishing, tell them it is live and delete the branch.

## Page map (live URL -> file to edit)
All page sources are in `redesign/src/`. The build fills `{{HOME}}`, `{{DIR}}`, `{{APPLY}}`, `{{MEMBERSHIP}}`, `{{STARTUPS}}`, `{{PORTFOLIO}}`, `{{PRINCIPLES}}`, `{{POLICY}}`, `{{PRIVACY}}`, `{{THANKS}}`, `{{EXT}}`, `{{NOTE}}` with the right links. Always use these placeholders for internal links; never type `/apply` etc. by hand. An unknown `{{NAME}}` stops the build.

| URL | Edit |
|---|---|
| `/` home | `home.tpl.html` (copy, styles and script all in one file; has its own header and footer) |
| `/startups` | `startups.body.html`, styles in `startups.css` |
| `/portfolio` | `portfolio.body.html`, styles in `portfolio.css`, logos in `redesign/img/portfolio/` |
| `/apply` founder form | `apply.body.html` (form rules below) |
| `/membership` membership form | `membership.body.html` (includes the "Next cohort intake" notice) |
| `/thanks` | `thanks.body.html` |
| `/members/` directory | `members.tpl.html`. Layout only. Member profiles are not in this repo (see Hard rules) |
| `/operating-policy` | `policy.body.html` (styles `legal.css` + `policy.css`) |
| `/privacy-policy` | `privacy.body.html` (styles `legal.css` + `privacy.css`) |
| "Page not found" (404) | `notfound.body.html` (styles `legal.css` + `notfound.css`) |
| `/edit` member editor | `editor/edit.html`. Do not touch |

Page titles and search descriptions for the redesigned pages are in the `PAGES` list at the top of `redesign/build_redesign.py`.
Do not edit the old copies in `website/` (`index.html`, `startups.html`, `apply.html`, `membership.html`, `thanks.html`, and the policy and 404 pages): the build overwrites them with the redesigned pages. Files in `website/` that are used as they are: `_redirects`, `_headers`, `robots.txt`, `llms.txt` (a summary for AI tools; update its links if a page is added, renamed or removed).
Check with Dave if a build ever shows the old green-and-white Squarespace-style look on a policy or 404 page; the redesigned versions of those were being added on 8 Oct 2026.

Where common content lives:
- **The Meitheal**: there is no separate Meitheal page any more (retired 9 Oct 2026). It lives in the Meitheal section of For startups (`startups.body.html`, banner `id="meitheal"` plus the explainer and four principles below it). `{{PRINCIPLES}}` links there, and `/meitheal` and `/meitheal-principles` redirect there.
- **Main navigation and footer links**: in three places. `_header.html` and `_footer.html` (every page except home and the member directory), the `<header>` and `<footer>` inside `home.tpl.html`, and the `<header>` (its footer also has Home) inside `members.tpl.html`. A nav change means editing all three headers.
- **Home page company ticker** ("Members have built and scaled at"): `home.tpl.html`, the `marquee__set` line. The list appears twice (the second copy, `aria-hidden`, makes the loop seamless); keep both identical. The same company names are repeated in the "Why Tech Operators?" paragraph.
- **Board tiles and roles**: `home.tpl.html`, "Meet the board" section. Each tile links to `{{DIR}}#<member-id>` (the member's id in the directory), with a photo in `redesign/img/` (`m-1.jpg`, `m-jc.jpg`, `m-fionnuala.jpg`, `m-niall.jpg`, 600x600). Roles are short: "Function. Previously X".
- **Portfolio company cards**: `portfolio.body.html`. The home page "Investment" card also names some portfolio companies.
- **Founder quotes**: the three full-width quote cards on Portfolio (Cytidel/Matt Conlon, Needi/Louise Doyle, Roamr/Stephen Dooley). The Needi and Cytidel quotes are repeated in "What founders say" on `/startups`, and that page also has two "Previous participants" quotes. If a quote changes, ask whether it should change in both places.

## Brand and style
- Colours (from `:root` in `home.tpl.html`): ground `#FBFCFA`, mist `#EFF6FA`, white, ink (dark green) `#112E23`, body text `#3B4F4A`, muted `#56686A`, accent green `#81E76D`, CTA orange `#FF8732`. Use the CSS variables (`var(--ink)` etc.), not new colours.
- Orange (`.btn`) is only for founder actions ("Apply as a founder", "Apply to pitch", "Apply now"). Anything for members or operators uses the dark green `btn--ink` or ghost button, or a text `.link`. Accent green is only for small signals (dots, highlight, glow).
- Font: Plus Jakarta Sans (weights 400 to 700), loaded from Google Fonts. Don't add fonts.
- Tone of voice: plain, specific and warm; short sentences; sentence case for headings and buttons; British/Irish spelling ("programme", "per cent"); concrete facts ("No fees, no strings attached", "Members invest their own money") rather than hype. No exclamation marks, no buzzwords, no superlatives the members wouldn't say themselves. Section headings often end with a full stop ("Meet the board.").
- Big headlines are split into lines, each wrapped as `<span class="mask"><span>line</span></span>`, so they slide up one line at a time. Keep lines short and similar in length, at most four lines.
- `<span class="hl-mark">words</span>` draws the green highlighter under the last words of a headline. Use it once per page, on two or three words. It only works on pages whose CSS defines it (startups, portfolio, apply, membership, thanks, members, and the policy and 404 pages via `legal.css`; and home).
- Glows (`<span class="glow glow--g">`/`glow--m`, `aria-hidden`) are decorative; reuse the existing ones, don't add more.
- Scroll fade-in: add class `rv` to new blocks, like their neighbours.
- The `<style>` and `<script>` in `home.tpl.html` are also used by For startups, Portfolio, the policy pages and 404. A style change in `home.tpl.html` changes all of them; put page-only styles in that page's `.css` file.

## Hard rules (never)
- Never change form names (`founder-application`, `membership-application`), field `name=` values, the hidden `form-name` input, the honeypot `company_fax`, or `data-netlify`/`action` without also updating `netlify/functions/submission-created.mts` (which sends applications to Attio). A new field also needs a label in its `LABELS` list. If a form change is asked for, check with Dave.
- Never put API keys, tokens or passwords in the repo. Secrets belong in Netlify environment variables (e.g. `ATTIO_API_KEY`).
- Never edit member profiles or member data here. The directory comes from a Google Sheet through a Google Apps Script; members update their own profiles via `/edit`. Don't edit `redesign/snapshot.last.js` by hand, and don't change the Apps Script address in `members.tpl.html` (the snapshot script reads it from there).
- Don't remove the `noindex` block in `website/_headers` or the `Disallow` in `website/robots.txt` until told the site is live (cutover).
- Don't touch `editor/edit.html`, `deploy-redesign.sh`, `netlify.toml`, `snapshot/` or `netlify/functions/` unless Dave asks.
- Don't delete pages or entries in `website/_redirects` without asking; the redirects keep old Squarespace links working.
- Don't remove phrases the build checks for: "Why Tech Operators" (home), "Three ways we help" (startups), "have invested in" (portfolio), `id="meitheal"` (the Meitheal section on startups), "Find an operator" (members). If a wording change needs to, check with Dave.
- In `home.tpl.html`, the build swaps `href="#how">For startups` and `Members ↗` for live links. Don't reword those two nav items there without checking with Dave.
- Keep accessibility: every meaningful image has alt text (decorative ones `alt=""`), one `<h1>` per page, headings in order (h1, h2, h3), links say where they go, and new motion must sit inside the existing `prefers-reduced-motion` rules.

## Adding a portfolio company
1. Get from the person: company name, one-line description, founder name and title, website, logo, and whether there is a quote. Ask for anything missing.
2. Logo: save it in `redesign/img/portfolio/` as a lowercase file named after the company (`acme.svg` or `acme.png`). SVG preferred; a PNG with a transparent background otherwise. Never hotlink a logo from another site. Cards are white tiles, so a white-only logo must be recoloured dark (ink `#112E23` or the brand's dark colour) before use. If only a small icon exists, use the "mark + word" pattern (see EarthVisio, Gemell); with no logo, use the word only (see Examfly).
3. Copy an existing `<li class="co rv">` card and change the logo `src` and `alt`, the `co__desc` line, founder, link text and `aria-label`. Add `class="is-tall"` on the image if a squarish logo looks too small. Keep `loading="lazy"`, `target="_blank" rel="noopener"`, and `&amp;` for "&".
4. Order: on desktop the grid fits three normal cards per row; `co--half` cards take half a row; quote cards (`co co--quote rv`) take a full row. Quote cards sit at the top, in the middle and at the end. Rows between quotes must be full: six normal cards per block, and the last block ends with the two `co--half` cards. When adding one company, rebalance (e.g. turn halves into normal cards) and check with the person or Dave if it can't fill rows evenly.
5. Ask whether the company should also be named in the home page "Investment" card.
6. Build, push, and check the Portfolio page on the preview at desktop and phone widths.

## If something goes wrong
- If the build fails, read the message, undo your last change, and tell the person in plain English. Don't work around a check.
- If a request touches forms, member data, redirects, search-engine settings or deployment, or isn't covered here, check with Dave.

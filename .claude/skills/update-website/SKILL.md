---
name: update-website
description: Use when someone asks to change anything on the Tech Operators website, such as changing wording, adding or removing a portfolio company, changing a board member or their role, swapping a founder quote, updating a link, or editing a page, so the edit is confirmed, previewed and only published on their say-so.
---

# Update the Tech Operators website

The person asking is not technical. Talk in plain English, never show code unless they ask, and follow the house rules in `CLAUDE.md` at the repository root (read it first if it is not already in context). Work through these steps in order.

## 1. Understand the ask
- Work out which page(s) and which exact words, images or links are involved. Use the page map in `CLAUDE.md` to find the source file. Open it and find the current text.
- Check whether the same content appears elsewhere (nav and footer are in three places; founder quotes are on Portfolio and For startups; portfolio names also appear in the home page "Investment" card and the company ticker repeats in "Why Tech Operators?").
- Stop and check with Dave (tell the person you will need Dave) if the request involves: form fields or form names, member profiles or the member directory data, redirects, search-engine settings (`_headers`, `robots.txt`), the member editor (`/edit`), deployment settings, or anything that needs a secret or API key.

## 2. Confirm before changing
Reply with a short summary and wait for a clear yes. Include:
- **Where**: the page and section, in their words ("the Portfolio page, after the Kota card").
- **What changes**: the current text and the new text, quoted, for every place it appears.
- **Questions** for anything missing. Typical ones:
  - New portfolio company: name, one-line description, founder name and title, website, logo file (ideally SVG or PNG with a transparent background), any quote, where in the list, and should it also appear in the home page "Investment" card?
  - Board change: name, short role in the form "Function. Previously X", a square photo (at least 600x600), and their member id in the directory so the tile links to their profile.
  - Quote swap: exact wording, person's name and title, company, and whether it should change on both Portfolio and For startups.
  - Wording: if their text breaks the house style (title case, exclamation marks, hype), suggest a plain sentence-case version and let them choose.
- If they ask for several small changes over time, suggest collecting them on one preview and publishing once, because every publish uses Netlify credits.

## 3. Make the change on a branch
```
git checkout main && git pull
git checkout -b edit/<short-description>
```
- Never commit to `main`.
- Edit only the source files in `redesign/src/` (and images in `redesign/img/`). Copy the structure of neighbouring markup: same classes, `rv` on new blocks, `{{PLACEHOLDER}}` links for internal pages, `&amp;` for "&", curly quotes in quotes.
- Images: save locally in `redesign/img/` (portfolio logos in `redesign/img/portfolio/`), lowercase file names, always with alt text. Never hotlink. Recolour white-only logos dark.
- Headlines: keep the `mask` line spans and the `hl-mark` highlight; keep lines short.

## 4. Build and check
```
OUT=/tmp/to-check ./deploy-redesign.sh
```
- The script only builds; it never deploys. Never set `OUT` to anything but a throwaway `/tmp` folder (it is wiped).
- "Could not fetch the live directory ... Using the last good copy" is fine.
- Success ends with "Built into /tmp/to-check."
- If it stops ("looks wrong, stopping" or "Unfilled placeholders"), fix your own change or undo it. Don't edit the script's checks. If you can't fix it, tell the person plainly and check with Dave.
- Look at the built page in `/tmp/to-check` (e.g. `grep` for the new text) to confirm the change landed and nothing nearby was lost.
- Throw away build side effects: `git checkout -- redesign/snapshot.last.js` and make sure `git status` only shows the files you meant to change.

## 5. Push for a preview
```
git add <changed files>
git commit -m "<plain description of the change>"
git push -u origin edit/<short-description>
```
- Open a pull request into `main` if the person or Dave prefers pull requests (check with Dave which is set up). Netlify posts a deploy preview link on the pull request, or the branch preview is at `https://<branch-name>--<netlify-site-name>.netlify.app` (check with Dave for the site name).
- Wait for the Netlify preview to finish and open it. If it is blank or shows "Page not found", stop and tell Dave; don't change `netlify.toml`.

## 6. Hand over the preview
Send a short message using this template:

> Done, here's a preview: <preview link>
>
> What changed:
> - <page>: <old> → <new>
> - <page>: <what was added or removed>
>
> Have a look on your phone and computer. Nothing is live yet. Say "publish" when you're happy, or tell me what to tweak.

If they ask for tweaks, repeat steps 3 to 6 on the same branch.

## 7. Publish only when told
- Merge to `main` only after the person explicitly says to publish (e.g. "publish", "go live", "yes, put it live"). "Looks good" alone is not enough; ask "Shall I publish it now?"
- Merge the branch (or pull request) into `main` and push. That starts the production deploy.
- Confirm when it is live, with the page link on the live site, then delete the branch.
- If something looks wrong after publishing, tell the person straight away and offer to undo it by reverting the change on a new branch, with the same preview and publish steps.

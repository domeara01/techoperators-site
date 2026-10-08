#!/bin/bash
# Builds the Tech Operators site into dist/. Netlify runs this on every push (see netlify.toml);
# you can also run it locally to check a change before pushing.
#   /                home page                   /members/     member directory
#   /apply           founder application         /membership   membership application
#   /edit            member editor (from editor/edit.html, unchanged)
#   /startups, /portfolio, /meitheal-principles, /operating-policy, /privacy-policy, 404
#                    redesigned pages built from redesign/src/
#   website/         redirects, headers, robots.txt and anything not yet redesigned
#
#   ./deploy-redesign.sh              build into dist/
#   OUT=/some/folder ./deploy-redesign.sh   build somewhere else
# Deploying is done by Netlify from GitHub; this script never deploys.
set -euo pipefail
cd "$(dirname "$0")"
OUT="${OUT:-dist}"
LIVE="https://techoperators-members.netlify.app"

echo "1/3 Starting from a clean $OUT"
rm -rf "$OUT" && mkdir -p "$OUT/members"
cp -R website/. "$OUT/"
cp editor/edit.html "$OUT/edit.html"
cp editor/mark.png "$OUT/mark.png"
grep -q "DIRECTORY_URL = '/members/'" "$OUT/edit.html" || { echo "editor/edit.html doesn't point at /members/, stopping."; exit 1; }

echo "2/3 Fetching the member directory data"
node snapshot/snapshot-data.mjs "$OUT/members/snapshot.js" redesign/snapshot.last.js

echo "3/3 Building the redesigned pages"
SNAPSHOT="$OUT/members/snapshot.js" python3 redesign/build_redesign.py prod "$OUT"
grep -q "Find an operator" "$OUT/members/index.html"   || { echo "Directory page looks wrong, stopping."; exit 1; }
grep -q 'name="founder-application"' "$OUT/apply.html" || { echo "Founder form looks wrong, stopping."; exit 1; }
grep -q 'name="membership-application"' "$OUT/membership.html" || { echo "Membership form looks wrong, stopping."; exit 1; }
grep -q "Why Tech Operators" "$OUT/index.html"             || { echo "Home page looks wrong, stopping."; exit 1; }
grep -q "Our Meitheal principles" "$OUT/meitheal-principles.html" || { echo "Meitheal page looks wrong, stopping."; exit 1; }
grep -q "Three ways we help" "$OUT/startups.html"     || { echo "For startups page looks wrong, stopping."; exit 1; }
grep -q "have invested in" "$OUT/portfolio.html"       || { echo "Portfolio page looks wrong, stopping."; exit 1; }

echo "Built into $OUT."

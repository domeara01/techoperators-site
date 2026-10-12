#!/usr/bin/env python3
"""Builds the redesigned Tech Operators pages from the sources in ./src.

  python3 build_redesign.py preview          -> index, members, apply, membership, thanks (.html) in this folder.
                                                Open index.html locally. Forms show a confirmation but send nothing.
  python3 build_redesign.py prod <out_dir>   -> <out_dir>/index.html, members/index.html, apply.html, membership.html,
                                                thanks.html and img/ with site-root links (/, /members/, /apply ...).
                                                Forms post to Netlify Forms and land on /thanks.
  python3 build_redesign.py artifact <out_dir> <links.json>
                                             -> page fragments for online review copies (links from the JSON file).

Pages
  home, members      one template each: src/home.tpl.html, src/members.tpl.html
  apply, membership, thanks
                     src/_shell.css + src/_header.html + src/<page>.body.html + src/_footer.html + src/_shell.js
  startups, portfolio, policy, privacy, notfound (HOME_STYLED)
                     home page style + src/_pages.css (+ src/legal.css for policy, privacy, notfound) + src/<page>.css,
                     src/_header.html + src/<page>.body.html + src/_footer.html + home page script

Member data is embedded from the directory snapshot (window.__DIRECTORY_SNAPSHOT in snapshot.js).
Default: ../dist/members/snapshot.js. Override with SNAPSHOT=/path/to/snapshot.js.
Form field names and the form names (founder-application, membership-application) must stay in step with
netlify/functions/submission-created.mts, which sends each application to Attio.
"""
import json, os, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
SNAPSHOT = Path(os.environ.get("SNAPSHOT", HERE.parent / "dist" / "members" / "snapshot.js"))
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap">\n')

PAGES = {  # page -> (site title, review-copy title, description)
    "home": ("Tech Operators | Advice, connections and investment for Irish startups", "Tech Operators",
             "Tech Operators is a network of experienced technology executives and founders who help early-stage founders scale internationally, through expert advice, warm introductions and angel investment."),
    "members": ("Members | Tech Operators", "Tech Operators Members",
                "Find an operator who has done it before. The Tech Operators member directory: experienced executives and founders who advise, connect and invest in Irish startups."),
    "apply": ("Apply as a founder | Tech Operators", "Tech Operators Founder Application",
              "Founders: apply to tap into the Tech Operators network for advice, connections and investment."),
    "membership": ("Join Tech Operators | Membership", "Tech Operators Membership",
                   "Apply to join Tech Operators, a group of Ireland-based senior technology leaders who advise and invest in Irish startups."),
    "thanks": ("Thank you | Tech Operators", "Tech Operators Thanks", "Your application has been received."),
    "startups": ("For startups | Tech Operators", "Tech Operators For startups",
                 "How Tech Operators' network of experienced advisors, investors and industry leaders can support your startup's growth. No fees, no strings attached."),
    "portfolio": ("Portfolio | Tech Operators", "Tech Operators Portfolio",
                  "Some of the startups and founders that Tech Operators members have invested in."),
    "policy": ("Operating policy | Tech Operators", "Tech Operators Operating policy",
               "The Tech Operators operating policy: our guiding principles, the outcomes we want and the code of conduct between members."),
    "privacy": ("Privacy policy | Tech Operators", "Tech Operators Privacy policy",
                "What personal information Tech Operators collects through techoperators.ie and how we use it."),
    "notfound": ("Page not found | Tech Operators", "Tech Operators Page not found",
                 "This page isn't here. It may have moved when the Tech Operators site was rebuilt."),
}
# Pages built on the home page's full style and script (they reuse its section designs) with the shared header and footer
HOME_STYLED = ("startups", "portfolio", "policy", "privacy", "notfound")
# Of those, the text-led legal and utility pages also share src/legal.css (hero glow, contents rail, readable column)
LEGAL = ("policy", "privacy", "notfound")
FILES = {"home": "index.html", "members": "members/index.html", "apply": "apply.html", "membership": "membership.html",
         "thanks": "thanks.html", "startups": "startups.html",
         "portfolio": "portfolio.html", "policy": "operating-policy.html", "privacy": "privacy-policy.html",
         "notfound": "404.html"}
NOTE = '<span>Design preview · some links are placeholders</span>'
LINKS = {
    "preview": dict(HOME="index.html", DIR="members.html", APPLY="apply.html", MEMBERSHIP="membership.html",
                    STARTUPS="startups.html", PORTFOLIO="portfolio.html", POLICY="#top", PRINCIPLES="startups.html#meitheal", PRIVACY="#top", THANKS="thanks.html",
                    EXT="", NOTE=NOTE, PREVIEW="true"),
    "prod": dict(HOME="/", DIR="/members/", APPLY="/apply", MEMBERSHIP="/membership", STARTUPS="/startups", PORTFOLIO="/portfolio",
                 POLICY="/operating-policy", PRINCIPLES="/startups#meitheal", PRIVACY="/privacy-policy",
                 THANKS="/thanks", EXT="", NOTE="", PREVIEW="false"),
}


def data_json():
    s = SNAPSHOT.read_text(encoding="utf-8")
    m = re.search(r"=\s*(\{.*\})\s*;?\s*$", s, re.S)
    if not m:
        sys.exit(f"Could not read the directory snapshot at {SNAPSHOT}")
    d = json.loads(m.group(1))["data"]
    if not d.get("members"):
        sys.exit("The snapshot has no members; stopping.")
    return json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def read(name):
    return (SRC / name).read_text(encoding="utf-8")


def fill(text, kv, label):
    for k, v in kv.items():
        text = text.replace("{{" + k + "}}", v)
    left = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", text)))
    if left:
        sys.exit(f"Unfilled placeholders in {label}: {left}")
    return text


def render(page, links, title_index):
    """Returns the page as a fragment that starts with <title>, <link> and <style>."""
    kv = dict(links, PAGE=page)
    title = PAGES[page][title_index]
    if page == "home":
        body = read("home.tpl.html")
    elif page == "members":
        body = read("members.tpl.html")
        kv["DATA"] = data_json()
    elif page in HOME_STYLED:
        home = read("home.tpl.html")
        style = home[home.index("<style>") + len("<style>"):home.index("</style>")]
        script = home[home.rindex("<script>") + len("<script>"):home.rindex("</script>")]
        mark = ("document.querySelectorAll('[data-nav=\"" + page + "\"]')"
                ".forEach(function (a) { a.setAttribute('aria-current', 'page'); });")
        legal = read("legal.css") + "\n" if page in LEGAL else ""
        body = (f"<title>{title}</title>\n{FONT}<style>\n{style}\n{read('_pages.css')}\n{legal}{read(page + '.css')}</style>\n\n"
                f"{read('_header.html')}\n{read(page + '.body.html')}\n{read('_footer.html')}\n"
                f"<script>\n{script}\n{mark}\n</script>\n")
    else:
        body = (f"<title>{title}</title>\n{FONT}<style>\n{read('_shell.css')}</style>\n\n"
                f"{read('_header.html')}\n{read(page + '.body.html')}\n{read('_footer.html')}\n"
                f"<script>\n{read('_shell.js')}</script>\n")
    body = re.sub(r"<title>.*?</title>", lambda m: f"<title>{title}</title>", body, count=1, flags=re.S)
    return fill(body, kv, page)


def document(fragment, page, icon):
    """Wraps a fragment in a full HTML document, moving <title>/<link>/<style> into <head>."""
    i = fragment.index("</style>") + len("</style>")
    desc = PAGES[page][2].replace('"', "&quot;")
    head = ('<!doctype html>\n<html lang="en-IE">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<meta name="description" content="{desc}">\n<link rel="icon" href="{icon}">\n'
            '<meta property="og:type" content="website">\n<meta property="og:site_name" content="Tech Operators">\n'
            f'<meta property="og:title" content="{PAGES[page][0]}">\n<meta property="og:description" content="{desc}">\n'
            '<meta property="og:image" content="https://www.techoperators.ie/img/meitheal-table.jpg">\n'
            '<meta name="twitter:card" content="summary_large_image">\n')
    return head + fragment[:i] + "\n</head>\n<body>\n" + fragment[i:] + "\n</body>\n</html>\n"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        names = dict(FILES, members="members.html")
        for page, name in names.items():
            (HERE / name).write_text(document(render(page, LINKS["preview"], 0), page, "img/mark.png"), encoding="utf-8")
        print("Wrote " + ", ".join(names.values()) + f" in {HERE}")
    elif mode == "prod":
        out = Path(sys.argv[2]) if len(sys.argv) > 2 else sys.exit("Usage: build_redesign.py prod <out_dir>")
        names = FILES
        (out / "members").mkdir(parents=True, exist_ok=True)
        for page, name in names.items():
            t = render(page, LINKS["prod"], 0)
            t = t.replace('src="img/', 'src="/img/').replace("'img/m/'", "'/img/m/'")
            if page == "home":
                t = t.replace('href="#how">For startups', 'href="/startups">For startups')
                t = t.replace("Members ↗", "Members").replace('<span class="ar" aria-hidden="true">↗</span>', '<span class="ar" aria-hidden="true">→</span>')
            (out / name).write_text(document(t, page, "/mark.png"), encoding="utf-8")
        shutil.copytree(HERE / "img", out / "img", dirs_exist_ok=True)
        print("Wrote " + ", ".join(names.values()) + f" and img/ in {out}")
    elif mode == "artifact":
        if len(sys.argv) < 4:
            sys.exit("Usage: build_redesign.py artifact <out_dir> <links.json>")
        out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
        urls = json.loads(Path(sys.argv[3]).read_text())
        links = dict(HOME=urls["home"], DIR=urls["members"], APPLY=urls["apply"], MEMBERSHIP=urls["membership"],
                     STARTUPS=urls["home"] + "#how", PORTFOLIO="#top", POLICY="#top", PRINCIPLES="#top", PRIVACY="#top", THANKS="#top",
                     EXT=' target="_blank" rel="noopener"', NOTE=NOTE, PREVIEW="true")
        for page in ("home", "members", "apply", "membership"):
            (out / f"{page}.html").write_text(render(page, links, 1), encoding="utf-8")
        print(f"Wrote review fragments in {out}")
    else:
        sys.exit("Mode must be 'preview', 'prod' or 'artifact'")


if __name__ == "__main__":
    main()

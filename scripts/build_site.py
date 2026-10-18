#!/usr/bin/env python3
"""Build the static site in _site/: the diagram index, every diagram, and each scene's README and SKILL rendered to HTML."""
import html, pathlib, re, shutil, sys

from markdown_it import MarkdownIt

MD = MarkdownIt("commonmark").enable("table")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
LOCAL_MD = re.compile(r'href="(?!https?://)([^"#]*?)\.md(#[^"]*)?"')

CSS = """:root{--bg:#fffff8;--ink:#1c1b19;--ink2:#4b4a45;--ink3:#8a8880;--rule:#d9d7cc;--wash:#efede1;--accent:#b0261c}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--ink:#ebe9e1;--ink2:#c4c2b9;--ink3:#8f8d85;--rule:#3d3c38;--wash:#252420;--accent:#f2735f}}
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;padding:28px 16px 48px;color:var(--ink);background:var(--bg);font:500 16px/1.7 -apple-system,BlinkMacSystemFont,"Pretendard","Apple SD Gothic Neo","Noto Sans KR","Noto Sans CJK KR","Segoe UI",Roboto,sans-serif}
main{max-width:980px;margin:0 auto}
article{max-width:760px}
.fig{margin:18px 0 8px;overflow-x:auto}
.fig a{display:block;font-size:12px;color:var(--ink3);margin-top:4px;text-decoration:none}
nav{font-size:13px;color:var(--ink3);padding-bottom:10px;border-bottom:1px solid var(--rule);margin-bottom:8px}
nav a{color:var(--ink2);text-decoration:none;margin-right:14px}
a{color:var(--ink);text-decoration-color:var(--rule);text-underline-offset:3px}
a:hover{color:var(--accent)}
h1{font-size:24px;font-weight:650;margin:18px 0 10px}
h2{font-size:18px;font-weight:650;margin:34px 0 8px}
p,li{color:var(--ink)}
code{font:500 0.88em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--wash);padding:1px 4px;border-radius:3px}
pre{background:var(--wash);padding:12px 14px;overflow-x:auto;border-radius:4px;line-height:1.5}
pre code{background:none;padding:0;overflow-wrap:normal}
p code,li code,td code{overflow-wrap:anywhere}
table{border-collapse:collapse;width:100%;font-size:15px;margin:10px 0;display:block;overflow-x:auto}
th,td{text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-weight:650;color:var(--ink2);border-bottom:1px solid var(--ink3)}
blockquote{margin:8px 0;padding-left:14px;border-left:1px solid var(--rule);color:var(--ink2)}
.meta{color:var(--ink3);font-size:14px}
footer{margin-top:40px;font-size:12px;color:var(--ink3)}"""


def md_links_to_html(text):
    return LOCAL_MD.sub(lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', text)


def page(title, body, nav):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
{CSS}
</style>
</head>
<body>
<main>
<nav>{nav}</nav>
{body}
<footer>herdr tour, herdr 0.9.5</footer>
</main>
</body>
</html>
"""


SKIP = (":root", "html", "body", "main", "header", "h1", "nav", "footer", "*", ".embed", ".fig", "@media")


def figure(scene):
    """Inline the scene's diagram SVG and its drawing styles so the concept page leads with the picture."""
    text = (scene / "diagram.html").read_text(encoding="utf-8")
    style = re.search(r"<style>\n(.*?)\n</style>", text, re.S).group(1).splitlines()
    rules = "\n".join(line for line in style if not line.startswith(SKIP))
    svg = re.search(r"<svg.*?</svg>", text, re.S).group(0)
    title = re.search(r"<h1>(.*?)</h1>", text, re.S).group(1)
    return f'<style>\n{rules}\n</style>\n<h2>{title}</h2>\n<div class="fig">{svg}<a href="diagram.html">개념도만 크게 보기</a></div>'


def render(path, prefix):
    text = path.read_text(encoding="utf-8")
    meta = ""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if m:
        desc = re.search(r'^description: "?(.*?)"?$', m.group(1), re.M)
        meta = f'<p class="meta">{html.escape(desc.group(1))}</p>' if desc else ""
        text = f"# {path.parent.name}: SKILL\n\n{m.group(2)}"
    body = MD.render(text)
    body = body.replace("</h1>", "</h1>" + meta, 1)
    return md_links_to_html(body)


ROW = re.compile(r"^\| \[`([bmp][0-9]+-[a-z]+)`\]\([^)]*\) \| ([^|]+) \| ([^|]+) \|", re.M)
PART = re.compile(r"^## ((?:초급|중급|고급)[^\n]*)$", re.M)
INSTALL = "curl -fsSL https://herdr.dev/install.sh | sh"
CLAUDE_INSTALL = "claude plugin marketplace add IamGroooooot/herdr-tour && claude plugin install herdr-tour@herdr-tour"
CODEX_INSTALL = "codex plugin marketplace add IamGroooooot/herdr-tour && codex plugin add herdr-tour@herdr-tour"
CLAUDE_OPEN = 'claude --allowedTools "Bash(herdr *),Bash(git *),Bash(mkdir *)"'

START_CSS = """
.lede{color:var(--ink2);max-width:680px;margin:6px 0 0}
ol.setup{list-style:none;padding:0;margin:22px 0 0;counter-reset:s}
ol.setup li{display:grid;grid-template-columns:28px 1fr;gap:2px 10px;margin:0 0 14px}
ol.setup li::before{counter-increment:s;content:counter(s);color:var(--ink3);font-weight:650}
.cmd{display:flex;gap:8px;align-items:flex-start}
.cmd code{display:block;white-space:pre-wrap;word-break:break-all;padding:8px 10px;flex:1}
button.copy{font:500 12px inherit;color:var(--ink3);background:none;border:1px solid var(--rule);border-radius:3px;padding:6px 8px;cursor:pointer}
button.copy:hover{color:var(--accent);border-color:var(--accent)}
.via{font-size:13px;color:var(--ink3);margin:8px 0 2px}
.part{margin-top:30px}
.part h2{margin:0 0 4px}
.scene{display:grid;grid-template-columns:92px 1fr 150px;gap:4px 14px;align-items:baseline;padding:9px 0;border-bottom:1px solid var(--rule)}
.scene .id{font-weight:650;white-space:nowrap}
.scene .id a{text-decoration:none}
.scene .what{color:var(--ink)}
.scene .what code{font-size:13px}
.scene .when{font-size:13px;color:var(--ink3);white-space:nowrap}
.bar{display:inline-block;height:6px;background:var(--ink3);vertical-align:middle;margin-right:6px}
.bar.open{background:none;border-top:2px dotted var(--ink3);height:0}
.scene.first .bar{background:var(--accent)}
.scene.first .id a{color:var(--accent)}
.run{grid-column:2 / 4;font-size:13px;color:var(--ink3)}
.run code{cursor:pointer}
@media (max-width:620px){.scene{grid-template-columns:1fr}.scene .when,.run{grid-column:1}}"""

COPY_JS = """<script>
for (const el of document.querySelectorAll("[data-copy]")) {
  el.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(el.dataset.copy); const t = el.textContent; el.textContent = "복사됨"; setTimeout(() => el.textContent = t, 1200); } catch (e) {}
  });
}
</script>"""


def cmd(text):
    e = html.escape(text, quote=True)
    return f'<div class="cmd"><code>{e}</code><button class="copy" data-copy="{e}">복사</button></div>'


def start_page():
    """The site root: what to run, in what order, and how long each step takes."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    parts, first = [], True
    heads = list(PART.finditer(readme))
    for i, h in enumerate(heads):
        chunk = readme[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(readme)]
        rows = []
        for name, when, what in ROW.findall(chunk):
            when = when.strip()
            mins = re.match(r"([0-9]+)분", when)
            bar = f'<span class="bar" style="width:{int(mins.group(1)) * 14}px"></span>' if mins else '<span class="bar open" style="width:42px"></span>'
            what_html = re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", html.escape(what.strip()).replace("&#x27;", "'"))
            slash = f"/herdr-tour:{name}"
            rows.append(f"""<div class="scene{' first' if first else ''}">
<div class="id"><a href="skills/{name}/README.html">{name}</a></div>
<div class="what">{what_html}</div>
<div class="when">{bar}{html.escape(when)}</div>
<div class="run">agent에게 <code data-copy="{slash}" title="눌러서 복사">{slash}</code>, <a href="skills/{name}/README.html">개념과 개념도</a></div>
</div>""")
            first = False
        parts.append(f'<section class="part"><h2>{html.escape(h.group(1))}</h2>{"".join(rows)}</section>')
    body = f"""<h1>herdr를 몸으로 익히는 투어</h1>
<ol class="setup">
<li><div>herdr를 설치하고 <code>herdr</code>로 연다.</div><div style="grid-column:2">{cmd(INSTALL)}</div></li>
<li><div>투어를 진행할 agent에 투어 plugin을 설치한다. 쓰는 쪽 하나만 하면 된다.</div><div style="grid-column:2"><div class="via">Claude Code</div>{cmd(CLAUDE_INSTALL)}<div class="via">Codex</div>{cmd(CODEX_INSTALL)}</div></li>
<li><div>herdr pane 안에서 agent를 열고 첫 장면을 부른다: <code>/herdr-tour:b1-server</code>. Codex는 <code>/</code> 대신 <code>$</code>로 부른다.</div><div style="grid-column:2"><div class="via">Claude Code는 herdr, git, mkdir 명령을 미리 허용해 승인 창을 줄인다.</div>{cmd(CLAUDE_OPEN)}</div></li>
</ol>
{"".join(parts)}
<p class="lede" style="margin-top:26px">개념도만 모아 보기: <a href="diagrams.html">diagrams</a>. 전체 설명: <a href="README.html">README</a>. 준비물: herdr 0.9.5 이상, Claude Code, Codex CLI, git, jq, python3.</p>
{COPY_JS}"""
    nav = '<a href="index.html">시작</a><a href="diagrams.html">개념도</a><a href="README.html">README</a><a href="https://github.com/IamGroooooot/herdr-tour">GitHub</a>'
    return page("herdr tour", body, nav).replace("</style>", START_CSS + "\n</style>", 1)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / ".nojekyll").write_text("")
    gallery = md_links_to_html((ROOT / "index.html").read_text(encoding="utf-8"))
    gallery = gallery.replace('<nav><a href="README.html">', '<nav><a href="index.html">시작</a><a href="README.html">')
    (OUT / "diagrams.html").write_text(gallery, encoding="utf-8")
    (OUT / "index.html").write_text(start_page(), encoding="utf-8")
    home = '<a href="index.html">시작</a><a href="diagrams.html">개념도</a>'
    (OUT / "README.html").write_text(page("herdr tour", "<article>" + render(ROOT / "README.md", "") + "</article>", home), encoding="utf-8")
    for scene in sorted((ROOT / "skills").iterdir()):
        if not scene.is_dir():
            continue
        dst = OUT / "skills" / scene.name
        dst.mkdir(parents=True)
        diagram = (scene / "diagram.html").read_text(encoding="utf-8")
        diagram = diagram.replace('href="../../index.html">index', 'href="../../diagrams.html">index')
        (dst / "diagram.html").write_text(md_links_to_html(diagram), encoding="utf-8")
        nav = ('<a href="../../index.html">시작</a><a href="diagram.html">개념도</a>'
               '<a href="README.html">README</a><a href="SKILL.html">SKILL</a>')
        for name in ("README", "SKILL"):
            src = scene / f"{name}.md"
            body = render(src, "../../")
            if name == "README":
                body = re.sub(r"<p>개념도: <a href=\"diagram.html\">diagram.html</a></p>\n", "", body)
                head, sep, rest = body.partition("</h1>")
                body = head + sep + figure(scene) + "<article>" + rest + "</article>"
            else:
                body = "<article>" + body + "</article>"
            (dst / f"{name}.html").write_text(page(f"{scene.name} {name}", body, nav), encoding="utf-8")
        for extra in scene.iterdir():  # 원본 md와 live.py 같은 실습 파일도 그대로 싣는다
            if extra.is_file() and extra.name != "diagram.html":
                shutil.copy(extra, dst / extra.name)
    print(f"built {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

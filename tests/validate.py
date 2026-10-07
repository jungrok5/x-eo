#!/usr/bin/env python3
"""Repo layout checks: 4 skills, frontmatter name == dir, no stray SKILL.md, relative links resolve, scripts parse."""
import re, subprocess, sys, pathlib
R = pathlib.Path(__file__).resolve().parent.parent; S = R / "skills"; bad = []
want = {"x-eo", "x-eo-audit", "x-eo-fix", "x-eo-verify"}
found = {p.parent.name for p in S.rglob("SKILL.md")}
if found != want: bad.append(f"SKILL.md dirs {sorted(found)} != {sorted(want)}")
for d in want:
    f = S / d / "SKILL.md"
    if not f.exists(): continue
    m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", f.read_text())
    if not m: bad.append(f"{f}: bad frontmatter"); continue
    if m.group(1) != d: bad.append(f"{f}: name {m.group(1)} != dir {d}")
    if len(m.group(2)) > 1024: bad.append(f"{f}: description too long")
for md in S.rglob("*.md"):
    txt = re.sub(r"```.*?```|`[^`\n]*`", "", md.read_text(), flags=re.S)
    if "claude-seo/" in str(md): txt = re.sub(r"^- \[[^\]]*\]\(url\).*$", "", txt, flags=re.M)
    for t in re.findall(r"\]\((?!https?:|#|mailto:)([^)\s]+)\)", txt):
        if not (md.parent / t.split("#")[0]).exists(): bad.append(f"{md.relative_to(R)}: broken link {t}")
for f in S.rglob("*.py"):
    try: compile(f.read_text(), str(f), "exec")
    except SyntaxError as e: bad.append(f"{f}: {e}")
for f in S.rglob("*.sh"):
    if subprocess.run(["bash", "-n", str(f)]).returncode: bad.append(f"{f}: bash syntax")
for f in S.rglob("*.mjs"):
    if subprocess.run(["node", "--check", str(f)], capture_output=True).returncode: bad.append(f"{f}: node syntax")
print("\n".join(bad) or "ok"); sys.exit(1 if bad else 0)

#!/usr/bin/env python3
"""Initialize the Idea Hatching workspace and optionally hatch one idea."""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import shutil
from pathlib import Path

ROOT = Path.home() / "idea-hatching"
SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_DIR / "templates"


def detect_lang(text: str) -> str:
    return "zh" if re.search(r"[一-鿿]", text) else "en"


def slugify(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    if words:
        base = "-".join(words[:6])
    else:
        mapping = {
            "会议": "meeting", "纪要": "note", "标签": "tagger", "结构化": "structured",
            "灵感": "idea", "自动": "auto", "工具": "tool", "知识": "knowledge",
            "计划": "plan", "研究": "research", "写作": "writing", "任务": "task",
        }
        hits = [v for k, v in mapping.items() if k in text]
        base = "-".join(hits[:6]) or "idea"
    base = re.sub(r"-+", "-", base).strip("-")[:64] or "idea"
    return base


def render(template: str, **values: str) -> str:
    out = template
    for k, v in values.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def ensure_workspace(root: Path = ROOT) -> None:
    root.mkdir(parents=True, exist_ok=True)
    index = root / "INDEX.md"
    if not index.exists():
        index.write_text(
            "# Idea Hatching · Index\n\n"
            "> Catalog of incubating ideas, one row each. status: incubating / hatched / blocked (fatal contradiction).\n"
            "> F = feasibility (0–3, cost vs benefit)   C = credibility (0–3, coverage + referenceability)\n\n"
            "| slug | status | F | C | last advanced | one-liner |\n"
            "|------|--------|---|---|---------------|-----------|\n",
            encoding="utf-8",
        )
    hb = root / "heartbeat.json"
    hb_template = TEMPLATES / "heartbeat.json"
    if not hb.exists() and hb_template.exists():
        hb.write_text(hb_template.read_text(encoding="utf-8"), encoding="utf-8")


def unique_slug(root: Path, base: str) -> str:
    slug = base
    i = 2
    while (root / slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


def hatch(idea: str, root: Path = ROOT) -> str:
    ensure_workspace(root)
    today = _dt.date.today().isoformat()
    lang = detect_lang(idea)
    slug = unique_slug(root, slugify(idea))
    idea_dir = root / slug
    idea_dir.mkdir(parents=True)

    values = {"slug": slug, "idea": idea, "lang": lang, "date": today}
    (idea_dir / "mind-model.md").write_text(render((TEMPLATES / "mind_model.md").read_text(encoding="utf-8"), **values), encoding="utf-8")
    (idea_dir / "lib.md").write_text(render((TEMPLATES / "lib.md").read_text(encoding="utf-8"), **values), encoding="utf-8")
    (idea_dir / "journal.md").write_text(render((TEMPLATES / "log.md").read_text(encoding="utf-8"), **values), encoding="utf-8")
    (idea_dir / "buffer.md").write_text(
        f"# Buffer · {slug}\n\n"
        "> The haiku subagent writes candidate edits here after research; the main agent accepts them into lib or drops them, then clears processed entries.\n"
        "> type: corroborate / refine / supplement / branch / contradiction.\n"
        "> status: pending / accepted / dropped / deferred.\n",
        encoding="utf-8",
    )

    with (root / "INDEX.md").open("a", encoding="utf-8") as f:
        f.write(f"| {slug} | incubating | 0 | 0 | 0000-00-00 | {idea.replace('|', '/')} |\n")
    return slug


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", default=str(ROOT))
    p.add_argument("--hatch")
    args = p.parse_args()
    root = Path(args.workspace).expanduser()
    if args.hatch:
        slug = hatch(args.hatch, root)
        print(f"hatched {slug} (incubating F0 C0).")
    else:
        ensure_workspace(root)
        print(f"initialized {root}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

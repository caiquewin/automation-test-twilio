#!/usr/bin/env python3
"""Gera sessions.html com todas as sessões do Claude Code deste repositório.

O Claude Code salva cada sessão como um arquivo JSONL em
~/.claude/projects/<caminho-do-repo-com-hifens>/<session-id>.jsonl
(ver https://code.claude.com/docs/en/how-claude-code-works#work-with-sessions).

Uso:
    python3 scripts/sessions_page.py [--out sessions.html]
"""
import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def sessions_dir(repo: Path) -> Path:
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(repo))
    return Path.home() / ".claude" / "projects" / slug


def parse_session(path: Path) -> dict:
    s = {"id": path.stem, "title": None, "prompts": [], "start": None, "end": None,
         "branches": set(), "version": None, "turns": 0}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = d.get("type")
        if t == "ai-title":
            s["title"] = d.get("aiTitle")
        if t == "custom-title" and d.get("customTitle"):
            s["title"] = d["customTitle"]
        ts = d.get("timestamp")
        if ts:
            s["start"] = s["start"] or ts
            s["end"] = ts
        if d.get("gitBranch"):
            s["branches"].add(d["gitBranch"])
        if d.get("version"):
            s["version"] = d["version"]
        if t == "assistant":
            s["turns"] += 1
        content = (d.get("message") or {}).get("content")
        if t == "user" and (d.get("origin") or {}).get("kind") == "human" and isinstance(content, str):
            s["prompts"].append((ts, content))
    return s


def fmt(ts: str | None) -> str:
    if not ts:
        return "—"
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%d/%m/%Y %H:%M")


def render(repo: Path, sessions: list[dict]) -> str:
    cards = []
    for s in sessions:
        prompts = "".join(
            f"<li><time>{fmt(ts)}</time><p>{html.escape(p)}</p></li>" for ts, p in s["prompts"]
        ) or "<li><p class=muted>Sem prompts.</p></li>"
        cards.append(f"""
<article class="card" data-search="{html.escape((s['title'] or '') + ' ' + ' '.join(p for _, p in s['prompts'])).lower()}">
  <header>
    <h2>{html.escape(s['title'] or 'Sessão sem título')}</h2>
    <div class="meta">
      <span>{fmt(s['start'])} → {fmt(s['end'])}</span>
      <span>{len(s['prompts'])} prompts · {s['turns']} respostas</span>
      <span>branch: {html.escape(', '.join(sorted(s['branches'])) or '—')}</span>
      <span>v{html.escape(s['version'] or '?')}</span>
    </div>
  </header>
  <div class="cmd"><code>claude --resume {s['id']}</code><button data-copy="claude --resume {s['id']}">Copiar</button></div>
  <div class="cmd"><code>claude --resume {s['id']} --fork-session</code><button data-copy="claude --resume {s['id']} --fork-session">Copiar</button></div>
  <details><summary>Prompts</summary><ol>{prompts}</ol></details>
</article>""")

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sessões do Projeto</title>
<style>
:root {{ --bg:#f7f7f5; --card:#fff; --fg:#1d1d1b; --muted:#6b6b66; --border:#e3e3de; --accent:#c96442; --code:#f0efea; }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg:#1a1a18; --card:#242422; --fg:#ecebe6; --muted:#9a9993; --border:#36352f; --accent:#e08a6a; --code:#2e2d29; }}
}}
:root[data-theme="dark"] {{ --bg:#1a1a18; --card:#242422; --fg:#ecebe6; --muted:#9a9993; --border:#36352f; --accent:#e08a6a; --code:#2e2d29; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:32px 16px; }}
h1 {{ margin:0 0 4px; font-size:24px; }}
.sub {{ color:var(--muted); margin:0 0 20px; word-break:break-all; }}
input {{ width:100%; padding:10px 12px; border:1px solid var(--border); border-radius:8px; background:var(--card); color:var(--fg); font:inherit; margin-bottom:20px; }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:18px; margin-bottom:16px; }}
.card h2 {{ margin:0 0 6px; font-size:17px; }}
.meta {{ display:flex; flex-wrap:wrap; gap:4px 16px; color:var(--muted); font-size:13px; margin-bottom:12px; }}
.cmd {{ display:flex; gap:8px; align-items:center; margin-bottom:6px; }}
.cmd code {{ flex:1; min-width:0; overflow-x:auto; white-space:nowrap; background:var(--code); padding:6px 10px; border-radius:6px; font-size:13px; }}
button {{ border:1px solid var(--border); background:transparent; color:var(--fg); border-radius:6px; padding:5px 10px; cursor:pointer; font:inherit; font-size:13px; }}
button:hover {{ border-color:var(--accent); color:var(--accent); }}
details {{ margin-top:10px; }}
summary {{ cursor:pointer; color:var(--accent); }}
ol {{ padding-left:20px; }}
li {{ margin:8px 0; }}
li time {{ color:var(--muted); font-size:12px; }}
li p {{ margin:2px 0 0; white-space:pre-wrap; word-break:break-word; }}
.muted {{ color:var(--muted); }}
</style>
</head>
<body>
<main>
  <h1>Sessões do Claude Code</h1>
  <p class="sub">{len(sessions)} sessões · {html.escape(str(repo))} · gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
  <input id="q" type="search" placeholder="Filtrar por título ou prompt…">
  {''.join(cards) or '<p class=muted>Nenhuma sessão encontrada.</p>'}
</main>
<script>
document.getElementById('q').addEventListener('input', e => {{
  const q = e.target.value.toLowerCase();
  document.querySelectorAll('.card').forEach(c => c.hidden = !c.dataset.search.includes(q));
}});
document.querySelectorAll('[data-copy]').forEach(b => b.addEventListener('click', async () => {{
  try {{ await navigator.clipboard.writeText(b.dataset.copy); b.textContent = 'Copiado'; }}
  catch {{ b.textContent = 'Falhou'; }}
  setTimeout(() => b.textContent = 'Copiar', 1500);
}}));
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO_ROOT / "sessions.html"))
    args = ap.parse_args()

    src = sessions_dir(REPO_ROOT)
    files = sorted(src.glob("*.jsonl")) if src.is_dir() else []
    sessions = sorted((parse_session(f) for f in files), key=lambda s: s["start"] or "", reverse=True)
    Path(args.out).write_text(render(REPO_ROOT, sessions), encoding="utf-8")
    print(f"{len(sessions)} sessões de {src} -> {args.out}")


if __name__ == "__main__":
    main()

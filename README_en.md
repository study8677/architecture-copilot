# Architecture Copilot 🧭

> A "co-design + evidence-based repository review" skill for **Claude Code / Cursor / OpenAI Codex**.
> For a new system it uses structured questions; for an existing repository it reads the code and configuration before making architectural claims.

**English** · [简体中文](./README.md)

[![Skill for](https://img.shields.io/badge/skill%20for-Claude%20Code%20·%20Cursor%20·%20Codex-3c8772.svg)](#-three-tools-ready-to-use)
[![Method from](https://img.shields.io/badge/method%20from-awesome--architecture-blue.svg)](https://github.com/study8677/awesome-architecture)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing)

---

## Why it exists

AI can already write most of your code. But there's one thing it won't do for you on its own — and it's exactly what makes or breaks a project:

> **Figure out what the system should look like, before you start.**

Most AI coding assistants default to "you say what you want, I start writing immediately." So you get rushed into implementation details before thinking through boundaries, scale, consistency, trade-offs — and by the time the architectural landmine goes off, it's months later and you're rewriting from scratch.

**Architecture Copilot does the opposite**: it turns the AI from "an intern itching to write code" into "a senior architect who thinks it through with you first." You describe what you want to build; it draws nothing and writes nothing — instead it asks **one question after another** until the architecture surfaces in the conversation itself.

---

## How it works

It follows a fixed guided flow (adapted from the "six soul questions" and "8-step design method" in [awesome-architecture](https://github.com/study8677/awesome-architecture)):

```
You: I want to build a multiplayer to-do list app.

Copilot: OK, forget tech for now. Which existing product is it most like?
         Personal use, or teams?
You: Teams, like a simplified Notion.

Copilot: Got it. Let's cut scope first — what does this version NOT do?
         (Comments? Permissions? Offline?)
You: Offline can wait, but permissions are needed.

Copilot: Then a few key ones: (1) Roughly how many people edit the same
         list at once? (2) If two people edit the same item simultaneously,
         who wins — or do you keep both?
You: Small teams, a few at once; simultaneous edits... can't lose data.

Copilot: That's the crux. "Can't lose data" means you don't want simple
         "last-write-wins" — you need CONFLICT MERGING, the hard part of
         collaborative docs. Two paths:
           A. OT: needs a central server to order ops; mature but complex.
           B. CRDT: built for offline/multi-device merge, but extra overhead.
         You said "no offline for now," so A's cost is more contained.
         Lean toward A?
You: Makes sense, A for now.

Copilot: ✅ Decision logged: use OT, give up CRDT's offline edge, because
         the MVP doesn't do offline. Next fork in the road…
```

By the end, it helps you converge on: **an ASCII architecture diagram, a data model, a list of ADRs (decision records), scaling-bottleneck warnings, an MVP→mature evolution path, and an honest list of risks.**

### Existing repositories: evidence before opinion

Ask it to "understand this repository, reconstruct the current architecture from code, and rank the three highest-leverage improvements." It will inspect entry points, core modules, data and migrations, deployment / CI, tests, and real request or event flows before answering. The result includes:

- the current Context / Container view and primary data flows;
- an Observed / Inferred / Unknown evidence table with file or command references;
- a Top 3 ranked by impact, confidence, reuse, cost, and risk;
- validation steps, rollback paths, ADR candidates, and enforceable architecture guardrails.

That makes the skill useful not only before a project starts, but also when onboarding to an unfamiliar codebase, prioritizing technical debt, or reviewing an evolution plan.

---

## Eight stages (0-7)

| Stage | What it's doing |
|---|---|
| 0 · Open | One question: what do you want to build? Like which product? |
| 1 · Scope | Whom does it serve? **More importantly, what does this version NOT do** |
| 2 · Six soul questions | Scale / read-write ratio / consistency / growth / cost of failure / constraints |
| 3 · Back-of-envelope | Compute QPS & storage on the spot — what will crush this system? |
| 4 · Quality attributes | Performance/availability/consistency/cost… forcing you to **rank, because you can't have all** |
| 5 · Key decisions ⭐ | By system type, raise each fork: option A vs B, and the cost of each |
| 6 · Converge | Diagram + data model + ADRs + bottlenecks + evolution + risks |
| 7 · Challenge | Proactively: where will it die? what did you give up? |

> Iron rules throughout: **ask before answering, one dimension at a time, interrogate "why / at what cost" for every choice, never sink into syntax, cut scope relentlessly.**

---

## 🛠 Three tools, ready to use

| Tool | Form | Where it goes |
|---|---|---|
| **Claude Code** | [`skills/architecture-copilot/SKILL.md`](skills/architecture-copilot/SKILL.md) | `~/.claude/skills/` or project `.claude/skills/` |
| **Cursor** | [`.cursor/rules/architecture-copilot.mdc`](.cursor/rules/architecture-copilot.mdc) | your project's `.cursor/rules/` |
| **OpenAI Codex** | native [`skills/architecture-copilot/`](skills/architecture-copilot/) | `~/.codex/skills/architecture-copilot/` |
| **Codex project overlay** | [`AGENTS.md`](AGENTS.md) (optional) | merge into the project-root `AGENTS.md` |
| **Any other AI** | paste `SKILL.md` body as the system prompt | —— |

👉 Full install steps in **[INSTALL.md](INSTALL.md)**.

---

## 🔗 Relationship with awesome-architecture

The two repos are a pair:

| | Repo | Role |
|---|---|---|
| 📚 | **[awesome-architecture](https://github.com/study8677/awesome-architecture)** | **Knowledge**: a continuously evolving architecture-thinking tutorial, system templates, and end-to-end cases (architecture only, no syntax). |
| 🧭 | **architecture-copilot** (this repo) | **Capability**: turns that knowledge into a skill that **actively guides you** inside Claude Code / Cursor / Codex. |

> One is the textbook; the other is the tutor that asks the questions. While guiding you, the Copilot cites the matching template and methodology from the former (building e-commerce? it pulls out the [e-commerce template](https://github.com/study8677/awesome-architecture/blob/main/templates/ecommerce-platform/README.md)'s key decisions to interrogate you).

---

## ✅ Verifiable, not prompt editing by feel

The repository includes realistic evaluation cases, structural / drift checks, and a read-only repository inventory tool:

```bash
python3 scripts/check_quality.py
python3 -m unittest discover -s tests -v
python3 skills/architecture-copilot/scripts/repo_inventory.py . --format markdown
```

CI checks skill metadata, cross-surface capability parity, template-to-reference routing, evaluation fixtures, and native Codex packaging. Behavioral changes should also be forward-tested against `evals/cases.json` with an independent agent.

---

## 🤝 Contributing

Add key-decision prompts, improve the guided workflow, contribute evaluation cases, or translate. Edit [`skills/architecture-copilot/SKILL.md`](skills/architecture-copilot/SKILL.md) first (the source of truth), sync `.cursor/rules/architecture-copilot.mdc` and `AGENTS.md`, then run `python3 scripts/check_quality.py` and the unit tests.

---

> 📌 In one line: **AI made "writing code" cheap, and "figuring out what to write" priceless. This skill flips the AI into the "think it through with you first" mode.**

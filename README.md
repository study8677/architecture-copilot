# Architecture Copilot · 架构副驾 🧭

> 一个给 **Claude Code / Cursor / OpenAI Codex** 用的「架构共创」skill。
> 在你写第一行代码前,它用**持续的深度提问**陪你把系统架构想清楚——不是替你决定,而是帮你看清每个选择背后的取舍。

[English](./README_en.md) · **简体中文**

[![Skill for](https://img.shields.io/badge/skill%20for-Claude%20Code%20·%20Cursor%20·%20Codex-3c8772.svg)](#-三种工具-即取即用)
[![Method from](https://img.shields.io/badge/方法论源自-awesome--architecture-blue.svg)](https://github.com/study8677/awesome-architecture)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-贡献)

---

## 为什么需要它

AI 已经能替你写绝大部分代码。但有件事它不会主动替你做,而它恰恰是项目成败的关键:

> **在动手之前,先想清楚这个系统该长什么样。**

大多数 AI 编程助手的默认行为是「**你说要什么,我立刻开始写**」。于是你常常在没想清楚边界、规模、一致性、取舍的情况下,就被它带着冲进了实现细节——等架构的坑暴露出来,已经是几个月后、推倒重来的时候了。

**架构副驾反其道而行**:它把 AI 从「急着写代码的实习生」变成「先陪你想清楚的资深架构师」。你说想做个东西,它不画图、不写码,而是**一个问题接一个问题地追问**,直到架构在对话中自己浮现出来。

---

## 它是怎么工作的

它遵循一套固定的引导流程(改编自 [awesome-architecture](https://github.com/study8677/awesome-architecture) 的「灵魂六问」与「八步设计法」):

```
你:我想做一个多人协作的待办清单 App。

副驾:好,先别管技术。它最像哪个已有产品?是给个人用,还是团队?
你:团队用,像简化版的 Notion。

副驾:明白。先做减法——这一版【不做】什么?(评论?权限?离线?)
你:离线先不做,权限要。

副驾:那问几个关键的:① 大概多少团队、多少人同时编辑同一份清单?
     ② 两个人同时改同一项,你希望谁赢、还是都保留?
你:小团队,几人同时编辑;同时改的话……不能丢吧。

副驾:这就触到核心了。"不能丢"意味着你需要的不是简单的"最后写入者赢",
     而是【冲突合并】——这正是协同文档的难点。给你两条路:
       A. OT(操作转换):需要中心服务器定序,成熟但实现复杂;
       B. CRDT:天生支持离线/多端合并,但数据结构有额外开销。
     你前面说"离线先不做",那 A 的代价更可控。倾向 A 吗?
你:有道理,先 A。

副驾:✅ 记一条决策:用 OT,放弃 CRDT 的离线优势,因为 MVP 不做离线。
     继续下一个岔路口……
```

到最后,它会帮你收敛出:**架构全景图(ASCII)、数据模型、一串 ADR 决策记录、规模化瓶颈预警、MVP→成熟的演进路线、以及诚实的风险清单**。

---

## 七个阶段

| 阶段 | 它在干什么 |
|---|---|
| 0 · 开场 | 只问一句:你想做什么?最像哪个产品? |
| 1 · 业务与范围 | 为谁解决什么问题?**更重要的是,这一版不做什么** |
| 2 · 灵魂六问 | 规模 / 读写比 / 一致性 / 增长 / 失败代价 / 约束 |
| 3 · 信封背面估算 | 当场算 QPS 和存储量,判断「这系统会被什么压垮」 |
| 4 · 质量属性取舍 | 性能/可用/一致/成本…逐项过,**逼你排序,不可能全要** |
| 5 · 关键决策追问 ⭐ | 按系统类型,逐个抛出岔路口:选项 A vs B,代价各是什么 |
| 6 · 收敛产出 | 架构图 + 数据模型 + ADR + 瓶颈 + 演进路线 + 风险 |
| 7 · 反挑战 | 主动指出:它会死在哪?你放弃了什么? |

> 全程铁律:**先问后答、一次一个维度、每个选择都追问「为什么/代价」、不陷入语法、拼命做减法。**

---

## 🛠 三种工具,即取即用

| 工具 | 形态 | 放哪 |
|---|---|---|
| **Claude Code** | [`skills/architecture-copilot/SKILL.md`](skills/architecture-copilot/SKILL.md) | `~/.claude/skills/` 或项目 `.claude/skills/` |
| **Cursor** | [`.cursor/rules/architecture-copilot.mdc`](.cursor/rules/architecture-copilot.mdc) | 你项目的 `.cursor/rules/` |
| **OpenAI Codex** | [`AGENTS.md`](AGENTS.md) | 你项目根的 `AGENTS.md` |
| **任何其它 AI** | 直接把 `SKILL.md` 正文当系统提示粘贴 | —— |

👉 详细安装步骤见 **[INSTALL.md](INSTALL.md)**。

---

## 🔗 和 awesome-architecture 的关系

这两个仓库是一对搭档:

| | 仓库 | 角色 |
|---|---|---|
| 📚 | **[awesome-architecture](https://github.com/study8677/awesome-architecture)** | **知识**:架构思维教程 + 数十个模板/架构地图(只讲架构、不讲语法,数量以上游为准)。还有一个[可交互教学站](https://github.com/study8677/awesome-architecture)。 |
| 🧭 | **architecture-copilot**(本仓库) | **能力**:把上面那套知识,变成一个能在 Claude Code/Cursor/Codex 里**主动引导你**的 skill。 |

> 一个是「教材」,一个是「会提问的私教」。副驾在引导你时,会引用前者里对应的模板和方法论(比如你做电商,它就搬出 [电商平台模板](https://github.com/study8677/awesome-architecture/blob/main/templates/ecommerce-platform/README.md) 的关键决策来追问你)。

---

## 🤝 贡献

欢迎补充更多系统类型的「关键决策追问」、改进引导话术、或翻译。先改 [`skills/architecture-copilot/SKILL.md`](skills/architecture-copilot/SKILL.md)(权威版),再同步 `.cursor/rules/architecture-copilot.mdc` 与 `AGENTS.md`;如果涉及教程/模板数量,也同步 `README.md`、`README_en.md`、`INSTALL.md`。

---

> 📌 一句话:**AI 让「写代码」变廉价,而「想清楚该写什么」变得空前值钱。这个 skill,就是把 AI 调成「先陪你想清楚」的那一档。**

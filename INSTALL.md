# 安装与使用

「架构副驾」是一套**给 AI 编程助手用的引导规范**。同一套规范封装成三种形态,按你用的工具取用即可。核心规范以 [`skills/architecture-copilot/SKILL.md`](skills/architecture-copilot/SKILL.md) 为准。

---

## 🟣 Claude Code

Claude Code 的 **Skills** 机制:把带 `name` / `description` 的 `SKILL.md` 放进 skills 目录,Claude 会根据 description 在合适时机**自动调用**。

```bash
# 方式一:用户级(所有项目可用)
mkdir -p ~/.claude/skills
cp -r skills/architecture-copilot ~/.claude/skills/

# 方式二:项目级(随项目走,可提交进 git)
mkdir -p .claude/skills
cp -r skills/architecture-copilot .claude/skills/
```

然后在 Claude Code 里直接说:**「帮我设计一下这个系统的架构」** 或 **「用 architecture-copilot 陪我理一下架构」**,它就会进入引导提问模式。

---

## 🔵 Cursor

Cursor 的 **Project Rules** 机制:`.cursor/rules/*.mdc`,带 `description` 的规则在「Agent 模式」下按需自动启用。

```bash
# 拷到你自己项目的 .cursor/rules/
mkdir -p .cursor/rules
cp .cursor/rules/architecture-copilot.mdc /你的项目/.cursor/rules/
```

然后在 Cursor 的 Chat / Agent 里说 **「帮我讨论这个新项目的架构」**;也可以用 `@architecture-copilot` 显式引用该规则。

---

## 🟢 OpenAI Codex

Codex 会自动读取项目根的 **`AGENTS.md`**。

```bash
# 如果你的项目还没有 AGENTS.md,直接拷过去:
cp AGENTS.md /你的项目/AGENTS.md

# 如果已有 AGENTS.md,把本仓库 AGENTS.md 的内容追加进去即可。
```

然后对 Codex 说 **「我想做一个 X,帮我把架构想清楚」**,它会按规范以提问方式引导你。

---

## ⚪ 任何其它 AI(通用兜底)

不依赖任何工具机制——**直接把 [`SKILL.md`](skills/architecture-copilot/SKILL.md) 的正文,作为系统提示 / 第一条消息,粘贴给任意大模型**(ChatGPT、Gemini、DeepSeek、通义……),然后说出你想做的东西即可。

---

## 它会怎么陪你(交互预期)

1. 先问你**想做什么**(一句话定位),不让你一上来就陷入技术细节;
2. 然后**一步步深度追问**:业务范围 → 灵魂六问(规模/读写比/一致性/增长/失败代价/约束)→ 信封背面估算 → 质量属性取舍 → 关键决策;
3. **每个技术选择都追问「为什么、代价是什么」**,你答不上来时给你候选项;
4. 最后**收敛产出**:架构全景图(ASCII)、数据模型、ADR 决策记录、规模化瓶颈、演进路线、风险清单。

> 它的知识与案例来自 **[awesome-architecture](https://github.com/study8677/awesome-architecture)** —— 一个专讲架构、不讲语法的开源知识库(系统设计教程 + 数十个模板/架构地图,数量以上游为准)。

# 贡献指南

感谢你想改进「架构副驾」!

## ⚠️ 核心原则:SKILL.md 是权威

引导规范以 [`skills/architecture-copilot/SKILL.md`](skills/architecture-copilot/SKILL.md) 为**唯一权威源**。改了它之后,请**同步**到另外两个工具形态(三份的核心流程必须保持一致,只有 frontmatter / 触发说明因工具而异):

- [`.cursor/rules/architecture-copilot.mdc`](.cursor/rules/architecture-copilot.mdc)(Cursor)
- [`AGENTS.md`](AGENTS.md)(Codex)

> 提 PR 时请在描述里注明:你改了哪一处、是否三份都同步了。

### 关于 `skills/architecture-copilot/references/`

Claude Code 形态额外带一个 `references/` 深度层(渐进式披露:正文不加载,阶段 5 命中模板才按需读)。它**只沉淀每个模板的「关键决策 / 反模式 / 演进信号」三节**,按类别打包成 6 个文件,外加 `signals.md`(升级信号对照表)和 `glossary.md`(术语速查)两份来自上游 `tutorial/` 的通用切片,不是上游全文。维护约定:

- 这是上游 `templates/` 的**裁剪快照**,每个文件头标了快照日期;上游为唯一权威源,冲突时以上游为准。
- 需要完整 14 节模板 / 案例,一律指向上游 `templates/<slug>/`,**不要**把全文搬进 references(注定滞后、打不过 `git clone`)。
- `.mdc` / `AGENTS.md` 是单文件形态,无此机制,只需保持映射表与数字同步即可。

## 常见贡献

- 🧭 给「**知识锚点映射表**」补新的系统类型 → 对应「必问的关键决策」
- 💬 改进引导话术、七阶段流程
- 📝 提供完整的**实战示例对话**(从开场到产出 ADR 走一遍)
- 🌍 翻译(英文 / 其它语言)

## 方法论来源

本 skill 的提问流程与案例知识,来自搭档仓库 [awesome-architecture](https://github.com/study8677/awesome-architecture)。补充关键决策时,优先与那里的模板和教程对齐。

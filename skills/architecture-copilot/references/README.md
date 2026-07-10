# references · 按需加载的模板深度层

这里是 `architecture-copilot` skill 的**渐进式披露(progressive disclosure)**层。
`SKILL.md` 正文始终常驻上下文;本目录下的文件**不自动加载**,只有当模型在阶段 5(关键决策追问)
把用户系统匹配到某个模板后,**按正文指引去读对应的那一个类别文件**。

## 为什么这样切

- **不是全文搬运。** 每个模板只沉淀「关键决策与权衡 / 常见反模式 / 演进与触发信号」三节——
  这三节信息密度最高、变动最慢,且**压成一行问句会失真**(重建不出岔路口的代价对比)。
  架构图、组件职责、数据流、数据模型、安全细节仍留在上游全文,不在这里。
- **按类别打包,不是一模板一文件。** 在「每命中付太多 token」和「32 个散文件的同步负担」之间取中点:
  6 个文件、每个 4–6 个模板,模型一次只读一个类别。

## 六个类别文件

| 文件 | 覆盖模板 |
|---|---|
| `web-and-product.md` | standard-web-app、mobile-app、browser-extension、url-shortener、search-engine、social-feed |
| `transactional.md` | ecommerce-platform、payment-system、online-ticketing、notification-system、ride-hailing |
| `realtime-and-storage.md` | realtime-chat、collaborative-doc、cloud-storage、video-streaming |
| `ai-native.md` | ai-chat-product、ai-gateway、rag-knowledge-base、vector-database、inference-serving、ai-agent-platform |
| `agent-and-org.md` | claude-code、codex、openclaw、hermes、system-prompt-architecture、ai-native-organization |
| `embedded-industrial.md` | embedded-device、iot-platform、industrial-edge、automotive-ee、robotics |

另有两份**跨模板通用**的稳定切片(来自上游 `tutorial/`,非某个模板专属):

| 文件 | 用途 |
|---|---|
| `signals.md` | 「什么信号 → 该升级什么」量化对照表,阶段 5 演进追问 / 阶段 7 反挑战引用 |
| `glossary.md` | 核心架构术语速查,用户卡在概念时对齐 |

## 漂移策略(维护者必读)

- 本目录是上游 [awesome-architecture](https://github.com/study8677/awesome-architecture) `templates/` 的**裁剪快照**,
  每个文件头部标注了快照日期。上游会持续演进(模板数、决策点都会变)。
- **上游永远是唯一权威源。** 用户需要完整 14 节模板 / 案例时,指引其去上游 `templates/<slug>/`,
  不要试图在这里维护全文——那注定滞后且打不过 `git clone`。
- 更新本层时:只同步「关键决策 / 反模式 / 演进信号」三节的实质变化,并更新快照日期;
  不要把它扩成上游的镜像。发现本层与上游冲突,以上游为准。

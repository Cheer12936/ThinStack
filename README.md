# ThinStack · 薄栈

> **统一交付标准，不统一实现步骤。**  
> Minimal process. Explicit contracts. Evidence-backed delivery.

ThinStack 是一个面向 AI 软件开发的轻量交付方法与 `ts-code` Skill。它不要求模型机械执行一套大而全的流程，而是围绕当前业务结果，按需使用需求澄清、项目记忆、TDD、风险验证与机器一致性检查，让 AI **更快交付、少做无关工作、能跨会话继续，并且知道凭什么算完成**。

当前版本：**v0.3.0**

## 从“薄肌”到“薄栈”

ThinStack 受到 Alan 的“薄肌理论”启发：**不靠堆体量制造效果，而是保留真正有效的投入，让结果足够明显。**

我们把这个思路迁移到 AI 软件工程中：

- 不是步骤越少越好，而是**只保留必要步骤**；
- 不是文档越少越好，而是**只保存下一次还会有价值的事实**；
- 不是测试越多越好，而是**用最小充分证据证明当前结果**；
- 不是让所有模型走同一路径，而是**统一交付标准，让实现过程保持弹性**；
- 不是只追求今天快速生成，而是让系统**下一次仍然容易理解、修改和验证**。

因此我们把“薄肌”进一步抽象成 **薄栈理论**：

> **用最少必要的决策、文档、验证和自动约束，可靠交付一个可观察结果，并保持下一次修改仍然简单。**

## ThinStack 解决什么

AI 编程的问题通常不是“不会写代码”，而是：

| 常见问题 | ThinStack 的处理 |
|---|---|
| 需求没说清，AI 很快做错方向 | 只在会改变产品/架构的重要歧义上进入 Grill 式追问 |
| 新项目一开始就过度设计 | 先确定跨片高代价决定，只详细设计当前 Slice |
| 长任务跨会话后失忆、反复重做 | 项目总览 + 永久切片档案 + 薄基线恢复上下文 |
| 强模型被机械流程拖慢 | 默认自主，只约束结果、边界与证据 |
| 模型开始跑偏、重复无效修改 | 按实际表现切入 Guided，引导缩小步长 |
| 测试通过但不等于业务完成 | Green Contract 把验收和真实证据绑定 |
| 总览、切片、证据互相打架 | 可选 `doctor` 做机械一致性检查，`sync` 派生总览 |
| 代码越生成越难改 | 强调模块职责、清晰接口、规则归属和必要局部整理 |

## Workflow

```text
需求 / 任务
   ↓
① 分流 + 授权
   FAST_FIX / PROJECT_INIT / SLICE
   ↓
② 恢复相关上下文
   总览 → 当前切片 → 基线 → 必要依赖 / 代码
   ↓
③ 关键歧义？
   是 → Grill / BDD：只问会改变结果或架构的问题
   否 → 复用已有决定
   ↓
④ 当前 Slice + Green Contract
   为什么做 / 可观察行为 / 负责模块 / 不变量 / 验收证据
   ↓
⑤ 一次确认（需要时）
   已批准同一范围则不重复确认
   ↓
⑥ 实现与反馈
   默认自主
   ├─ 适用时 TDD
   ├─ 适用时风险强化验证
   └─ 跑偏时 Guided
   ↓
⑦ 实际测试 / 运行观察
   ↓
⑧ 更新切片档案与证据
   ↓
⑨ [可选机器接入] doctor → sync
   检查一致性 → 派生总览进度
   ↓
⑩ 交付
   可操作结果 + 环境 + 当前证据 + 未验证边界
```

**这不是固定十步流水线。** 小修复不会被迫创建完整项目档案；BDD、SDD、TDD、风险验证和 Guided 都按实际信号加载。

## 三种工作类型

| 类型 | 适用场景 | 核心目标 |
|---|---|---|
| `FAST_FIX` | 行为清楚的局部 Bug | 找直接原因、窄范围修复、验证后停止 |
| `PROJECT_INIT` | 新项目 / 新系统 | 明确首个可用结果、跨片关键决定、薄基线与首片路线 |
| `SLICE` | 新业务结果或独立技术结果 | 一次交付一个可独立验收的结果 |

多个结果按**业务结果**拆片，不按“前端 / 后端 / 数据库”机械拆分。

## 项目记忆：一个总览，每片永久留存

ThinStack 不把模型上下文当持久存储。

| 文档 | 负责什么 |
|---|---|
| `docs/SLICES.md`（或已有入口） | 客户与 AI 共用的项目总览、范围、全量切片、阻塞与下一步 |
| `docs/slices/<id>.md`（或已有 SPEC/RUN） | 单个 Slice 的原因、行为、设计增量、状态、验收、证据与历史 |
| `docs/architecture/BASELINE.md`（或已有架构文档） | 跨 Slice 长期成立的模块职责、术语、身份/数据归属、接口与重要决定 |
| 测试 / 日志 / Evidence | 支撑“为什么可以说完成”的实际证据 |

原则：**总览展示全局，切片档案保存本片事实，基线保存长期规则，证据支撑完成结论。**

完成和取消的 Slice 都保留稳定编号；恢复任务时只读取当前片及必要依赖，不全量重读历史。

## 按信号加载，而不是全量加载

`ts-code` 只有一个核心 Skill，五份 Reference 按需使用：

| 信号 | 加载 |
|---|---|
| 新项目、正式切片、重要规则变化、恢复 | `memory.md` |
| 业务/技术歧义会改变产品、架构或高代价决定 | `clarify.md` |
| 已决定采用测试先行 | `tdd.md` |
| 权限、金额、数据、迁移、外部服务、并发等真实风险 | `risk-proof.md` 相关部分 |
| 用户要求引导或已有实际跑偏信号 | `guided.md` |

目标不是“流程完整”，而是**需要多少约束，就加载多少约束**。

## 安装

```text
git clone https://github.com/Cheer12936/ThinStack.git
cd ThinStack
python tools/manage.py install --skills-dir "你的客户端技能目录"
```

更新：

```text
git pull --ff-only
python tools/manage.py update --skills-dir "你的客户端技能目录"
```

请整体更新 `skills/ts-code`，不要只覆盖 `SKILL.md`。安装器不会猜客户端目录，也不会自动修改宿主配置；更新/卸载前会归档旧 Skill。

不同宿主的技能发现、隐式调用和项目指令机制不同。默认包保持显式调用；项目级接入见 [`docs/PROJECT-ADOPTION.md`](docs/PROJECT-ADOPTION.md)。

## 使用

```text
$ts-code 修复这个回访列表问题，保持现有权限与数据规则。

$ts-code 初始化库存项目，先明确首个可用结果和影响整体架构的关键决定。

$ts-code 增加一个业务切片：员工可以筛选待回访客户。

$ts-code 按已有总览和切片继续，不重做已经验证的模块。

$ts-code 只设计下一可执行 Slice，不修改产品代码。

$ts-code 建立项目总览和永久切片档案，本次只建档。
```

新项目 / 新业务默认展示一次关键方案并确认；同一具体范围已批准或用户明确要求直接实施时，不重复确认。设计、只读、验证、实施、生产写入和部署是不同授权。

## 可选：把“纪律”变成机器检查

v0.3.0 可以让现有 Markdown 项目显式接入机器字段，而不是维护第二套数据库。完整协议见 [`skills/ts-code/scripts/PROJECT_STATE.md`](skills/ts-code/scripts/PROJECT_STATE.md)。

```text
# 只读检查
python skills/ts-code/scripts/project_state.py doctor --root "项目目录" --json

# 预览总览生成区变化
python skills/ts-code/scripts/project_state.py sync --root "项目目录"

# 获得项目写入授权后更新总览生成区
python skills/ts-code/scripts/project_state.py sync --root "项目目录" --write

# 要求某个 Slice 当前具备有效验证记录
python skills/ts-code/scripts/project_state.py doctor --root "项目目录" --require-verified S-001
```

`doctor` 可机械检查重复编号、依赖、死链、基线版本、正式验收与 Evidence 覆盖、声明输入摘要以及总览是否过期；`sync` 从切片档案派生进度区域。

它**不会**运行测试、理解全部自然语言业务规则、证明批准真实、认证生产安全或自动宣布产品 GREEN。需要强制放行时，应把检查接入客户项目 CI / 分支保护，并保护验收标准和验证器本身。

## 完成意味着什么

ThinStack 只有在当前承诺范围满足时才报告 `GREEN`：

```text
正式验收项都有当前证据
+ 项目必需检查通过
+ 适用风险底线满足
+ 没有相关已知回归 / 未解决高风险
```

`GREEN` 只表示**当前工程范围已获得相应证据**。

它不自动代表：

- 用户真的需要这个功能；
- 产品已经产生商业价值；
- 已经部署生产；
- 客户已经验收；
- 整个项目全部完成。

这些状态分别记录。

## 验证与评测

```text
python tools/validate.py
python -B -m unittest discover -s tests -v
python -B examples/project-state/demo.py --root "新的空目录"
python tools/context_budget.py
```

当前 v0.3.0 已通过 Ubuntu / Windows CI；工具回归、项目状态检查和评测 Harness 的结果见 [`docs/RELEASE-v0.3.0.md`](docs/RELEASE-v0.3.0.md)。

最小对照评测 Harness 位于 [`evals/harness/`](evals/harness/README.md)，用于比较同一任务下的 **bare / autonomous / guided**。框架和正反控制已经验证，但**当前没有真实模型对照结果，不宣称 ThinStack 已被证明提升某个模型的成功率、Token 或速度**。

## 仓库结构

```text
skills/ts-code/            # 可安装 Skill
  SKILL.md                 # 核心规则
  references/              # 按需加载：memory / clarify / tdd / risk-proof / guided
  assets/                  # 总览、基线、切片模板
  scripts/                 # Evidence 与项目状态检查

docs/                      # 接入、发布与迁移说明
evals/                     # 可复现评测场景与 Harness
examples/                   # 最小可运行示例
tools/                      # 安装、包校验、上下文预算
```

## 设计边界

ThinStack **不是**：

- 一个替你做产品决策的 PRD 生成器；
- 强制每个任务都跑 BDD + SDD + TDD 的重流程；
- 自动监控模型“变聪明 / 变笨”的独立服务；
- 只靠哈希就能防止同权限伪造的安全系统；
- 对生产正确性、用户需求或商业收益的保证。

ThinStack 的目标更窄：

> **让 AI 围绕一个明确结果工作，记得为什么改、知道不能破坏什么，并用当前有效证据结束任务。**

## 贡献与安全

- 贡献指南：[`CONTRIBUTING.md`](CONTRIBUTING.md)
- 安全说明：[`SECURITY.md`](SECURITY.md)
- 版本记录：[`CHANGELOG.md`](CHANGELOG.md)
- v0.3.0 交付记录：[`docs/RELEASE-v0.3.0.md`](docs/RELEASE-v0.3.0.md)

MIT License。详见 [`LICENSE`](LICENSE)。

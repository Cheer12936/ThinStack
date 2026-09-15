# 项目检查与总览同步（可选接入）

`project_state.py` 是交付记录检查器，不是安装器，不执行档案中的命令，不测试业务，也不能证明报告真实。默认只读；只有 `sync --write` 会写总览的生成区域，不改切片、基线、历史或批准。五份工作流参考不因此全部加载。

## 接入

先取得项目建档/修改授权，沿用已有入口。新旧项目都可以只保留人工 Markdown；不采用机器字段不会自动迁移。启用时，在项目根目录添加 `.thinstack.json`（也可用 `--config` 指定其他路径）：

```json
{"schema_version":1,"overview":"docs/SLICES.md","records":["docs/slices/001.md"],"baselines":["docs/architecture/BASELINE.md"]}
```

配置仅登记路径，不维护另一套状态。路径必须在项目内，不接受符号链接。`records` 每个文件允许多个独立 `thinstack-slice` 块，因此已有 SPEC/RUN 的不同切片章节无需改名。总览、档案、基线须为不同路径；混在同一文件的旧项目可先保持人工模式，不能静默拆档。未登记文件不在检查范围，新增/移动档案须同步配置。无配置或旧文档没有机器块时明确报错，不假装已检查。

总览在需要显示自动进度的位置放且只放一对标记：

```text
<!-- thinstack:progress:start -->
<!-- thinstack:progress:end -->
```

不会自动插入标记或覆盖整篇总览。其余目标、范围、客户说明原样保留；生成区包含来源摘要、每片阶段、证据状态、阻塞、依赖、部署/客户验收记录值及分类统计。

## 每片的机器字段

在原档案中添加一个围栏，语言名为 `thinstack-slice`，内容是严格 JSON（拒绝重复键、未知字段、NaN）：

````text
```thinstack-slice
{
  "schema_version": 1,
  "id": "S-001",
  "title": "员工可以查询库存",
  "type": "business",
  "module": "inventory",
  "stage": "planned",
  "scope": "current",
  "dependencies": [],
  "blocker": "",
  "next": "确认行为并实现",
  "approval": {"state":"proposed","source":""},
  "acceptance": [],
  "inputs": [],
  "baseline_refs": {},
  "evidence": "",
  "deployment": "未知",
  "customer_acceptance": "未知"
}
```
````

未轮到的片允许空验收、空输入，但不允许声称已验证。正式验收内容写在 acceptance，而不是从证据报告反向生成。采用此块后，正文解释理由与历史，不另维护同名“最新状态”。

| 字段 | 规则 |
|---|---|
| id | 稳定 ASCII 编号，1–80 字符；不复用取消编号 |
| type | business / technical / foundation（业务/技术/基础） |
| stage | clarify / approval / planned / doing / verify / verified / cancelled |
| scope | current / deferred（本期/延后）；取消由 stage 表示 |
| dependencies | 其他已登记切片 ID；检查缺失、自环和循环，不把依赖存在当成联动通过 |
| approval | proposed 或 approved；approved 必须记录来源，但工具不认证其真实性 |
| acceptance | `[{"id":"AC-1","text":"明确的成功条件","kinds":["runtime"]}]`，编号唯一；kinds 明确允许 mock/replay/runtime/live/manual 中哪些证据，模拟不会自动升级 |
| inputs | 必需的代码、测试、配置相对路径；不能填进度档案或证据自身。范围完整性仍需审查 |
| baseline_refs | 基线相对路径→实际 SHA256；须在配置登记；基线变动先标记需核对，不擅自判定全部业务错误 |
| evidence | 当前有效证据 JSON 相对路径；历史另保留，不混用失败和旧通过结果 |
| blocker / next | 本片唯一当前阻塞与下一步；阻塞不抹去阶段 |
| deployment / customer_acceptance | 原样标为“记录值”；不从测试通过自动生成生产或客户批准事实 |

## 证据对照

兼容既有 `check_evidence.py` 的 schema_version=1 记录，机器模式还需要：
- `slice_id` 对应本片，`contract_sha256` 对应当前正式约定；每项 checks 增加 `kind`。
- `required` 与本片 acceptance ID 完全一致；每项通过证据的 kind 必须被该验收允许。
- snapshot 包含所有声明的 inputs 与 baseline_refs，并核对实际文件摘要。
- `contract_sha256` 按本脚本 `contract_digest(record)` 计算：仅包含 id、acceptance、approval、inputs、baseline_refs，以排序键、无额外空白的 UTF-8 JSON 哈希。doctor 的 JSON 输出提供当前值。

不要手填虚构哈希，不通过删验收、改测试、改规则来获得通过。进度、时间和总览生成区不纳入约定摘要，避免“刚写通过就让自己失效”。证据与源码、测试或约定不匹配时显示需重验；历史原结论保留。

`证据匹配` 只表示在声明范围内记录/摘要/种类/覆盖匹配，不认证命令执行过、断言充分、业务正确或批准真实。运行证据应由已有测试工具/独立 CI 产生；该工具不自动采集任何供应商的日志。仅有哈希不能防止同权限的伪造。

## 命令

以下从 ThinStack 仓库运行；只安装技能时使用安装位置下的同名 scripts 路径。

```text
python skills/ts-code/scripts/project_state.py doctor --root "项目目录" --json
python skills/ts-code/scripts/project_state.py sync --root "项目目录"
python skills/ts-code/scripts/project_state.py sync --root "项目目录" --write
python skills/ts-code/scripts/project_state.py doctor --root "项目目录" --require-verified S-001
```

`doctor` 只读；`sync` 默认展示差异；`sync --write` 显式刷新。可用 `--expect <doctor的snapshot_sha256>` 要求与先前检查一致。写入使用协作锁、源文件复核和临时文件替换；能发现常见并发变化，但不是对任意外部写入的事务或恶意攻击安全边界。崩溃遗留锁时先确认无进程写入，再人工处理，不自动删除未知锁。

退出码：0=声明范围结构/一致性检查通过；1=检测到问题（包括总览过期）；2=配置/读写/格式失败。不代表产品 GREEN。`--require-verified ID` 可重复，只检查明确指定的交付片；未验证的未来计划本身不应阻止当前片。

证据失效时允许同步出诚实的“需重验”视图，但检查仍失败。编号/结构歧义时拒绝发布不完整总览。不自动修改阶段、升级权限、删除记录、访问网络或运行测试。

## 一致性与安全边界

检查本地文件死链；常见 Markdown 标题及显式 HTML 锚点可以识别，无法确认的锚点产生警告。复杂 Markdown、远程链接、自然语言业务矛盾未被认证。推荐关键引用用显式锚点和真实版本。

把 doctor 放到客户软件项目的 CI/交接检查，而不是仅检查 ThinStack 自身。需要强制放行时配置必需检查和受控来源，保护验证器、验收标准及工作流配置，不允许执行代理绕过分支规则。安装本工具不会自动更改仓库权限。高风险仍需独立审查；客户分享材料须脱敏。

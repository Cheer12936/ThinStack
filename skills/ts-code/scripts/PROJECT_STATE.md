# 项目检查与总览同步（可选接入）

`project_state.py` 是交付记录与一致性工具，不是安装器，不执行档案中的命令，不测试业务，也不能证明报告真实。`doctor` 只读，`sync` 默认预览；`sync --write` 只刷新总览生成区。获得项目建档授权后，`add` 可一次建立最小切片档案、登记路径并刷新总览，不替用户编造业务规则或批准。

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
python skills/ts-code/scripts/project_state.py add --root "项目目录" --title "导出客户对账单" --goal "财务人员能导出指定客户的未收款明细" --module reporting --depends-on S-001 --acceptance "导出内容与查询结果一致" --evidence-kind runtime
python skills/ts-code/scripts/project_state.py doctor --root "项目目录" --json
python skills/ts-code/scripts/project_state.py sync --root "项目目录"
python skills/ts-code/scripts/project_state.py sync --root "项目目录" --write
python skills/ts-code/scripts/project_state.py doctor --root "项目目录" --require-verified S-001
```

`add` 是显式写入动作，需要 `--title`、`--goal` 和 `--module`。首次使用会建立统一的 `docs/SLICES.md`、`docs/architecture/BASELINE.md`、`.thinstack.json` 和 `docs/slices/S-001.md`；未配置但发现 root/docs 中的 `slice.md`、`SLICES.md`、`BASELINE.md`、`ARCHITECTURAL_BASELINE.md`、`SPEC.md`、`RUN.md` 或已有 `docs/slices/*.md` 时停止，要求显式适配路径，不创建平行入口。检测是有界的已知入口检查，不保证发现任意命名的外部任务系统。验收目标可以暂空；一旦使用 `--acceptance`，必须用可重复的 `--evidence-kind` 明确允许的证据种类。`--approval-state approved` 必须同时给出真实 `--approval-source`。新项目仍从 S-001 开始；旧项目只有一个明确数字后缀序列时沿用前缀与补零宽度（如 TASK-009 → TASK-010），取消编号也计入。多个序列或无数字后缀时要求 `--id` 显式指定未使用编号，不改旧档案。沿用唯一的既有档案目录；多个目录时要求 `--record-dir` 指定本次目标。它们只是旧布局歧义的出口，不是按项目大小选择模式。依赖须已登记。

未来片的 `baseline_refs` 默认为空，不把新建基线模板视为已确认规则。轮到实施时由代理核对并绑定实际相关的基线；登记时确需绑定，可重复传 `--baseline <已登记相对路径>`，只绑定所选文件，不能指定尚未建立的模板。既有记录的绑定和证据不会被批量清空。机器块是阶段、依赖、批准、正式验收的唯一可编辑来源，正文仅记录目标、理由、设计与历史；旧文档不会被自动清理或迁移。

`doctor` 只读；`sync` 默认展示差异；`sync --write` 显式刷新。可用 `--expect <doctor的snapshot_sha256>` 要求与先前检查一致。`add` 与 `sync --write` 共用 `.thinstack-sync.lock`，登记在读取来源和分配编号前取锁，并尊重旧 `.thinstack-add.lock`。写入前复核来源与目标；回滚只撤销本操作尝试写入且字节仍匹配的文件。检测到他人改动时不覆盖，保留现场并报告恢复冲突；不要在未核对残留配置/档案前盲目重试。崩溃可能留下锁或部分文件，先确认无写入进程再人工恢复；不自动删除未知锁，也不把协作锁声称为针对任意进程的完整事务。

退出码：0=声明范围结构/一致性检查通过；1=检测到问题（包括总览过期）；2=配置/读写/格式失败。`add` 的 0 仅表示登记完成，JSON 中 `project_result` 另列整项检查状态；后续交付仍运行 doctor。不代表产品 GREEN。`--require-verified ID` 可重复，只检查明确指定的交付片；未验证的未来计划本身不应阻止当前片。

证据失效时允许同步出诚实的“需重验”视图，但检查仍失败。编号/结构歧义时拒绝发布不完整总览。除明确调用 `add` 外，不创建档案；任何动作都不自动修改既有阶段、升级权限、删除记录、访问网络或运行测试。

## 一致性与安全边界

检查本地文件死链；常见 Markdown 标题及显式 HTML 锚点可以识别，无法确认的锚点产生警告。复杂 Markdown、远程链接、自然语言业务矛盾未被认证。推荐关键引用用显式锚点和真实版本。

把 doctor 放到客户软件项目的 CI/交接检查，而不是仅检查 ThinStack 自身。需要强制放行时配置必需检查和受控来源，保护验证器、验收标准及工作流配置，不允许执行代理绕过分支规则。安装本工具不会自动更改仓库权限。高风险仍需独立审查；客户分享材料须脱敏。

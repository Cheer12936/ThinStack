# 最小多组评测执行框架

此目录提供可执行框架，不宣称已证明 ThinStack 优于裸模型。默认不调用任何模型、读取凭据或发生 API 费用。

## 任务与对照

`cases.py` 内置 7 个小型可复现任务：折扣 Bug、优惠券本地迁移未执行、模糊财会初始化、库存业务行为、纯函数权限边界、跨会话恢复、缺少真实联调条件。迁移夹具只验证“补跑已有本地迁移并停止”，不是生产数据库演练；权限夹具也不代表整个 HTTP/生产权限系统。

默认每题三组：bare（不加载技能）、autonomous（当前技能默认自主）、guided（同一技能明确引导）。真实版本比较可用 `--arm-config` 指向不可变 Skill 快照，例如 bare / alpha.11 / v0.3.0 / candidate；同一组只改变 Skill 快照或引导模式。参考文件仅对加载技能组提供，全新工作目录隔离每次任务，固定随机种子混排顺序。

每题默认运行 1 次；默认三组使用 `--repeats 3` 得到 7×3×3=63 次，四版本对照得到 7×4×3=84 次。运行前固定模型、推理档位、工具权限、环境、用户回答和外部总预算，并控制全局技能/宿主指令污染；不要强行让每组都执行相同诊断步数。交互题最多 4 轮，固定用户事实回复，不编造无限访谈。

## 无模型自测

```text
python -B evals/harness/run.py selftest --output /新目录/harness-selftest --repeats 3
```

运行正控制（硬编码参考实现/问答）和负控制（不解决问题却宣称 complete）。默认 `repeats=3` 共 126 次控制试验。输出必须标记 `HARNESS_SELFTEST_NOT_MODEL_BENCHMARK`；它验证判分链路，不是模型成绩。不得用其正例通过率宣传模型成功率或技能收益。

## 接入真实模型代理

代理必须能读取/修改 workspace，并遵循请求文件与响应文件协议。运行的是用户明确配置的外部可执行程序，不用 shell 展开命令，不预设模型品牌。

适配器配置示例（绝对路径须替换为本机实际位置）：

```json
{
  "kind": "model",
  "model_label": "实际模型、推理档位与代理版本",
  "argv": ["python", "/absolute/path/to/adapter.py", "{request}", "{response}"]
}
```

支持 stdin 文本、stdout 单个 JSON 的已有代理，可复用 `stdio_adapter.py`：argv 在该脚本、两个路径占位符后追加 `--` 和真实代理命令。供应商流式事件协议应由对应适配器转为下述响应，不要猜最后一行。该桥接器不提供编码工具、不发模型 API 请求，仍需本机已有并授权的模型代理。

仓库提供 `codex_cli_adapter.py` 和 `response-schema.json` 作为 Codex CLI 实例。它使用临时会话、忽略用户配置/执行规则、自动审批的 workspace-write 沙盒，并保存 JSONL 事件和 CLI 报告的真实用量。它不是 OS 隔离；当前 CLI 的 `skip_host_skill_discovery` 必须用 `codex debug prompt-input` 验证，正式版本对照还需在运行前排除全局同名 Skill，否则 bare 组会被污染。

适配器配置可写为：

```json
{
  "kind": "model",
  "model_label": "gpt-6-astra medium via codex-cli",
  "argv": ["python", "/absolute/path/codex_cli_adapter.py", "{request}", "{response}", "--model", "gpt-6-astra", "--thinking", "medium"]
}
```

```text
python -B evals/harness/run.py run --adapter /本机/model-adapter.json --arm-config /本机/four-versions.json --ack-execution --output /新目录/model-eval --repeats 3
```

版本配置只接受本地不可变快照目录，不从运行中的分支名称重新解析：

```json
{
  "schema_version": 1,
  "arms": [
    {"name":"bare","skill_root":null,"mode":"autonomous"},
    {"name":"alpha11","skill_root":"/snapshots/alpha11/ts-code","mode":"autonomous"},
    {"name":"v030","skill_root":"/snapshots/v030/ts-code","mode":"autonomous"},
    {"name":"candidate","skill_root":"/snapshots/candidate/ts-code","mode":"autonomous"}
  ]
}
```

`--ack-execution` 确认外部命令及潜在费用；不是沙箱。不要在生产目录、有秘密的环境或具有生产凭据的进程中评测不可信代理。使用宿主/容器限制文件、网络、CPU、内存和子进程；工作目录隔离不阻止恶意代理访问其他路径。Windows 超时默认终止顶层进程，完整进程树隔离由宿主承担。

请求 JSON 包括 case_id、arm、workspace、prompt、skill_root、history、answers、response_path。响应为：

```json
{"status":"complete","message":"实际完成或阻塞说明","questions":[],"usage":null}
```

需要问用户时 status=`question`，questions 填 `[{"topic":"business_goal","text":"具体问题"}]` 或 ownership/other。初始化题的既定事实分别对应业务目标和组织归属；topic 是机械评分辅助，不证明文字问得合理。环境缺失时如实 blocked，不能把没执行算 complete。真实 usage 填适配器实际计量；未知保留 null，不由字节或时间推算。原始工具轨迹应由实际适配器保存到 trial 目录；本框架未获得时 tool_call_count 为 null。

## 结果与评分限制

每次保留初始/最终文件摘要、完整提示与对话、外部程序 stdout/stderr/退出码/耗时、独立夹具检查输出、变更文件和范围差异、结构化结果。summary 按组汇总机械验收、无依据宣称完成、明确越界路径、不必要阻塞、耗时中位数、最长耗时和最多提问数。Token 只使用适配器实际计量；模型标识与用量来自操作者/适配器，框架不认证后端实际路由。

数值任务用框架在候选工作区外保存的固定断言检查；不相信代理自己的“通过”总结。初始化与缺凭据任务的机械检查仅覆盖部分行为，始终保留 `semantic_review=NOT_REVIEWED`，需要独立人员检查问题质量、是否真正解决了歧义和总结是否准确。既测错误，也测不必要阻塞；不要把修改行数或提问次数直接当质量分。

当前框架不提供对恶意代理的独立安全裁判，候选与评分进程在同一 OS 权限下仍可能相互影响。真实研究应把评分环境隔离并固定评分代码。测试案例公开，模型可能针对案例过拟合；推广结论需额外留出任务及重复试验。框架运行成功只表示记录完成，不表示模型任务全部通过。

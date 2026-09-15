# 可选机器证据记录

用途：防止遗失日志、使用选定文件的过期结果、遗漏已列出的验收项，或将失败/跳过项标成 GREEN。不是业务测试，也不是独立裁判。

仅交付任务需要这种记录时使用；普通小修复不强制写 JSON。`NOT_GREEN` 是诚实的未证实状态，结构有效不会把它转换成 GREEN。

```json
{
  "schema_version": 1,
  "scope": "Slice 1：回访筛选",
  "verdict": "NOT_GREEN",
  "required": ["AC-1"],
  "snapshot": {},
  "checks": [],
  "unresolved_high_risks": ["缺少实际权限边界验证"]
}
```

获得真实证据后：snapshot 填写受影响来源文件相对路径与实际 SHA256；checks 中每项含 covers（required 的 ID 数组）、status（pass/fail/skipped）、method（命令或观察方式）、observed_at、environment。pass/fail 项还须有 artifact（相对项目路径）与 sha256。不要复制或伪造摘要。

只列当前范围的活动检查；历史失败另存。修复后实际重新执行才可更新，不通过删除必要标准获得 GREEN。路径必须留在项目根目录内，不接受符号链接。记录不包含凭据或真实个人信息。

```text
python skills/ts-code/scripts/check_evidence.py 你的证据记录.json --root "被验证的项目目录"
```

退出码：0 表示记录结构与摘要有效，1 表示检查不通过，2 表示文件/参数解析错误。输出 RECORD_VALID 不等于产品 GREEN；工具不会执行 method，不会判断日志是否伪造、断言是否充分、来源快照是否完整，也不会监控模型能力。

真实执行记录最好由项目测试工具/持续集成产生；人工或可信外部检查仍需判断需求与断言是否一致。仅把文件内容加哈希不能让它变成可信事实。

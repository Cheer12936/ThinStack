# 项目级接入（可选，不全局接管）

公共安装默认仍显式调用 `$ts-code`（Claude Code 通常为 `/ts-code`）。用户明确选择某项目使用 ThinStack 后，才为该项目采用宿主支持的项目配置；不把整份技能粘贴进 AGENTS.md / CLAUDE.md，也不为一个项目放开全局副本。

Codex 会从当前目录向上到仓库根扫描 `.agents/skills`。项目采用时安装同一份正文，只改该副本的调用策略：

```text
python tools/manage.py install --skills-dir "项目目录/.agents/skills" --invocation project --project-root "项目目录"
```

公共目录省略 `--invocation`，保持显式调用。更新默认保留目标副本已有策略；如需明确收回项目自动匹配，可在更新时使用 `--invocation explicit`。安装器要求项目型目录精确为 `<project>/.agents/skills`，防止误把全局副本改成隐式调用。

## 最小入口片段

将下述片段合并到项目已有指令文件，替换技能位置与项目总览路径，不覆盖其他规则：

```text
本项目已由维护者选择使用 ThinStack。
正式开发、切片设计与续做使用已安装的 ts-code；一般问答/解释不加载。
项目总览：docs/SLICES.md（已有其他入口则写实际路径）。
优先通过宿主支持的技能调用加载；不可调用时明确说明，不声称已经加载。
恢复只读当前片及相关基线；机器档案已接入时，交接前运行 project_state.py doctor。
只读检查不写项目；sync --write 仍遵循用户本次建档授权。
```

AGENTS.md/CLAUDE.md 只放入口、项目命令和约束，不复制参考文档。项目选择不自动授权生产写入、付费调用、部署、清理或跳过批准。

## 宿主差异与验证

- 仓库标准运行包 `agents/openai.yaml` 保持 `allow_implicit_invocation: false`。`--invocation project` 只把明确目标的 `.agents/skills/ts-code` 副本设为 `true`。Codex 路径与隔离还需用实际宿主记录验证；其他宿主使用它们正式支持的项目机制。
- Claude Code 官方通过技能 frontmatter 的 `disable-model-invocation` 控制自动调用；`agents/openai.yaml` 不是它的统一权限设置。我们的默认描述要求明确启用；需要仅手动调用时在该项目副本采用宿主开关；需要项目自动调用时检查该副本与 Skill 工具权限。不要把一个宿主的字段抄给另一个宿主。
- 安装器不写 hook、不覆盖项目指令、不修改仓库权限；自动调用是否生效仍须通过实际调用记录验证。

在本机做五个烟雾检查：普通代码解释不加载；明确 ts-code 调用加载；已启用项目的正式开发按约定加载；其他项目不受影响；更新后项目副本仍保留调用策略。通过宿主日志/技能调用记录核对，不能只相信模型口头“已使用”。

v0.3.1 已在 Windows、Codex CLI `0.155.0-alpha.9.2`、`gpt-6-astra` medium 上执行一次这组检查：正式库存方案任务的原始轨迹显示读取项目副本 `SKILL.md`、`proposal.md` 与 `clarify.md`；普通 Python 解释未读取；另一项目未发现该副本；更新后策略和发现均保留。这是当前宿主的有界观察，不是其他版本或宿主的保证。

## 客户项目 CI

安装包检查和客户软件检查是两回事。采用机读档案后，在客户项目的 CI 中调用固定版本的 project_state.py doctor；需要交付某片时加 `--require-verified <编号>`，不把未来待做片全设为必需。同步是单独的显式动作，CI 默认只读。

检查器、验收内容及工作流需受审查和权限保护；同权限代理能改程序和证据时不能保证不可绕过。接入文档不自动设置分支保护。只检查版本、哈希与声明范围，真实业务测试仍要运行；人工记录的部署/客户验收不等于外部平台认证。

## 官方参考（核对日期 2026-09-20）
- OpenAI 项目指令：https://learn.chatgpt.com/docs/agent-configuration/agents-md
- OpenAI 技能文档：https://learn.chatgpt.com/docs/build-skills
- Claude Code 技能与调用控制：https://code.claude.com/docs/en/skills

文档可能更新；以实际客户端可用设置为准。英文介绍可另行维护，但运行规则保持一份中文权威版本。

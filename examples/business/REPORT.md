# Notes.create 验证报告

模式 DELIVERY；工作类型 SLICE；Design LIGHT / Verification STANDARD；profiles DATABASE、CRUD。

## 契约

目标：完成现有 Notes.create(text)，返回新记录整数 ID。
验收：非空白字符串原样保存；空白字符串抛 ValueError，非字符串抛 TypeError，两者均不新增行；独立实例能读取已提交记录；list 按 ID 升序。
约束：保留原表结构、list 接口、已有 test_app.py 测试，不改其他目录。
最小充分证明：既有空列表测试，加真实文件 SQLite 集成测试覆盖上述全部行为及已有记录不受拒绝请求影响；不需浏览器、外部服务或重复单元测试。
深度理由：接口和表结构已明确，无架构变更；保存事务和跨连接可见性必须用真实数据库证明，因此验证为 STANDARD。

## 证据

GREEN：2026-09-08 00:22 +08:00，Windows / PowerShell / Python 3.12.5，真实 SQLite 文件。

所有命令的工作目录均为本报告所在 business 目录。首次执行先创建 `.tmp`（`New-Item -ItemType Directory -Path '.tmp' -Force`）。测试命令如下；首次日志为 red.log，最终为 green.log：

```powershell
$env:TEMP = (Resolve-Path '.tmp').Path
$env:TMP = $env:TEMP
$env:PYTHONIOENCODING = 'utf-8' # 最终运行添加
python -B -m unittest discover -v 2>&1 | Tee-Object -FilePath 'green.log'
exit $LASTEXITCODE
```

- 初次 red.log：退出 1，4 个测试，15 个 error。新用例暴露 NotImplementedError；既有及新用例还暴露数据库连接未关闭造成 WinError 32，不能把整次失败统称为纯行为 RED。
- 最终 green.log：退出 0，4 个测试全部通过，0.091 秒。原 test_app.py 原样保留。
- `test_empty`：既有空库列表及上下文退出清理通过。
- `test_preserves_text_returns_id_and_commits_for_new_instance`：含首尾空白、中文、换行、SQL 形状文本及重复文本，原文保留；返回正整数且不同记录 ID 唯一；新实例读取一致且按 ID 升序。
- `test_blank_strings_rejected_without_changing_rows`：4 类空白拒绝，跨实例确认已有记录不变。
- `test_non_strings_rejected_without_changing_rows`：9 类非字符串拒绝，跨实例确认数据库没有新增行。

这些真实持久化断言共同证明请求验收及 list 消费端兼容性；没有 mock 替代数据库。

## 实现与范围

app.py 的 create 在任何数据库操作前验证类型及空白，以参数化 SQL 保存原文，在事务提交后向调用者返回 ID。另用 closing 修复构造、创建、列表连接的释放：sqlite3 的事务上下文并不自动关闭连接，这是初次测试发现的真实生命周期缺陷；未改表结构或 list 返回格式。新增 test_create.py；test_app.py 未修改。失败运行留下的临时数据库仅在本目录，未接触外部数据。

## 被测快照

执行 `Get-Date -Format o; python --version; Get-FileHash -Algorithm SHA256 -LiteralPath 'app.py','test_app.py','test_create.py' | Format-List | Out-String`：时间 2026-09-08T00:22:06.2952599+08:00，Python 3.12.5。

- app.py：2B5C81DBABA4551BEFB90F2FE4CFE894D68720805877DFA562A2790B97963F91
- test_app.py：D6912C58C510230DFD4AFCFFCAF6DD909864613D6884A27587CB77A0BCCCF7FB
- test_create.py：3AC92E434C3113AE491D239E9BC0E8970A0FA271CFEE69860C7F6F7A731BB744

源码与测试在最终运行后没有修改。报告是用户指定的唯一契约/结果载体，不另建重复 SPEC/RUN。

## 局限与剩余工作

剩余：本次验收范围内无。未验证多进程并发、磁盘故障或其他数据库后端；本次未改变这些行为，也不宣称已验证。没有网络调用、业务系统操作或主技能/ERP修改。

实际读取技能文件：SKILL.md、references/database.md、references/verification.md、references/checkpoint-resume.md、references/final-report.md。未加载其他技能。

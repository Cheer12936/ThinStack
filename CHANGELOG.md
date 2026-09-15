# Changelog

## 0.2.0 — 2026-09-15

### 初始化追问与设计边界后续更新 — 2026-09-15

- 初始化先核对影响架构与跨片依赖的业务、组织/数据、权限、外部接口及实际运行约束；重要未知深入追问，已有充分答案复用，不把未来全部实现前置。
- Grill 以正常行为、适用失败示例与不做的反例检查共识；保留决策依赖、一问一答、具体选项和有限停止，不新增审批或外部技能依赖。
- 基线和切片按需明确模块对外操作、规则归属、隐藏复杂性与失败行为；不以文件大小代替模块质量。
- TDD 强调稳定行为边界与设计反馈；保留内部单元测试及必要真实风险证据，不把测试先行仅当弱模型辅助。
- 明确允许有当前事实依据、授权范围内的最小局部整理及回归保护；禁止借机扩展业务、改契约或在验收后启动架构审计。生产/数据授权和 GREEN 证据底线不放宽。
- 总览与切片交付先展示可操作结果、实际运行证据、环境和局限；不新增自动进度后台、完成判定器或文档体系。
- 更新运行包摘要和使用说明；新增 12 个 NOT_RUN 设计行为场景，与工具测试区分。版本保持 0.2.0，以提交标识本次更新。

### 项目记忆后续更新 — 2026-09-15

- 新增项目总览模板；显式项目建档、新项目或新业务计划确认后建立/更新统一总览和每片持久入口，沿用已有 slice.md / SLICES.md，不创建重复总表。
- 明确登记与设计的区别：未来片仅记目标/依赖/状态，当前片实施前才细化；新增业务、独立技术结果及重要契约变化按需设计，普通修复与续做不重做规划。
- 扩展任务模板为永久切片档案；完成和取消后保留历史，状态先在档案更新，再汇总到总览，基线保持长期规则的唯一来源。
- 执行阶段、阻塞、验证有效性、客户验收和部署分开记录；不把切片数量占比冒充工期完成率，不新增后台自动汇总服务。
- 只设计/只读、一次确认、生产操作与风险证据边界不变。项目记忆行为场景另列为 NOT_RUN；包结构/现有工具回归不代表模型行为评测。

- 保留 FAST_FIX / PROJECT_INIT / SLICE 与独立 LIGHT / STANDARD / FULL；用户默认看到中文工作方式和实际结果，而不是固定档位播报。
- 共用薄核心，加入按需自主/引导模式；模式根据用户选择、任务评测或实际失控信号切换，不绑定模型品牌，也不声称能检测服务端降级。
- 保留薄基线和当前验收约定的持久化，记录为什么改及模块职责；取消统一文件名/READY 标签作为普遍开工门槛，已有编号和文档不迁移。
- 增加按需行为追问、TDD 与风险证据参考；移除固定三次诊断和所有功能默认完整章节要求。旧 16 份运行参考整合为 5 份。
- 授权不放宽：新项目/新功能默认确认一次；已有同一方案批准可复用；只审查、生产写入、破坏性操作与付费调用的边界保留。
- GREEN 的当前范围和必要证据底线保留，强化验证不要求固定测试层数；引导模式不能削弱验收、测试或安全。
- 宿主默认关闭隐式触发；完整替换运行包，继续用原安装/备份工具，不残留旧参考规则。
- 增加可选机器证据记录检查器和回归测试；仅检查记录/摘要，不证明业务正确、真实执行或模型稳定性。
- VERSION 为版本来源；包校验检查简化元数据、实际引用、UTF-8 字节预算与运行包 SHA256。摘要清单范围改为 skills/ts-code，不再覆盖历史演示和仓库文档。
- 提供 12 个 NOT_RUN 模型评测场景；实际本地测试与待测模型效果分开记录，不声明 Token、速度或跨模型成功率提升。

## 0.1.0-alpha.11 — 2026-09-09

- One canonical docs/SLICES.md per project; stable consecutive Slice N names across modules, requests and sessions.
- Registry links goals, status, dependencies, design and evidence; legacy IDs map without rewriting historical files.
- No cancelled-ID reuse or per-module inventories; FAST_FIX does not create new slices or registry scaffolding.


## 0.1.0-alpha.10 — 2026-09-09

- FAST_FIX is a LIGHT/LIGHT work type with at most 3 high-discrimination diagnostic steps, persistent count, frozen repair scope and mandatory stopping after scoped proof passes.
- Replace one-way escalation with evidence-based recalibration; lower depths need no user approval when risk assumptions are disproved. Actual applicable proof floors remain binding.
- Separate authoring production migrations from locally applying unchanged existing migrations with bounded target/backup/execution/function evidence.
- GREEN covers the current repair promise, not nearby modules or the full project roadmap; speculative risks cannot accumulate verification scope.


## 0.1.0-alpha.9 — 2026-09-09

- Add explicit FAST_FIX versus PLANNED_CHANGE routing before templates or document creation.
- Local bugs start with 1–2 high-information diagnostics; expand only to resolve evidence-backed uncertainty or wider impact.
- Prohibit opportunistic refactoring, general audits, planning scaffolds and unrelated verification for fast fixes.
- Discovered data/security/architecture risks activate relevant full analysis/proof while preserving existing valid plans and approvals.


## 0.1.0-alpha.8 — 2026-09-09

- Require a confirmed persisted relevant baseline before new business-slice implementation.
- Existing projects must derive/supplement baseline claims from actual code, tests, schema/migrations and configuration.
- Separate observed, verified, proposed and unknown claims; code defects are not approved rules.
- Retain narrow local-fix and read-only exceptions, and combine baseline/slice approval when appropriate.


## 0.1.0-alpha.7 — 2026-09-08

- Restore substantive spec-to-design-style baseline and slice proposal formats before plan approval.
- Require concrete rules, acceptance, domain/schema/API/state deltas, UI flow, compatibility and traceable proof in the visible proposal.
- Keep lightweight Green Contract as a summary, not a replacement for design.
- Preserve one-time confirmation, current-slice-only detailed design, existing file layouts and concise local fixes.


## 0.1.0-alpha.6 — 2026-09-08

- Make slice planning, meaningful progress transitions and per-slice final accounting consistently visible.
- Keep tiny fixes concise and reuse the existing one-time approval; design/review modes retain their boundaries.
- Add a suggested entry prompt and usage guidance without new workflow gates.


## 0.1.0-alpha.5 — 2026-09-08

- Require a visible business-outcome slice map for multi-outcome requests before plan approval.
- Detail only the current slice; preserve small/atomic changes without artificial splitting.
- Approval of a mapped multi-slice scope permits continuous in-scope execution without per-slice confirmation.
- Track slice states and prerequisites; overall GREEN requires all requested slices and relevant integration evidence.


## 0.1.0-alpha.4 — 2026-09-08

- Authorization behavior change: new projects and new business features show a concise concrete plan and wait for one confirmation before implementation.
- Local understood fixes remain direct; the same already-approved plan or an explicit instruction to skip confirmation avoids duplicate approval.
- Approval covers continuous in-scope implementation and verification; pending confirmation survives resume.
- No new repeated stage gates, test-layer requirements or reduced evidence floors.


## 0.1.0-alpha.3 — 2026-09-08

- Rename the display name, folder and invocation from thinslack-code to ts-code.
- Update installation tools and documentation; behavior and quality gates unchanged.
- Archive earlier installations after installing ts-code to avoid duplicate active rules.


## 0.1.0-alpha.2 — 2026-09-08

- Rename the displayed skill to Thinslack-Code and its folder/invocation to thinslack-code.
- Update installation tooling, validation and usage examples. Repository name remains ThinStack.
- No workflow, permission or verification-floor changes. Archive the previous slice-to-green installation after installing the new name; historical reports and copyright notices remain unchanged.


## 0.1.0-alpha.1 — 2026-09-08

- Single self-contained skill; removed separate design/test entrypoints from the distribution.
- Project initialization and slice delivery distinguished from design-only/verification-only/implementation scope.
- Independent design and verification depths, risk override floors and evidence-based GREEN.
- Clarified that high failure cost raises verification without automatically requiring full architecture design.
- Scope-appropriate reports for design/review; no fabricated delivery verdict.
- Explicit-target installer with backups; portable structural checks; isolated runnable evaluations.

This alpha changes invocation names and removes legacy compatibility entrypoints. Existing project documentation is preserved. Downgrade rules, risk floors and authorization boundaries must be called out in later changes.

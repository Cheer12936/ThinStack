# ThinStack

**ThinStack：一个轻量的 AI 编码工作框架。内置唯一技能 ts-code，用于初始化项目、设计、实现和验证业务切片。**

An adaptive skill for project initialization, design, implementation and verification. Independent design/verification depths; no mandatory test-layer ladder. English skill instructions, Chinese quickstart.

版本：`0.1.0-alpha.3`（试用版）。默认只安装 `skills/ts-code`，无需其他技能、插件或在线服务。

## 使用

在支持显式技能调用的客户端中输入 `$ts-code`，或明确说“使用 ts-code”。宿主是否自动触发技能取决于客户端支持；不要假定所有环境一致。

- 初始化：“用 ts-code 初始化一个库存项目。先确定最小基线并搭建可运行基础，首期只做商品和库存查询。”
- 完成切片：“用 ts-code 增加按名称搜索，空查询、分页和已有权限保持不变。”
- 只设计：“用 ts-code 只设计跨门店权限，先不实现。”
- 只测试：“用 ts-code 审查测试覆盖，暂时不写测试或改产品代码。”

PROJECT_INIT/SLICE 决定工作对象；DESIGN_ONLY/VERIFY_ONLY/DELIVERY 决定授权范围。LIGHT/STANDARD/FULL 分别用于设计与验证深度，不能扩大授权。

新项目通常先建立一份架构基线；普通切片默认 SPEC.md + RUN.md，小修复可以只在对话中记录。已有项目继续使用现有文档，不强制迁移或重搭工程。

## 安装、更新、卸载

先获取仓库：

```text
git clone https://github.com/Cheer12936/ThinStack.git
cd ThinStack
```

需要 Python 3.10+ 才能运行下面的可选工具；技能本身不依赖 Python。先从你的客户端配置或官方文档确认技能目录。工具不会猜测路径或修改客户端配置。

```text
python tools/manage.py install --skills-dir "你的客户端技能目录"
python tools/manage.py update --skills-dir "你的客户端技能目录"
python tools/manage.py uninstall --skills-dir "你的客户端技能目录"
```

也可以把 `skills/ts-code` 整个文件夹手动复制到客户端发现目录。不要只复制 SKILL.md。刷新技能列表或开启新任务后核对已识别的名称。

install 遇到已有同名目录会拒绝覆盖；update 先把旧目录归档到技能目录旁的备份目录；uninstall 也只归档而不删除。工具输出准确备份位置，恢复时将归档目录复制回原技能目录。工具不会移除其他技能或旧兼容入口。

从旧版升级：本版统一使用 `ts-code`；旧名称为 `slice-to-green` 和 `thinslack-code`。先安装新名称，再将旧技能目录移出发现目录；不要同时保留两套活动规则。安装工具不会自动改动旧目录。新版本不再提供 spec-to-design / spec-to-tests。确认主技能安装成功后，可自行归档旧入口；将旧调用改为“ts-code 只设计/只测试”。新技能全部内部引用自包含。

## 工作方式

目标和现有约束 → 双深度与风险判断 → 简短 Green Contract → 自主实现/验证/修复 → 按证据报告。

Green Contract 包含目标、验收条件、约束和必需证据。选择证明这些条件的最小充分检查集合；权限、迁移、金额等风险具有验证下限。只有验收被证明、必需检查通过、无已知回归及未解决高风险发现时，完整交付才可声明 GREEN。

**质量门目前是模型指令，不是程序强制拦截器。**结构校验脚本只查发布包完整性，不能判断测试是否充分，也不能保证安全、生产就绪或零错误。只设计/只审查不冒充实现完成；缺必需访问或数据时必须如实说明未验证。

## 环境与验证范围

- 本地已验证环境：Windows PowerShell、Python 3.12、Codex 工具环境中的技能读取与隔离演示，见 [评估报告](evals/README.md)。
- Linux/macOS、其他客户端、其他模型：尚未完成实机兼容验证。
- agents/openai.yaml 是可选宿主元数据；核心指令采用 [Agent Skills 结构](https://agentskills.io/specification)。其他宿主可能忽略这份元数据。
- 客户端安装与识别请参考其当前官方文档，例如 [OpenAI 技能文档](https://learn.chatgpt.com/docs/build-skills)；本文不把目录发现行为当作跨产品保证。

## 维护

```text
python tools/validate.py
python -m unittest discover -s tests -v
```

参见 [更新记录](CHANGELOG.md)、[贡献方式](CONTRIBUTING.md)、[安全与反馈](SECURITY.md)、[来源说明](PROVENANCE.md)。仓库文档和演示不属于运行时技能上下文，不要把整个发布仓库放进技能发现目录。

MIT License。项目仓库：[Cheer12936/ThinStack](https://github.com/Cheer12936/ThinStack)。技能调用名称保持 `ts-code`。

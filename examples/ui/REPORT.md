# UI slice 实作验证

**GREEN** · 2026-09-08 00:22–00:27 Asia/Shanghai

## 契约与深度

DELIVERY / SLICE；Design LIGHT、Verification LIGHT、Profile UI。现有独立演示页只有局部样式改变，没有新架构或业务规则。修改前已以可见消息记录契约。

目标：预约按钮左右 padding 从 12px 改为 16px。验收/约束：上下仍为 8px，其他代码及点击结果不变；代表性 desktop/mobile 显示完整，点击后显示 Selected。

充分证明：唯一 CSS 替换 + 浏览器计算样式 + 两个视口真实点击 + 截图观察。没有新建测试套件或重复全层测试。

## 实作与验证

[index.html](index.html) 唯一产品改动：`padding:8px 12px` → `padding:8px 16px`。执行替换前断言旧声明仅出现一次，其余源码由原字符串保留。

环境：Windows，已安装 Chrome，经现有缓存 Playwright CLI 0.1.19 自动化；无依赖安装。临时 Python HTTP 服务仅绑定 127.0.0.1:18764。

操作：

1. `python -m http.server 18764 --bind 127.0.0.1`，cwd 为本目录。
2. 现有 CLI 的 `-s=alpha-ui open http://127.0.0.1:18764 --browser chrome`。
3. `resize 1440 900` → `snapshot` → 对新鲜 button ref 读取 computed style 并断言 → `screenshot` → `click` → 断言 status 为 Selected → `screenshot`。
4. `resize 390 844` → `reload` → 新 `snapshot`，以新 ref 重复相同验证。
5. `close` 关闭自己的浏览器；Ctrl+C 结束自己的服务器；`Get-NetTCPConnection -LocalPort 18764 -State Listen` 确认不再监听。

实际命令产生的 Playwright 操作、断言函数、结果及关闭记录见 [operations.log](output/playwright/operations.log)。

| 证据 | Desktop 1440×900 | Mobile viewport 390×844 |
|---|---|---|
| padding 上/右/下/左 | 8px / 16px / 8px / 16px，PASS | 同左，PASS |
| 文档横向溢出 | 无，PASS | 无，PASS |
| 初始结果 | 空字符串，PASS | 刷新后为空，PASS |
| 浏览器实际点击 | Selected，PASS | Selected，PASS |
| 按钮尺寸 | 139.46875×31 CSS px | 139.46875×31 CSS px |

截图已通过图像查看工具实际检查：两个视口标题、按钮文字均完整单行；按钮没有截断或遮挡；点击后 Selected 在按钮下方正常显示，无横向溢出。

- [desktop.png](output/playwright/desktop.png)
- [desktop-selected.png](output/playwright/desktop-selected.png)
- [mobile.png](output/playwright/mobile.png)
- [mobile-selected.png](output/playwright/mobile-selected.png)

测试产物对应 index.html SHA256：
`9D099261015CC1E1D91D6B2678A4D45DB74D5E3EED7415E225EF3567788AA999`

## 局限与剩余

mobile 是 Chrome 的代表性 CSS viewport 检查，不是实体手机或跨浏览器认证。初始加载出现一次 /favicon.ico 404，原始演示文件未定义 favicon；与修改无关，刷新后的控制台为 0 errors/0 warnings，未将该请求声称通过。不涉及后台预约或持久化。

所需证据已取得，无已知相关回归或未解决高风险项；剩余工作：无。自己的临时服务器和浏览器均已关闭。仅改变本目录下 index.html、此报告以及浏览器证据产物；没有编辑 ERP、主技能或其他评估报告。

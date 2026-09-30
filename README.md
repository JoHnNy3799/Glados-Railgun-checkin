# Glados自动签到

## 食用方式：

### 注册一个GLaDOS的账号([注册地址](https://glados.space/landing/0A58E-NV28S-6U3QV-33VMG))

#### 我的邀请码：([0A58E-NV28S-6U3QV-33VMG](https://0a58e-nv28s-6u3qv-33vmg.glados.space)) 

#### 我的优惠码（9折）：([DEVILSTORE](https://0a58e-nv28s-6u3qv-33vmg.glados.space)) 

### **Fork**本仓库

![图片加载失败](imgs/1.png)

### 添加**secret**

1. 跳转至自己的仓库的`Settings`->`Secrets and variables`->`Action`

2. 添加1个`repository secret`，命名为`GLADOS_COOKIES`，其值对应GLaDOS账号的cookie值中的有效部分（获取方式如下）

- 在GLaDOS的签到页面按`F12`

- 切换到`Network`页面下，刷新

![图片加载失败](imgs/2.png)

- 点击第一个选项卡后在`Request Headers`下找到`Cookie`，右键复制cookie的值即可

  > 参考格式：koa:sess=eyJ1c2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxAwMH0=; koa:sess.sig=xJkOxxxxxxxxxxxxxxxtnM;

![图片加载失败](imgs/3.png)

- 多账号请在 `COOKIES` 中 添加多个 `cookies` 中间使用 `&`连接即可。（例如： `c1&c3&c3...`）

3. 配置积分兑换策略（非必须）

- 添加1个`repository secret`，命名为`GLADOS_EXCHANGE_PLAN`，配置自动兑换积分策略：

| 值 | 积分要求 | 兑换天数 |
|---|---------|---------|
| `plan100` | 100 积分 | 10 天 |
| `plan200` | 200 积分 | 30 天 |
| `plan500` | 500 积分 | 100 天 |

> 不配置时默认不进行自动兑换；如需兑换，设置 `GLADOS_EXCHANGE_PLAN` 为 `plan100` / `plan200` / `plan500`。

4. 手机推送（非必须）

- 添加1个`repository secret`，命名为`PUSHDEER_SENDKEY`，其值对应 PushDeer key: ([获取地址](https://www.pushdeer.com/product.html))。

### **star**自己的仓库

![图片加载失败](imgs/4.png)

## 文件结构

```shell
│  checkin.py	# 签到脚本
│
├─.github
│  └─workflows
│          gladosCheck.yml	# Actions 配置文件
```

## 更新日志

- **2026-01**: 重构代码，添加log输出方便定位，支持新版网址，支持配置积分兑换策略。
- **2026-04**: 优化代码逻辑，优化日志输出，支持[新版域名](https://railgun.info) ，在 GLADOS_COOKIES 中添加新版域名下的 cookies 即可使用。
- **2026-09**: 新增设备平台自适应重试（code 4 无需手动配置 UA 即可自动恢复）；默认关闭自动兑换，需显式配置 `GLADOS_EXCHANGE_PLAN` 才启用。
- **2026-09**: 新增网络层重试/退避：`requests.Session` 挂载 `HTTPAdapter` + `urllib3.Retry`（total=3、指数退避 1/2/4s、对 429/5xx 自动重试），降低 CI 网络抖动导致的误报失败；业务 200 响应不受影响。
- **2026-09**: 修复“job 绿了但一次都没签到”的静默失败——**存在真实签到失败时进程以非 0 退出码结束，Actions 会把 run 标红**；签到总结与推送通知中直接带出服务端返回的失败原因（如「没有权限」），不再只显示「签到失败」四个字。
- **2026-09**: 修复 cookie 与域名的笛卡尔积误报——同一个 cookie 若只在部分域名有效，其余域名会被标记为「跳过」而非「失败」，只有当该 cookie 在**所有**域名上都认证失败时才计为真实失败（说明 cookie 本身失效）。同时补充 cookie 失效时的排查提示、新增 `requirements.txt`、`pypushdeer` 缺失时不再阻塞签到本身。


## 问题排查与定位
- 大家可以通过查询 actions 中的 running checkin 日志快速定位问题，有其他问题提交issue。
- **run 显示红叉（失败）**：说明本次运行存在真实签到失败，日志末尾的「签到总结」会写明每个任务的失败原因。
- 若日志出现 `code : -2, message : 没有权限` / `No permission`：**cookie 已失效或复制不完整**。请在 glados.cloud 重新登录，打开签到页面按 `F12` → `Network` → 刷新 → 在 `Request Headers` 里复制**完整的** `Cookie` 值（必须同时包含 `koa:sess` 与 `koa:sess.sig` 两段），更新到 `GLADOS_COOKIES` secret。多账号用 `&` 连接。
- 若日志出现 `code : 4, message : Automated check-in detected`：这是 GLaDOS 的**设备平台校验**（`reason=device-mismatch`，即签到请求 UA 平台与登录设备平台不一致）。脚本已内置**设备平台自适应**：首次失败时自动读取服务端返回的 `loginDevice` 并切换对应平台 UA 重试，**无需手动配置 User-Agent**；若长期仍失败，请重新登录 glados.cloud 手动签到一次并刷新 cookie。

  <img width="1684" height="844" alt="image" src="https://github.com/user-attachments/assets/45348a5f-43e4-45f5-8fdf-ce84d343b30d" />

## 声明

本项目基于 [Devilstore/Glados-Railgun-checkin](https://github.com/Devilstore/Glados-Railgun-checkin) 修改，遵循 **GPL-3.0** 许可证（原项目的版权声明与许可证文件予以保留）。README 中原有的注册邀请码与优惠码同样来自原项目。

本项目不保证稳定运行与更新, 因GitHub相关规定可能会删库, 请注意备份








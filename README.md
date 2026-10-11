# BleBridgeMcp

**blebridge 的 MCP（Model Context Protocol）服务器独立发行包** —— 把
[nRF52840 BLE 全透传双角色桥](https://github.com/andy-qingcai/ble_bridge_nrf52840)
的完整工具面交给 AI 客户端（Claude 等）：扫描 / 连接 / 服务发现 / GATT 读写 /
订阅 notify / MTU-连接参数-PHY 调优 / SMP 配对 / 外设广播与本地（含动态定义）
GATT 服务 / SUOTA 固件升级应用流程。

- 固件不含任何应用层专用逻辑，只做可靠的协议执行；全部智能在上位机
  `blebridge` Python 包，本包把它的 daemon 命令面以 MCP tool 形式一对一透出。
- **零硬件 sim 后端**：`open(backend="sim")` 使用内置行为模型
  （完整 0xFEF5 SUOTA 会话模型 + 桥级罐头应答），不插任何硬件即可端到端跑通
  全部工具 —— 适合安装后立即冒烟、CI 与 AI 客户端联调。
- 真硬件：`open(backend="serial", port=...)` 连接 nRF52840 DK 桥固件
  （USB CDC / UART 帧协议）。

## 安装

```bash
pip install .            # 本仓库检出
# 或
pip install blebridge-mcp
```

入口：`blebridge-mcp`（stdio transport）。

## MCP 客户端注册示例

```json
{
  "mcpServers": {
    "blebridge": {
      "command": "blebridge-mcp",
      "args": []
    }
  }
}
```

## 工具面（摘要）

| 类别 | 工具 |
|---|---|
| 链路 | `open`(serial/sim)、`close`、`ping`、`info`、`drain`、`events` |
| central | `scan_start`/`scan_stop`、`connect`、`disconnect`、`mtu`、`conn_update`、`phy`、`pair`、`sec` |
| GATT | `disc_svc`、`read`、`write`、`subscribe`、`unsubscribe`（uuid16 与原始 handle 双寻址） |
| 外设 | `adv_start`、`adv_stop`、`notify`、`set_char`、`gatt_define` |
| SUOTA 应用流程 | `suota_start`（上传合成/真实镜像）、`suota_abort`、`suota_status` |
| 逃生口 | `raw`（任意桥协议命令）、`log_level`、`reset`、`list_serial_ports` |

全部工具返回 JSON 字符串（unstructured），`ok=false` 时带人话错误。

## 快速冒烟（无需硬件）

```bash
python -m pytest tests/ -q        # 内置 sim 冒烟：open(sim) → ping → scan → SUOTA 全流程
```

或手动驱动：

```python
from blebridge.mcp_server import run_tool
run_tool("open", backend="sim")
print(run_tool("ping"))
print(run_tool("scan_start", duration_ms=200))
print(run_tool("close"))
```

## 与主仓库的关系

- 主仓库 `ble_bridge_nrf52840`：nRF52840 桥固件 + host 包 + CLI/daemon/MCP 全量。
- 本仓库：只发行 MCP 服务器（含完整 `blebridge` host 库与 sim 行为模型），
  面向 AI 工具集成场景的最小安装面。
- 协议契约见主仓库 `docs/protocol-contract.md`；SUOTA 为 Dialog/Renesas 公开
  协议（AN-B-022）。

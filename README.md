# 🦞 longbridge-trader

> An [OpenClaw](https://github.com/openclaw/openclaw) agent skill that lets your AI assistant trade HK/US stocks through [Longbridge Open API](https://open.longbridge.com) — using plain Chinese or English.

```
你：帮我买100股腾讯，价格395港元
AI：✅ 限价买单已提交 — 700.HK × 100 @ HKD 395.00 | 订单号: 1213xxxxxxxxx
```

---

## ✨ Features

| 功能 | 说明 |
|------|------|
| 🗣️ **自然语言下单** | 说中文就能买卖，无需记命令 |
| 📊 **实时报价** | 查港股/美股实时价格 |
| 💼 **账户管理** | 查余额、持仓、历史订单 |
| 🔒 **安全确认** | 下单前强制二次确认，防误操作 |
| 🧪 **Dry-run 模式** | `--dry-run` 参数模拟下单，不实际提交 |
| 🌏 **港股 + 美股** | 同时支持 `.HK` 和 `.US` 市场 |

---

## 🚀 Quick Start

### 1. 安装依赖

```bash
pip install longport
```

### 2. 配置 API 凭证

在 [长桥开发者中心](https://open.longbridge.com) 完成认证后，将凭证写入 `.env`：

```bash
cp .env.example .env
# 编辑 .env，填入你的 APP_KEY / APP_SECRET / ACCESS_TOKEN
```

或直接运行交互式配置向导：

```bash
python scripts/setup.py
```

### 3. 测试连通性

```bash
python scripts/quote.py 700.HK AAPL.US
```

---

## 💬 Natural Language Usage (via OpenClaw)

当 AI 收到自然语言指令时，自动调用 `lb.py` 统一入口：

```bash
# 买卖
python scripts/lb.py "买入100股腾讯，价格395"
python scripts/lb.py "卖出50股 BLSH.US，价格33.5"
python scripts/lb.py "买入400股小米，价格31.8港元"

# 行情
python scripts/lb.py "查一下苹果和特斯拉的股价"
python scripts/lb.py "700.HK 现在多少钱"

# 账户
python scripts/lb.py "看看我的持仓"
python scripts/lb.py "查账户余额"
python scripts/lb.py "今日订单"
```

### 支持的中文股票名称

| 中文 | 代码 | 中文 | 代码 |
|------|------|------|------|
| 腾讯 | 700.HK | 苹果 | AAPL.US |
| 阿里巴巴 | 9988.HK | 特斯拉 | TSLA.US |
| 美团 | 3690.HK | 英伟达 | NVDA.US |
| 小米 | 1810.HK | 微软 | MSFT.US |
| 京东 | 9618.HK | 谷歌 | GOOGL.US |
| 比亚迪 | 1211.HK | 亚马逊 | AMZN.US |

---

## 🛠️ Direct Script Usage

### 📈 实时报价

```bash
python scripts/quote.py 700.HK AAPL.US TSLA.US
```

```
700.HK   腾讯控股   HKD 395.00  ▲+2.30 (+0.59%)
AAPL.US  Apple Inc  USD 227.50  ▲+1.20 (+0.53%)
```

### 💰 账户余额

```bash
python scripts/account_balance.py
python scripts/account_balance.py --currency USD
```

### 📋 持仓查询

```bash
python scripts/stock_positions.py
python scripts/stock_positions.py 700.HK  # 查特定标的
```

### 🛒 下单

```bash
# 港股限价买入
python scripts/trade.py buy 700.HK 100 --price 395.0

# 美股限价买入
python scripts/trade.py buy AAPL.US 10 --price 227.0

# 美股市价买入
python scripts/trade.py buy AAPL.US 5 --market

# 卖出
python scripts/trade.py sell 700.HK 100 --price 400.0

# 试运行（不实际下单）
python scripts/trade.py buy 700.HK 100 --price 395.0 --dry-run
```

### 📑 订单管理

```bash
python scripts/orders.py today          # 今日订单
python scripts/orders.py history        # 历史订单
python scripts/orders.py cancel <id>    # 撤单
```

---

## 📁 Project Structure

```
longbridge-trader/
├── SKILL.md                  # OpenClaw skill descriptor
├── .env.example              # 环境变量模板
└── scripts/
    ├── lb.py                 # 🤖 自然语言入口（AI 调用此文件）
    ├── trade.py              # 下单（买入/卖出）
    ├── quote.py              # 实时报价
    ├── account_balance.py    # 账户余额
    ├── stock_positions.py    # 持仓查询
    ├── orders.py             # 订单管理
    ├── setup.py              # 配置向导
    └── _env.py               # 环境变量加载
```

---

## 📦 Order Types

| 类型 | 说明 | 适用市场 |
|------|------|----------|
| LO | 限价单 | 港股 / 美股 |
| MO | 市价单 | 仅美股 |
| ELO | 增强限价单 | 港股 |
| ALO | 碎股单 | 港股 |

---

## ⚠️ Safety

- 所有买卖操作**强制二次确认**（内置，不可绕过）
- 建议先用 `--dry-run` 验证参数
- API 凭证**只存在 `.env` 文件**，不硬编码，`.env` 已加入 `.gitignore`
- 不建议在无人监督场景下自动批量执行交易

---

## 🔧 Requirements

- Python 3.8+
- `longport` SDK (`pip install longport`)
- 长桥证券账户 + [Open API 权限](https://open.longbridge.com)

---

## 📄 License

MIT — 随意用，后果自负，股市有风险 📉

---

> Built with ❤️ as an [OpenClaw](https://github.com/openclaw/openclaw) agent skill.  
> OpenClaw lets your AI assistant control your apps, files, and services — including your brokerage.

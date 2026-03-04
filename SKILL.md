# longbridge-trader Skill

自动操作长桥（Longbridge）证券账户买卖港股/美股的 skill。

## 触发条件

当用户提到以下内容时激活：
- 买入/卖出股票（港股/美股）
- 查询账户余额、持仓
- 查询股票实时报价
- 撤单、查询今日/历史订单
- 关键词：长桥、Longbridge、港股、美股买卖、下单、持仓、账户余额

## 首次配置

```bash
# 1. 安装 SDK
pip install longport

# 2. 运行配置向导（交互式输入 API 凭证）
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/setup.py
```

或手动设置环境变量：
```bash
export LONGPORT_APP_KEY="从长桥开发者中心获取"
export LONGPORT_APP_SECRET="从长桥开发者中心获取"
export LONGPORT_ACCESS_TOKEN="从长桥开发者中心获取"
```

> 在 https://open.longbridge.com 完成开发者认证后获取。

---

## AI 使用方式（推荐）

当用户说自然语言时，使用 `lb.py` 统一入口：

```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/lb.py "买入100股腾讯，价格50"
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/lb.py "查一下苹果和特斯拉的股价"
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/lb.py "看看我的持仓"
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/lb.py "卖出10股AAPL，价格180"
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/lb.py "查账户余额"
```

### 支持的中文股票名称

| 中文名 | 代码 |
|--------|------|
| 腾讯 | 700.HK |
| 阿里巴巴 | 9988.HK |
| 美团 | 3690.HK |
| 小米 | 1810.HK |
| 京东 | 9618.HK |
| 苹果 | AAPL.US |
| 特斯拉 | TSLA.US |
| 英伟达 | NVDA.US |
| 微软 | MSFT.US |

---

## 直接调用脚本

### 查询报价
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/quote.py 700.HK AAPL.US TSLA.US
```

### 查账户余额
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/account_balance.py
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/account_balance.py --currency USD
```

### 查持仓
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/stock_positions.py
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/stock_positions.py 700.HK AAPL.US
```

### 限价买入
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/trade.py buy 700.HK 100 --price 50.0
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/trade.py buy AAPL.US 10 --price 180.0
```

### 限价卖出
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/trade.py sell 700.HK 100 --price 55.0
```

### 市价买入（仅美股）
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/trade.py buy AAPL.US 5 --market
```

### 试运行（不实际下单）
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/trade.py buy 700.HK 100 --price 50.0 --dry-run
```

### 查今日订单
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/orders.py today
```

### 查历史订单
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/orders.py history
```

### 撤单
```bash
python ~/.openclaw/workspace/skills/longbridge-trader/scripts/orders.py cancel <order_id>
```

---

## AI 操作流程

当收到用户自然语言指令时：

1. **解析意图**：买入 / 卖出 / 查报价 / 查持仓 / 查余额 / 撤单
2. **确认参数**：
   - 股票代码（带后缀 `.HK` 或 `.US`）
   - 数量（股数）
   - 价格（限价单必填；港股没有市价单，美股有）
3. **高风险操作前显示摘要并要求二次确认**（脚本内置确认步骤）
4. **执行脚本**并展示返回结果
5. **解读结果**：帮用户理解成交/失败原因

## 订单类型参考

| 类型 | 说明 | 适用 |
|------|------|------|
| LO | 限价单 | 港股/美股 |
| MO | 市价单 | 仅美股 |
| ELO | 增强限价单 | 港股 |
| SLO | 特别限价单 | 港股 |
| ALO | 碎股单 | 港股 |

## ⚠️ 安全原则

- 买卖操作**必须**让用户二次确认（脚本内置，不可绕过）
- 建议先通过 `--dry-run` 测试参数正确性
- 不要在无人监督的情况下批量或自动执行交易
- API 凭证不要硬编码在脚本中，使用环境变量

#!/usr/bin/env python3
"""
长桥交易助手 - 统一入口
支持自然语言解析（供 AI 调用）

用法:
  python lb.py "买入100股腾讯，价格50港元"
  python lb.py "查一下苹果和特斯拉的股价"
  python lb.py "看看我的持仓"
  python lb.py "查账户余额"
  python lb.py "卖出10股AAPL，价格180美元"
"""
import sys
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _env import load_env; load_env()
import os
import re
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

# 常见股票名称映射
STOCK_ALIASES = {
    '腾讯': '700.HK', '阿里': '9988.HK', '阿里巴巴': '9988.HK',
    '美团': '3690.HK', '小米': '1810.HK', '京东': '9618.HK',
    '百度': 'BIDU.US', '网易': 'NTES.US', '苹果': 'AAPL.US',
    '特斯拉': 'TSLA.US', '英伟达': 'NVDA.US', '微软': 'MSFT.US',
    '谷歌': 'GOOGL.US', '亚马逊': 'AMZN.US', 'Meta': 'META.US',
    '比亚迪': '1211.HK', '中国平安': '2318.HK', '工商银行': '1398.HK',
    '建设银行': '939.HK', '中国移动': '941.HK',
}

def resolve_symbol(text):
    """将中文名/代码解析为标准格式"""
    # 中文名映射
    for name, symbol in STOCK_ALIASES.items():
        if name in text:
            return symbol
    # 已有后缀
    m = re.search(r'([A-Z0-9]{1,6})\.(HK|US|SZ|SH)', text.upper())
    if m:
        return m.group(0)
    # 纯数字（港股）
    m = re.search(r'\b(\d{1,5})\b', text)
    if m:
        return f"{m.group(1)}.HK"
    # 纯字母（美股）
    m = re.search(r'\b([A-Z]{1,5})\b', text.upper())
    if m:
        return f"{m.group(1)}.US"
    return None

def run(cmd, **kwargs):
    """执行子命令"""
    result = subprocess.run(
        [sys.executable] + cmd,
        cwd=str(SCRIPTS_DIR),
        **kwargs
    )
    return result.returncode

def parse_and_execute(text):
    """解析自然语言并执行"""
    text_lower = text.lower()

    # 查报价
    if any(k in text for k in ['报价', '股价', '价格', '多少钱', '现价', 'quote']):
        # 提取所有可能的股票
        symbols = []
        for name, sym in STOCK_ALIASES.items():
            if name in text:
                symbols.append(sym)
        # 正则匹配代码
        for m in re.finditer(r'[A-Z]{1,6}\.(?:HK|US)', text.upper()):
            symbols.append(m.group(0))
        if not symbols:
            sym = resolve_symbol(text)
            if sym:
                symbols.append(sym)
        if symbols:
            return run([str(SCRIPTS_DIR / 'quote.py')] + list(set(symbols)))
        else:
            print("❓ 未识别股票代码，请指定，如：查一下 AAPL.US 的股价")
            return 1

    # 查余额
    if any(k in text for k in ['余额', '账户', '资金', '买入力', 'balance']):
        return run([str(SCRIPTS_DIR / 'account_balance.py')])

    # 查持仓
    if any(k in text for k in ['持仓', '仓位', '我买了', '我有', 'positions']):
        return run([str(SCRIPTS_DIR / 'stock_positions.py')])

    # 查今日订单
    if any(k in text for k in ['今日订单', '今天订单', 'today order']):
        return run([str(SCRIPTS_DIR / 'orders.py'), 'today'])

    # 历史订单
    if any(k in text for k in ['历史订单', '历史记录', 'history order']):
        return run([str(SCRIPTS_DIR / 'orders.py'), 'history'])

    # 买入
    buy_match = any(k in text for k in ['买入', '买', '建仓', '加仓', 'buy'])
    sell_match = any(k in text for k in ['卖出', '卖', '平仓', '减仓', 'sell'])

    if buy_match or sell_match:
        symbol = resolve_symbol(text)
        if not symbol:
            print("❓ 未识别股票代码，请指定，如：买入100股 700.HK，价格50")
            return 1

        # 提取数量
        qty_match = re.search(r'(\d+)\s*(?:股|手|shares?)?', text)
        qty = int(qty_match.group(1)) if qty_match else None
        if not qty:
            print(f"❓ 未识别数量，请指定，如：{'买入' if buy_match else '卖出'}100股 {symbol}")
            return 1

        # 提取价格
        price_match = re.search(r'(?:价格?|@|=)\s*([\d.]+)', text)
        if not price_match:
            price_match = re.search(r'([\d.]+)\s*(?:港元|美元|元|HKD|USD)?', text[text.find(str(qty)):])

        side = 'buy' if buy_match else 'sell'
        cmd = [str(SCRIPTS_DIR / 'trade.py'), side, symbol, str(qty)]

        if price_match:
            cmd += ['--price', price_match.group(1)]
        else:
            # 港股不支持市价单，需要提示
            if symbol.endswith('.HK'):
                print(f"❓ 港股 {symbol} 不支持市价单，请指定价格")
                return 1
            cmd += ['--market']

        return run(cmd)

    # 默认帮助
    print(__doc__)
    return 0

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    text = ' '.join(sys.argv[1:])
    sys.exit(parse_and_execute(text))

if __name__ == '__main__':
    main()

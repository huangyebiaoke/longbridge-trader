#!/usr/bin/env python3
"""
长桥持仓查询
用法: python stock_positions.py [symbol ...]
示例: python stock_positions.py 700.HK AAPL.US
"""
import sys
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _env import load_env; load_env()
import argparse

def main():
    parser = argparse.ArgumentParser(description='查询长桥持仓')
    parser.add_argument('symbols', nargs='*', help='股票代码（不填则查全部）')
    args = parser.parse_args()

    try:
        from longport.openapi import TradeContext, Config
    except ImportError:
        print("❌ 未安装 longport，请运行: pip install longport")
        sys.exit(1)

    try:
        config = Config.from_env()
        ctx = TradeContext(config)

        kwargs = {}
        if args.symbols:
            kwargs['symbols'] = args.symbols

        resp = ctx.stock_positions(**kwargs)

        if not resp.channels:
            print("📭 暂无持仓")
            return

        print("✅ 当前持仓\n" + "="*60)
        total_market_value = 0
        for channel in resp.channels:
            print(f"账户: {channel.account_channel}")
            if not channel.positions:
                print("  (无持仓)")
                continue
            for pos in channel.positions:
                market_val = float(pos.market_value) if pos.market_value else 0
                cost = float(pos.cost_price) if pos.cost_price else 0
                current = float(pos.price) if pos.price else 0
                pnl = market_val - cost * float(pos.quantity) if cost > 0 else 0
                pnl_pct = (pnl / (cost * float(pos.quantity)) * 100) if cost > 0 else 0

                print(f"\n  📈 {pos.symbol} ({pos.symbol_name})")
                print(f"     持仓量:    {pos.quantity}")
                print(f"     可用量:    {pos.available_quantity}")
                print(f"     成本价:    {pos.cost_price}")
                print(f"     现价:      {pos.price}")
                print(f"     市值:      {pos.market_value}")
                pnl_str = f"{pnl:+.2f} ({pnl_pct:+.2f}%)"
                print(f"     盈亏:      {pnl_str}")
                total_market_value += market_val
        print(f"\n{'='*60}")
        print(f"总市值: {total_market_value:.2f}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

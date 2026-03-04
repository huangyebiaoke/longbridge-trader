#!/usr/bin/env python3
"""
长桥股票报价查询
用法: python quote.py AAPL.US 700.HK TSLA.US
"""
import sys
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _env import load_env; load_env()
import argparse

def main():
    parser = argparse.ArgumentParser(description='查询股票实时报价')
    parser.add_argument('symbols', nargs='+', help='股票代码，如 700.HK AAPL.US')
    args = parser.parse_args()

    try:
        from longport.openapi import Config, QuoteContext
    except ImportError:
        print("❌ 未安装 longport，请运行: pip install longport")
        sys.exit(1)

    try:
        config = Config.from_env()
        ctx = QuoteContext(config)
        resp = ctx.quote(args.symbols)

        print("✅ 实时报价\n" + "="*60)
        for q in resp:
            change = float(q.last_done) - float(q.prev_close) if q.prev_close else 0
            change_pct = (change / float(q.prev_close) * 100) if q.prev_close and float(q.prev_close) != 0 else 0
            change_str = f"{change:+.3f} ({change_pct:+.2f}%)"

            print(f"\n  {q.symbol}")
            print(f"     最新价:    {q.last_done}")
            print(f"     涨跌:      {change_str}")
            print(f"     开盘:      {q.open}")
            print(f"     最高:      {q.high}")
            print(f"     最低:      {q.low}")
            print(f"     昨收:      {q.prev_close}")
            print(f"     成交量:    {q.volume}")
            print(f"     成交额:    {q.turnover}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

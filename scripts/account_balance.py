#!/usr/bin/env python3
"""
长桥账户余额查询
用法: python account_balance.py [--currency HKD|USD|CNH]
"""
import sys
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _env import load_env; load_env()
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='查询长桥账户余额')
    parser.add_argument('--currency', choices=['HKD', 'USD', 'CNH'], help='货币类型')
    args = parser.parse_args()

    try:
        from longport.openapi import TradeContext, Config
    except ImportError:
        print("❌ 未安装 longport，请运行: pip install longport")
        sys.exit(1)

    try:
        config = Config.from_env()
        ctx = TradeContext(config)
        resp = ctx.account_balance(currency=args.currency)

        print("✅ 账户余额\n" + "="*50)
        for account in resp:
            print(f"币种: {account.currency}")
            print(f"  净资产:     {account.net_assets}")
            print(f"  买入力:     {account.buy_power}")
            print(f"  总现金:     {account.total_cash}")
            print(f"  风险等级:   {account.risk_level}")
            if hasattr(account, 'cash_infos') and account.cash_infos:
                for cash in account.cash_infos:
                    print(f"  [{cash.currency}] 可用: {cash.available_cash}  冻结: {cash.frozen_cash}  待交割: {cash.settling_cash}")
            print()
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

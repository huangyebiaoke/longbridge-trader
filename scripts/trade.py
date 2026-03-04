#!/usr/bin/env python3
"""
长桥下单脚本（买入/卖出）
用法:
  python trade.py buy  700.HK   100 --price 50.0     # 限价买入100股
  python trade.py sell AAPL.US  10  --price 180.0    # 限价卖出10股
  python trade.py buy  AAPL.US  5   --market          # 市价买入（港股不支持市价单）
  python trade.py buy  700.HK   100 --price 50.0 --dry-run  # 试运行（不实际下单）

订单类型:
  限价单 (LO): 指定 --price，港股/美股均支持
  市价单 (MO): 指定 --market，仅美股支持
"""
import sys
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _env import load_env; load_env()
import argparse
from decimal import Decimal

ORDER_TYPES = {
    'LO': '限价单',
    'MO': '市价单',
    'ELO': '增强限价单(港股)',
    'SLO': '特别限价单(港股)',
    'ALO': '碎股单(港股)',
    'MIT': '触及市价单',
    'LIT': '触及限价单',
}

def confirm(msg):
    """要求用户二次确认"""
    print(f"\n⚠️  {msg}")
    ans = input("确认执行？(输入 yes 继续，其他取消): ").strip().lower()
    return ans == 'yes'

def main():
    parser = argparse.ArgumentParser(description='长桥下单')
    parser.add_argument('side', choices=['buy', 'sell'], help='buy=买入 sell=卖出')
    parser.add_argument('symbol', help='股票代码，如 700.HK 或 AAPL.US')
    parser.add_argument('quantity', type=int, help='数量')
    parser.add_argument('--price', type=float, help='限价单价格')
    parser.add_argument('--market', action='store_true', help='使用市价单（仅美股）')
    parser.add_argument('--order-type', default=None, help='指定订单类型（默认：LO 或 MO）')
    parser.add_argument('--tif', choices=['Day', 'GTC', 'GTD'], default='Day', help='Time in force（默认 Day）')
    parser.add_argument('--remark', default='', help='备注')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不实际下单')
    args = parser.parse_args()

    # 参数校验
    if not args.market and args.price is None and args.order_type is None:
        print("❌ 错误：必须指定 --price（限价）或 --market（市价）")
        sys.exit(1)

    if args.quantity <= 0:
        print("❌ 错误：数量必须大于 0")
        sys.exit(1)

    try:
        from longport.openapi import TradeContext, Config, OrderType, OrderSide, TimeInForceType
    except ImportError:
        print("❌ 未安装 longport，请运行: pip install longport")
        sys.exit(1)

    # 确定订单类型
    if args.order_type:
        order_type_map = {
            'LO': OrderType.LO, 'MO': OrderType.MO,
            'ELO': OrderType.ELO, 'SLO': OrderType.SLO,
            'ALO': OrderType.ALO, 'MIT': OrderType.MIT,
            'LIT': OrderType.LIT,
        }
        if args.order_type not in order_type_map:
            print(f"❌ 未知订单类型: {args.order_type}，可选: {', '.join(order_type_map.keys())}")
            sys.exit(1)
        order_type = order_type_map[args.order_type]
        order_type_str = args.order_type
    elif args.market:
        order_type = OrderType.MO
        order_type_str = 'MO (市价单)'
    else:
        order_type = OrderType.LO
        order_type_str = 'LO (限价单)'

    # 确定方向
    side = OrderSide.Buy if args.side == 'buy' else OrderSide.Sell
    side_str = '🟢 买入' if args.side == 'buy' else '🔴 卖出'

    # 确定 TIF
    tif_map = {
        'Day': TimeInForceType.Day,
        'GTC': TimeInForceType.GoodTilCanceled,
        'GTD': TimeInForceType.GoodTilDate,
    }
    tif = tif_map[args.tif]

    # 打印订单信息
    print(f"\n{'='*50}")
    print(f"📋 待提交订单")
    print(f"{'='*50}")
    print(f"  方向:     {side_str}")
    print(f"  股票:     {args.symbol}")
    print(f"  数量:     {args.quantity}")
    if args.price:
        print(f"  价格:     {args.price}")
        est_value = args.price * args.quantity
        print(f"  预估金额: {est_value:.2f}")
    else:
        print(f"  价格:     市价")
    print(f"  类型:     {order_type_str}")
    print(f"  有效期:   {args.tif}")
    if args.remark:
        print(f"  备注:     {args.remark}")
    print(f"{'='*50}")

    if args.dry_run:
        print("\n✅ [试运行模式] 订单信息正常，未实际提交")
        return

    # 二次确认
    if not confirm(f"即将{'买入' if args.side == 'buy' else '卖出'} {args.quantity} 股 {args.symbol}"):
        print("❌ 已取消")
        return

    try:
        config = Config.from_env()
        ctx = TradeContext(config)

        kwargs = {
            'symbol': args.symbol,
            'order_type': order_type,
            'side': side,
            'submitted_quantity': Decimal(str(args.quantity)),
            'time_in_force': tif,
        }

        if args.price is not None:
            kwargs['submitted_price'] = Decimal(str(args.price))

        if args.remark:
            kwargs['remark'] = args.remark

        resp = ctx.submit_order(**kwargs)
        print(f"\n✅ 下单成功！")
        print(f"   订单ID: {resp.order_id}")

    except Exception as e:
        print(f"\n❌ 下单失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

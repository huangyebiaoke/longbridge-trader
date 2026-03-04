#!/usr/bin/env python3
"""
长桥订单查询与撤单
用法:
  python orders.py today              # 查今日订单
  python orders.py history            # 查历史订单
  python orders.py detail <order_id>  # 查订单详情
  python orders.py cancel <order_id>  # 撤单
"""
import sys
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _env import load_env; load_env()
import argparse

STATUS_MAP = {
    'NotReported': '未申报',
    'WaitToSubmit': '等待申报',
    'Submitted': '已申报',
    'RejectSubmit': '申报被拒',
    'AcceptedUnfilled': '已接受未成交',
    'PartialFilledActive': '部分成交活跃',
    'PartialFilledCancelled': '部分成交已撤',
    'Filled': '完全成交',
    'WaitToCancel': '等待撤单',
    'Cancelled': '已撤单',
    'Rejected': '已拒绝',
    'Expired': '已过期',
    'PartialWithdrawal': '部分撤单',
}

def fmt_status(s):
    return STATUS_MAP.get(str(s), str(s))

def print_order(order):
    print(f"\n  📄 {order.order_id}")
    print(f"     股票:   {order.symbol}")
    print(f"     方向:   {'🟢 买入' if str(order.side) == 'Buy' else '🔴 卖出'}")
    print(f"     类型:   {order.order_type}")
    print(f"     数量:   {order.quantity}")
    if hasattr(order, 'price') and order.price:
        print(f"     价格:   {order.price}")
    if hasattr(order, 'executed_quantity') and order.executed_quantity:
        print(f"     已成交: {order.executed_quantity}")
    if hasattr(order, 'executed_price') and order.executed_price:
        print(f"     成交价: {order.executed_price}")
    print(f"     状态:   {fmt_status(order.status)}")
    if hasattr(order, 'submitted_at') and order.submitted_at:
        print(f"     时间:   {order.submitted_at}")
    if hasattr(order, 'remark') and order.remark:
        print(f"     备注:   {order.remark}")

def main():
    parser = argparse.ArgumentParser(description='长桥订单管理')
    subparsers = parser.add_subparsers(dest='cmd', required=True)

    # today
    p_today = subparsers.add_parser('today', help='查今日订单')
    p_today.add_argument('--symbol', help='过滤股票代码')

    # history
    p_hist = subparsers.add_parser('history', help='查历史订单')
    p_hist.add_argument('--symbol', help='过滤股票代码')
    p_hist.add_argument('--side', choices=['buy', 'sell'], help='过滤方向')

    # detail
    p_detail = subparsers.add_parser('detail', help='查订单详情')
    p_detail.add_argument('order_id', help='订单ID')

    # cancel
    p_cancel = subparsers.add_parser('cancel', help='撤单')
    p_cancel.add_argument('order_id', help='订单ID')

    args = parser.parse_args()

    try:
        from longport.openapi import TradeContext, Config
    except ImportError:
        print("❌ 未安装 longport，请运行: pip install longport")
        sys.exit(1)

    try:
        config = Config.from_env()
        ctx = TradeContext(config)

        if args.cmd == 'today':
            kwargs = {}
            if args.symbol:
                kwargs['symbol'] = args.symbol
            resp = ctx.today_orders(**kwargs)
            if not resp:
                print("📭 今日暂无订单")
            else:
                print(f"✅ 今日订单（共 {len(resp)} 条）\n" + "="*60)
                for order in resp:
                    print_order(order)

        elif args.cmd == 'history':
            from longport.openapi import OrderSide, OrderStatus
            kwargs = {}
            if args.symbol:
                kwargs['symbol'] = args.symbol
            if args.side:
                kwargs['side'] = OrderSide.Buy if args.side == 'buy' else OrderSide.Sell
            resp = ctx.history_orders(**kwargs)
            if not resp:
                print("📭 暂无历史订单")
            else:
                print(f"✅ 历史订单（共 {len(resp)} 条）\n" + "="*60)
                for order in resp:
                    print_order(order)

        elif args.cmd == 'detail':
            resp = ctx.order_detail(order_id=args.order_id)
            print("✅ 订单详情\n" + "="*60)
            print_order(resp)

        elif args.cmd == 'cancel':
            # 先查询订单状态
            try:
                detail = ctx.order_detail(order_id=args.order_id)
                print(f"即将撤销订单:")
                print_order(detail)
            except:
                pass

            ans = input(f"\n确认撤销订单 {args.order_id}？(输入 yes 继续): ").strip().lower()
            if ans != 'yes':
                print("❌ 已取消")
                return

            ctx.cancel_order(order_id=args.order_id)
            print(f"✅ 撤单请求已提交：{args.order_id}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

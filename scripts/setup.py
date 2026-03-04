#!/usr/bin/env python3
"""
长桥 OpenAPI 配置向导
用法: python setup.py
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _env import load_env; load_env()
import os
import sys

def main():
    print("="*55)
    print("  长桥 OpenAPI 配置向导")
    print("  https://open.longbridge.com")
    print("="*55)

    # 检查 longport 是否安装
    try:
        import longport
        print(f"✅ longport 已安装 (版本: {longport.__version__})")
    except ImportError:
        print("📦 正在安装 longport...")
        os.system("pip install longport -q")
        try:
            import longport
            print(f"✅ longport 安装成功")
        except ImportError:
            print("❌ 安装失败，请手动运行: pip install longport")
            sys.exit(1)

    print("\n请输入你的长桥 OpenAPI 凭证")
    print("(在 https://open.longbridge.com 开发者中心获取)")
    print()

    # 读取现有配置
    current = {
        'LONGPORT_APP_KEY': os.environ.get('LONGPORT_APP_KEY', ''),
        'LONGPORT_APP_SECRET': os.environ.get('LONGPORT_APP_SECRET', ''),
        'LONGPORT_ACCESS_TOKEN': os.environ.get('LONGPORT_ACCESS_TOKEN', ''),
    }

    def prompt(key, label):
        cur = current.get(key, '')
        if cur:
            display = cur[:8] + '...' + cur[-4:] if len(cur) > 12 else cur
            val = input(f"  {label} (当前: {display}, 回车保留): ").strip()
            return val if val else cur
        else:
            return input(f"  {label}: ").strip()

    app_key = prompt('LONGPORT_APP_KEY', 'App Key    ')
    app_secret = prompt('LONGPORT_APP_SECRET', 'App Secret ')
    access_token = prompt('LONGPORT_ACCESS_TOKEN', 'Access Token')

    if not all([app_key, app_secret, access_token]):
        print("\n❌ 所有字段必填")
        sys.exit(1)

    # 写入 .env 文件
    env_file = os.path.join(os.path.dirname(__file__), '../.env')
    with open(env_file, 'w') as f:
        f.write(f"LONGPORT_APP_KEY={app_key}\n")
        f.write(f"LONGPORT_APP_SECRET={app_secret}\n")
        f.write(f"LONGPORT_ACCESS_TOKEN={access_token}\n")

    print(f"\n✅ 配置已保存到: {os.path.abspath(env_file)}")

    # 验证连接
    print("\n正在验证连接...")
    try:
        # 加载 .env
        os.environ['LONGPORT_APP_KEY'] = app_key
        os.environ['LONGPORT_APP_SECRET'] = app_secret
        os.environ['LONGPORT_ACCESS_TOKEN'] = access_token

        from longport.openapi import TradeContext, Config
        config = Config.from_env()
        ctx = TradeContext(config)
        resp = ctx.account_balance()
        print(f"✅ 连接成功！账户: {len(resp)} 个货币余额")
        for acc in resp:
            print(f"   {acc.currency}: 净资产 {acc.net_assets}，买入力 {acc.buy_power}")
    except Exception as e:
        print(f"⚠️  连接验证失败: {e}")
        print("   请检查凭证是否正确，或 API 权限是否开通")

    print("\n🎉 配置完成！现在可以使用长桥交易 skill 了")
    print("\n快速测试命令:")
    print(f"  python {os.path.dirname(__file__)}/account_balance.py")
    print(f"  python {os.path.dirname(__file__)}/quote.py 700.HK AAPL.US")

if __name__ == '__main__':
    main()

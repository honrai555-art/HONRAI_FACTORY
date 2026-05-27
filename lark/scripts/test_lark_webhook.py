#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lark Webhook テストスクリプト

Lark Incoming Webhook の設定が正しく機能しているかテストします。

使用方法:
    python test_lark_webhook.py

動作:
    1. Webhook URL の読み込み確認
    2. テスト通知を Lark に送信
    3. 送信成功の確認と結果表示

出力例（成功時）:
    ✅ Lark通知テスト成功
    Webhook URL: https://open.larksuite.com/...
    Message: HONRAI_FACTORY システム正常です

出力例（失敗時）:
    ❌ テスト失敗
    Reason: Webhook URL が見つかりません
"""

import sys
from pathlib import Path

# send_lark_notification.py と同じディレクトリ
sys.path.insert(0, str(Path(__file__).resolve().parent))

from send_lark_notification import send_notification, load_webhook_url


def test_lark_webhook():
    """Lark Webhook のテストを実行する"""
    
    print("=" * 60)
    print("🧪 Lark Webhook テスト")
    print("=" * 60)
    print()
    
    # Step 1: Webhook URL の読み込みテスト
    print("【ステップ 1】Webhook URL の読み込み確認...")
    try:
        webhook_url = load_webhook_url()
        # URL をマスク表示（セキュリティ対策）
        masked_url = webhook_url[:50] + "..." if len(webhook_url) > 50 else webhook_url
        print(f"✅ Webhook URL を読み込みました")
        print(f"   URL: {masked_url}")
    except RuntimeError as e:
        print(f"❌ Webhook URL が見つかりません")
        print(f"   {e}")
        print()
        return False
    
    print()
    
    # Step 2: テスト通知の送信
    print("【ステップ 2】テスト通知を送信中...")
    
    test_message = """✅ Lark通知テスト成功

システム: HONRAI_FACTORY
ステータス: 正常

テスト時刻: 現在時刻
メッセージ: Lark 連携が正常に機能しています

次のステップ:
- notification_templates.md から通知テンプレートを確認
- task_templates.md から依頼テンプレートを確認
- 実際の通知送信を試す

【参考】
- 通知スクリプト: python send_lark_notification.py "メッセージ"
- テンプレート: lark/templates/
"""
    
    success = send_notification(test_message)
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ Lark通知テスト成功")
        print()
        print("📋 次のステップ:")
        print("   1. notification_templates.md を確認")
        print("   2. task_templates.md を確認")
        print("   3. 以下のコマンドで本通知を送信:")
        print()
        print("   python send_lark_notification.py \\")
        print("     \"キャリアカード PDF が完成しました\"")
        print()
        print("=" * 60)
        return True
    else:
        print("❌ Lark通知テスト失敗")
        print()
        print("🔍 トラブルシューティング:")
        print("   1. Webhook URL が正しいか確認")
        print("   2. ネットワーク接続を確認")
        print("   3. Lark グループが存在するか確認")
        print("   4. logs/lark.log を確認")
        print()
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_lark_webhook()
    sys.exit(0 if success else 1)

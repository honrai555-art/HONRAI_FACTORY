#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lark 通知送信スクリプト

Lark Incoming Webhook を使用して、Lark グループチャットに通知を送信します。

使用方法:
    python send_lark_notification.py "通知内容"

設定:
    1. config/lark_config.json に webhook_url を設定、または
    2. 環境変数 LARK_WEBHOOK_URL を設定

例:
    # CLI から直接送信
    python send_lark_notification.py "キャリアカード PDF が完成しました"

    # Python スクリプトから呼び出し
    from send_lark_notification import send_notification
    send_notification("AI 分析が完了しました")
"""

import argparse
import json
import logging
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


# ログ設定
def setup_logging():
    """ログ設定を初期化する"""
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "lark.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    
    return logging.getLogger("lark_notification")


logger = setup_logging()


def load_webhook_url() -> str:
    """
    Lark Webhook URL を読み込む
    
    優先順位:
    1. 環境変数 LARK_WEBHOOK_URL
    2. config/lark_config.json の webhook_url
    3. なければエラー
    
    Returns:
        str: Lark Webhook URL
        
    Raises:
        RuntimeError: Webhook URL が見つからない場合
    """
    # 環境変数から読み込み
    webhook_url = os.getenv("LARK_WEBHOOK_URL", "").strip()
    if webhook_url:
        logger.debug("LARK_WEBHOOK_URL from environment variable")
        return webhook_url
    
    # config/lark_config.json から読み込み
    config_path = Path(__file__).resolve().parent.parent / "config" / "lark_config.json"
    
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            webhook_url = config.get("webhook_url", "").strip()
            if webhook_url:
                logger.debug(f"Loaded webhook_url from {config_path}")
                return webhook_url
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {config_path}: {e}")
        except Exception as e:
            logger.error(f"Error reading {config_path}: {e}")
    
    # エラー: Webhook URL が見つからない
    error_msg = (
        "❌ エラー: LARK_WEBHOOK_URL が設定されていません\n\n"
        "設定方法:\n"
        "1. 環境変数で設定:\n"
        "   set LARK_WEBHOOK_URL=https://open.larksuite.com/...\n\n"
        "2. または config/lark_config.json を作成:\n"
        f"   {config_path}\n"
        '   {{\n'
        '     "webhook_url": "https://open.larksuite.com/..."\n'
        '   }}\n\n'
        "Lark Webhook URL の取得方法:\n"
        "- Lark グループチャット → 設定 → 連携 → Incoming Webhook\n"
    )
    raise RuntimeError(error_msg)


def send_notification(message: str) -> bool:
    """
    Lark に通知を送信する
    
    Args:
        message (str): 送信するメッセージ本文
        
    Returns:
        bool: 送信成功時 True、失敗時 False
    """
    # Webhook URL を取得
    try:
        webhook_url = load_webhook_url()
    except RuntimeError as e:
        logger.error(str(e))
        print(str(e))
        return False
    
    # メッセージペイロードを構築
    payload = {
        "msg_type": "text",
        "content": {
            "text": message,
        }
    }
    
    # JSON に変換
    json_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    
    # リクエスト送信
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json_data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            response_body = response.read().decode("utf-8")
            response_data = json.loads(response_body)
            
            # レスポンス確認
            if response_data.get("code") == 0:
                logger.info(f"✅ 通知送信成功: {message[:50]}...")
                return True
            else:
                error_msg = response_data.get("msg", "Unknown error")
                logger.error(f"❌ Lark API エラー: {error_msg}")
                print(f"❌ エラー: {error_msg}")
                return False
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        logger.error(f"❌ HTTP エラー ({e.code}): {error_body}")
        print(f"❌ HTTP エラー: {e.code}")
        print(f"詳細: {error_body}")
        return False
        
    except urllib.error.URLError as e:
        logger.error(f"❌ ネットワークエラー: {e.reason}")
        print(f"❌ ネットワークエラー: {e.reason}")
        return False
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON デコードエラー: {e}")
        print(f"❌ レスポンス形式エラー: {e}")
        return False
        
    except Exception as e:
        logger.error(f"❌ 予期しないエラー: {e}")
        print(f"❌ エラー: {e}")
        return False


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="Lark Incoming Webhook を使用して通知を送信します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python send_lark_notification.py "通知内容"
  python send_lark_notification.py "キャリアカード PDF が完成しました"
        """,
    )
    
    parser.add_argument(
        "message",
        type=str,
        help="送信するメッセージ本文",
    )
    
    args = parser.parse_args()
    
    # 通知送信
    success = send_notification(args.message)
    
    # 終了コード
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

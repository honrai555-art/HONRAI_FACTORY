# Lark 連携 - HONRAI_FACTORY 製造ラインの管制塔

## 概要

Lark は HONRAI_FACTORY における **製造ラインの管制塔** としての役割を担います。データの本体はスプレッドシートやDBに保管し、Lark は **進捗確認・通知・依頼** に特化しています。

## Lark の役割

### ✅ Lark で同期するもの

| 項目 | 用途 | 頻度 |
|------|------|------|
| 通知・アラート | システムエラー、完了通知、開始通知 | リアルタイム |
| 進捗状況 | 各製造ラインの状態確認（漫画、ゲーム、3D等） | 1分～5分 |
| 依頼・タスク | アルバイトへの依頼、修正指示、確認依頼 | 都度 |
| 障害報告 | ComfyUI停止、GASエラー、Discord Bot停止等 | 都度 |

### ❌ Lark で同期しないもの

| 項目 | 理由 | 保管先 |
|------|------|--------|
| キャリアカード本データ | ファイルサイズが大きい | Google スプレッドシート |
| キャリアカード画像 | 数千個の画像を管理 | Google Drive + DB |
| 漫画原稿・フルPNG | 大量データ、バイナリ | output/manga + Google Drive |
| 3D素材・メタバースファイル | 大容量ファイル | models/ + GitHub LFS |
| ゲーム素材パック | ビルド成果物 | builds/ + GitHub Release |
| GAS スクリプト | コード管理 | GitHub (career-card-gas) |

## データフロー

### 1️⃣ キャリアカード診断フロー

```
Google フォーム（回答者）
    ↓ (自動転記)
Google スプレッドシート（回答DB）
    ↓ (Google Apps Script)
GPT API → プロンプト生成
    ↓
ComfyUI / Stable Diffusion（画像生成）
    ↓
SQLite DB（生成結果を記録）
    ↓
PDF 出力（google-python-client）
    ↓
📢 Lark 通知 → 「キャリアカード PDF が完成しました」
```

### 2️⃣ AI 漫画生成フロー

```
Discord: !manga コマンド
    ↓
Python スクリプト（gpt_manga_generate.py）
    ↓
GPT-4: ストーリープロット + キャラクター設定生成
    ↓
ComfyUI: イラスト生成（prompt拡張）
    ↓
output/manga に PNG/JSON 出力
    ↓
📢 Lark 通知 → 「漫画プロット生成が完了しました」
```

### 3️⃣ ゲーム素材生成フロー

```
Notion / Google ドキュメント（要件定義）
    ↓
ComfyUI / Blender（素材生成）
    ↓
builds/YYYYMMDD に素材パック出力
    ↓
📢 Lark 通知 → 「ゲーム素材生成が完了しました」
    ↓
Aさん（担当）に確認依頼
    ↓
Lark で承認 or 修正指示
```

### 4️⃣ メタバース制作フロー

```
Unity プロジェクト（unityprojects/）
    ↓
Discord: !unity コマンド で batchmode ビルド
    ↓
builds/ に WebGL/Standalone 出力
    ↓
📢 Lark 通知 → 「メタバース制作タスクが完了しました」
```

## アルバイト 3 名への依頼フロー

### Aさん（漫画セリフ確認担当）

```
📢 Lark 通知: 「新しい漫画が生成されました」
    ↓
Aさん: Google Drive / Notion で確認
    ↓
Aさん: セリフ確認・修正
    ↓
Lark で「✅ 確認完了」コメント
    ↓
自動的に次のステップへ
```

### Bさん（ゲーム素材整理担当）

```
📢 Lark 通知: 「素材パック XX が生成されました」
    ↓
Bさん: builds/YYYYMMDD で確認
    ↓
Bさん: 重複削除・フォルダ整理
    ↓
Lark で「✅ 整理完了」コメント
```

### Cさん（キャリアカード確認担当）

```
📢 Lark 通知: 「PDF出力が完了しました」
    ↓
Cさん: PDF をプレビュー確認
    ↓
レイアウト・内容チェック
    ↓
Lark で「✅ 確認完了」or「❌ 修正必要」
```

## エラー通知フロー

### 重大エラーの場合

```
ComfyUI 停止 / GAS エラー / Discord Bot 停止
    ↓
scripts/error_monitor.py が検知
    ↓
📢 Lark に RED エラー通知
    ↓
🔴 @channel mention で緊急通知
    ↓
logs/ にエラーログ保存
    ↓
自動修復スクリプト実行（可能な場合）
    ↓
修復結果を Lark に報告
```

### 軽微な警告の場合

```
API レート制限 / ファイル生成遅延
    ↓
📢 Lark に YELLOW 警告通知
    ↓
logs/ に記録
    ↓
手動対応が必要ならコメント依頼
```

## 週次報告フロー

毎週月曜 9:00（自動実行）

```
1. 生成実績の集計
   - 診断完了数
   - 漫画生成数
   - 素材生成数

2. CSV で Google スプレッドシート に保存

3. 📢 Lark に週次レポート投稿
   ```
   ✅ 週次レポート (2026-05-26)
   ├ キャリアカード: 12件生成 / 1件エラー
   ├ 漫画: 5話生成 / 100枚出力
   ├ 素材: 8パック生成 / 準備完了
   └ メタバース: ビルド2回 / 成功
   ```

4. アルバイトに共有
```

## 設定方法

### 1. Lark Incoming Webhook URL を取得

1. Lark グループチャットを作成（例: `HONRAI_FACTORY`）
2. チャット設定 → 連携 → 新しい連携を追加
3. 「Incoming Webhook」を選択
4. トークンをコピー

### 2. Webhook URL を保存

```bash
# (この後に Webhook URL を環境変数や設定ファイルに保存します)
```

## 追加ドキュメント

- `lark/base/manufacturing_line_base_schema.md`：製造ライン Base 設計
- `lark/base/manufacturing_line_base_sample.csv`：Base サンプルデータ
- `lark/base/status_master.csv`：ステータスマスタ
- `lark/docs/lark_integration_design.md`：Lark 連携設計
- `lark/rules/lark_notification_rules.md`：Lark 通知運用ルール
- `lark/rules/lark_docs_usage_rules.md`：Lark Docs 運用ルール

これらを参照し、Lark を製造ライン管制塔として活用してください。

### 2. Webhook URL を保存

```bash
# lark/config/lark_config.json
{
  "webhook_url": "https://open.larksuite.com/open-apis/bot/v2/hook/xxx..."
}
```

**⚠️ 重要**: `lark_config.json` は `.gitignore` に登録済み（GitHub に保存しない）

### 3. 環境変数で設定（推奨）

```bash
export LARK_WEBHOOK_URL="https://open.larksuite.com/open-apis/bot/v2/hook/xxx..."
```

## 使い方

### テスト通知を送る

```bash
python lark/scripts/test_lark_webhook.py
```

出力例：
```
✅ Lark通知テスト成功
Webhook URL: https://open.larksuite.com/...
Message: HONRAI_FACTORY システム正常です
```

### 通知を送る（手動）

```bash
python lark/scripts/send_lark_notification.py "キャリアカードPDFが出力されました。確認してください。"
```

### Python スクリプトから呼び出す

```python
from lark.scripts.send_lark_notification import send_notification

send_notification("AI分析が完了しました")
```

## トラブルシューティング

### Webhook URL が見つからない

```
❌ エラー: LARK_WEBHOOK_URL が設定されていません
解決策:
  1. lark/config/lark_config.json を作成
  2. または環境変数 LARK_WEBHOOK_URL を設定
```

### メッセージが送信されない

```
❌ エラー: Lark API エラー (xxx)
原因候補:
  - Webhook URL が不正
  - Lark グループが削除されている
  - ネットワーク接続エラー
→ logs/lark.log を確認
```

## ファイル構成

```
lark/
├── README.md                           # このファイル
├── templates/
│   ├── notification_templates.md       # 通知テンプレート集
│   └── task_templates.md               # 依頼テンプレート集
├── scripts/
│   ├── send_lark_notification.py       # 通知送信スクリプト
│   └── test_lark_webhook.py            # テストスクリプト
└── config/
    └── lark_config.example.json        # 設定ファイル（例）
```

---

**最終更新**: 2026-05-26  
**管理者**: HONRAI_FACTORY 運用チーム

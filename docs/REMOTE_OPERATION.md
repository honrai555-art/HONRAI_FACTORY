# HONRAI_FACTORY REMOTE OPERATION

## 目的

HONRAI_FACTORY を **スマホや外出先から操作・確認** するための手段を定義する。
主な経路は Discord Bot と Chrome Remote Desktop の 2 系統である。

---

# 操作経路

```
スマホ / 外出先
    │
    ├── Discord Bot ──────→ 工場コマンド実行・状態確認・通知
    │
    └── Chrome Remote Desktop ──→ PC 画面直接操作（Cursor / VSCode）
```

---

# Discord Bot

## 概要

| 項目 | 内容 |
|------|------|
| 実装 | `bot/factory_bot.py`（Python / discord.py） |
| 起動 | `python -m bot.factory_bot` または `run_factory_bot.ps1` |
| 設定 | `bot/.env` |
| ログ | `logs/bot.log`, `logs/bot_stdout.log`, `logs/bot_stderr.log` |

## 環境変数（bot/.env）

| 変数 | 用途 |
|------|------|
| `DISCORD_TOKEN` | Bot トークン（必須） |
| `ALLOWED_CHANNEL_ID` | コマンドを受け付けるチャンネル ID |
| `PROJECT_ROOT` | 工場ルートパス（git pull / スクリプト実行用） |
| `DISCORD_WEBHOOK_URL` | 漫画生成完了通知用 Webhook |

`.env.example` をコピーして作成する。`.env` は Git に commit しない。

## セットアップ

```powershell
cd C:\Users\honra\HONRAI_FACTORY\bot

python -m pip install -r requirements.txt

if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

## 起動

```powershell
# 通常起動
cd C:\Users\honra\HONRAI_FACTORY
python -m bot.factory_bot

# 常時起動（クラッシュ時に 5 秒後に自動再起動）
.\run_factory_bot.ps1
```

---

# コマンド一覧

指定チャンネル（`ALLOWED_CHANNEL_ID`）からのみ実行可能。

| コマンド | 説明 |
|----------|------|
| `!ping` | Bot 応答確認（レイテンシ表示） |
| `!status` | CPU / RAM / GPU、漫画・Unity ライン状態 |
| `!gitpull` | `PROJECT_ROOT` で git pull を実行 |
| `!manga` | 漫画出力監視スクリプトを起動 |
| `!comfy_test` | ComfyUI 最小テストを実行 |
| `!unity` | Unity ビルドスクリプトを起動 |
| `!logs` | 最新の Bot・エラーログを表示 |
| `!restart` | Bot プロセスを再起動 |
| `!help` | コマンド一覧を表示 |

---

# 状態確認（!status）

`!status` は以下を返す。

* **CPU / RAM / GPU** 使用率
* **Manga Line** — `watch_manga_output.py` の稼働状態、最新エラー
* **Unity Line** — Unity プロセスの稼働状態、最新ビルド結果

ログ参照先:

* `logs/manga.log`
* `logs/unity.log`

---

# 製造ライン遠隔操作

## 漫画ライン

```
!manga
```

* `scripts/watch_manga_output.py` をバックグラウンド起動
* `output/manga/` の新規ファイルを検知し Discord Webhook へ通知
* 事前に `DISCORD_WEBHOOK_URL` の設定が必要

## Unity ライン

```
!unity
```

* `scripts/unity_build.ps1` を実行
* 結果は `logs/unity.log` に記録

## GitHub 同期

```
!gitpull
```

* `PROJECT_ROOT` で `git pull` を実行
* リモートの最新を工場 PC に取り込む

---

# 通知

## Webhook 通知（漫画生成）

漫画ファイル（`.json`, `.md`, `.png` 等）が `output/manga/` に追加されると、Webhook 経由で Discord チャンネルへ通知される。

設定:

```powershell
$env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
```

## Bot 通知（ビルド・エラー）

重要イベント（ビルド完了、エラー発生）のみ通知する。
スパム防止のため、毎ビルドではなく主要イベントごとに送る。

通知に含める項目:

* プロジェクト名
* 実行時間
* 成果物の場所
* エラー発生時は概要

---

# セキュリティ

## チャンネル制限

`ALLOWED_CHANNEL_ID` を設定し、指定チャンネル以外からのコマンドを拒否する。
未設定の場合、Bot はコマンドを受け付けない。

## トークン管理

* Bot トークンは `bot/.env` のみに置く
* GitHub に commit しない
* 漏洩時は Discord Developer Portal で **Reset** し、新トークンを `.env` に反映

## 本番と開発の分離

* 本番 Bot と開発 Bot は **別 Application / 別トークン** を推奨
* 開発用 scaffold（`bot/src/`）と工場 Bot（`factory_bot.py`）を同じトークンで同時起動しない

チェックリスト: `workflow/discord-bot-checklist.md`

---

# Chrome Remote Desktop

## 用途

Discord Bot では足りない操作に使う。

* Cursor / VSCode の直接操作
* GUI アプリ（ComfyUI、Blender、Unity Editor）
* ファイルエクスプローラーでの確認
* 初回セットアップ・トラブルシュート

## 向く場面

| 操作 | Discord Bot | Chrome RD |
|------|-------------|-----------|
| 状態確認 | ○ `!status` | ○ |
| git pull | ○ `!gitpull` | ○ |
| スクリプト起動 | ○ `!manga` 等 | ○ |
| コード編集 | × | ○ |
| GUI 操作 | × | ○ |
| 複雑なトラブルシュート | △ | ○ |

---

# 運用フロー（外出先）

## 日常確認

1. Discord アプリを開く
2. `!status` で工場の稼働状態を確認
3. 必要なら `!logs` でエラーを確認

## 製造開始

1. `!gitpull` で最新コードを取得
2. `!manga` または `!unity` でラインを起動
3. Webhook / Bot 通知で完了を待つ

## 障害対応

1. `!status` / `!logs` で症状を把握
2. 軽微なら `!restart` で Bot 再起動
3. 解決しない場合は Chrome Remote Desktop で PC に接続

---

# 今後追加予定

* Discord 自然言語命令（「漫画を生成して」→ スクリプト実行）
* AI Agent 自律化（定期ビルド・通知）
* スマホ専用ステータスダッシュボード

---

# 参照

* 全体構造: `docs/SYSTEM_MAP.md`
* ワークフロー: `docs/WORKFLOW.md`
* Bot 詳細: `bot/README.md`
* 公開前チェック: `workflow/discord-bot-checklist.md`

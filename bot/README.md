# HONRAI_FACTORY Bot

このフォルダには **2 種類の Bot** があります。用途に応じて使い分けてください。

| 種類 | 入口 | 用途 |
|------|------|------|
| **工場 Bot（本番）** | `factory_bot.py` | ComfyUI / Unity / git pull など工場操作 |
| **学習用 scaffold** | `src/index.js` | discord.js v14 の最小構成（`/ping` など） |

Windows + PowerShell 前提、初心者向けに手順をまとめています。

## フォルダ構成

```
bot/
├── .env.example          … 環境変数の雛形（GitHub に commit して OK）
├── .env                  … 実際の設定（自分で作る・commit 禁止）
├── factory_bot.py        … Python 工場 Bot（discord.py）
├── commands/             … Python コマンド群
├── requirements.txt      … Python 依存関係
├── package.json          … Node.js（discord.js scaffold）
├── src/                  … discord.js 学習用
│   ├── index.js
│   ├── deploy-commands.js
│   ├── commands/
│   │   └── ping.js
│   └── events/
└── README.md             … このファイル
```

---

## A. 工場 Bot（Python / discord.py）

工場の自動化コマンド（manga / comfy / unity / gitpull など）を Discord から実行します。

### セットアップ（PowerShell）

```powershell
cd C:\Users\honra\HONRAI_FACTORY\bot

# Python 依存関係（初回のみ）
python -m pip install -r requirements.txt

# .env がなければ作成
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

最低限 `DISCORD_TOKEN` を設定してください。必要に応じて `ALLOWED_CHANNEL_ID` や `PROJECT_ROOT` も設定します。

### 起動

```powershell
cd C:\Users\honra\HONRAI_FACTORY
python -m bot.factory_bot
```

---

## B. discord.js 学習用 scaffold

スラッシュコマンドの作り方を学ぶための最小 Bot です。工場 Bot とは **別プロセス** です（同時起動は同じトークンだと競合するため非推奨）。

### 事前準備

1. [Discord Developer Portal](https://discord.com/developers/applications) で Application を作成
2. **Bot** タブで Bot を追加し、トークンを控える
3. **OAuth2 → URL Generator** で `bot` と `applications.commands` にチェック → 生成 URL でテストサーバーに招待

### セットアップ（PowerShell）

```powershell
cd C:\Users\honra\HONRAI_FACTORY\bot

npm install

# .env に DISCORD_TOKEN / DISCORD_CLIENT_ID / DISCORD_GUILD_ID を設定
notepad .env
```

| 変数 | 取得場所 |
|------|----------|
| `DISCORD_TOKEN` | Developer Portal → Bot → Token |
| `DISCORD_CLIENT_ID` | Developer Portal → General Information → Application ID |
| `DISCORD_GUILD_ID` | Discord でサーバー右クリック → ID をコピー（開発者モード要） |

### 起動

```powershell
# 1. スラッシュコマンドを開発サーバーに登録（初回・コマンド追加時）
npm run deploy-commands

# 2. Bot を起動
npm start

# 開発中（ファイル変更で自動再起動・Node 18+）
npm run dev
```

Discord で `/ping` を実行し、応答が返れば成功です。

### コマンドの追加方法

1. `src/commands/` に新しい `.js` を追加（`ping.js` をコピーして編集）
2. `npm run deploy-commands` を再実行
3. Bot を再起動（`npm run dev` なら自動）

---

## トラブルシューティング

| 症状 | よくある原因 |
|------|--------------|
| ログインできない | `DISCORD_TOKEN` が間違い / 漏洩後に Reset していない |
| `/ping` が表示されない | `deploy-commands` 未実行 / `DISCORD_GUILD_ID` が違う |
| 2 つの Bot を同時に動かせない | 同じトークンは 1 接続のみ — 開発用 Bot を別 Application にする |
| Python Bot が反応しない | `ALLOWED_CHANNEL_ID` が別チャンネルを指している |

詳細チェックリスト: `../workflow/discord-bot-checklist.md`

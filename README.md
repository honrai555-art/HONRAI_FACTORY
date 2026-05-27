# HONRAI_FACTORY

AI 工場（Cursor / Claude）のルールと、Discord bot 開発の土台をまとめたリポジトリです。

## このリポジトリの目的

1. **AI 工場ルールの固定** — Cursor と Claude が同じ方針で動く
2. **日本語化** — 説明・ドキュメントを日本語中心に
3. **GitHub 運用** — コードの正本を GitHub に置く
4. **Discord bot 開発** — Bot 開発を最優先のユースケースにする

## フォルダ構成

```
HONRAI_FACTORY/
├── .cursorrules      … Cursor 用ルール（このリポジトリ全体）
├── CLAUDE.md         … Claude 用ルール
├── README.md         … このファイル（人間向け説明）
├── bot/              … Discord bot（discord.js）
├── prompts/          … AI に渡すプロンプト例
└── workflow/         … GitHub・日常運用の手順
```

## 必要なもの（Windows）

| ツール | 用途 |
|--------|------|
| [Git for Windows](https://git-scm.com/download/win) | バージョン管理 |
| [Node.js LTS](https://nodejs.org/) | Discord bot（Node.js） |
| [Cursor](https://cursor.com/) | AI 支援エディタ |
| PowerShell | ターミナル（Windows 標準） |

## クイックスタート（PowerShell）

```powershell
# 1. リポジトリを clone（GitHub に上げた後）
git clone https://github.com/<あなたのユーザー名>/HONRAI_FACTORY.git
cd HONRAI_FACTORY

# 2. Bot のセットアップ
cd bot
npm install
Copy-Item .env.example .env
# .env を編集してから:
npm run deploy-commands
npm start
```

Bot の詳しい手順は `bot/README.md` を参照してください。

## AI への依頼の仕方（初心者向け）

1. **何をしたいか** を一文で書く（例: 「`/ping` コマンドを追加したい」）
2. **困っていること** があれば症状を書く（例: 「Bot がオンラインにならない」）
3. **大きな変更は避ける** と伝える（例: 「関係ないファイルは触らないで」）

テンプレートは `prompts/` にあります。

## ルールの要点

- 修正する前に **原因の説明** を求める
- **勝手な大規模変更** をしない
- トークン等は **`.env` に置き、GitHub に上げない**

詳細は `.cursorrules` と `CLAUDE.md` を参照してください。

## GitHub への保管

1. GitHub で空のリポジトリ `HONRAI_FACTORY` を作成
2. ローカルで初回 push:

```powershell
git add .
git commit -m "docs: AI工場ルールとDiscord bot開発の土台を追加"
git branch -M main
git remote add origin https://github.com/<あなたのユーザー名>/HONRAI_FACTORY.git
git push -u origin main
```

日常の運用フローは `workflow/github-basics.md` を参照してください。

## ライセンス

未定（必要に応じて追加してください）。

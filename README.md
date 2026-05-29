# HONRAI_FACTORY

AI 製造工場（Cursor / Claude）のルールと、Discord 遠隔操作・製造ライン・外部連携の土台をまとめたリポジトリです。

## このリポジトリの目的

1. **AI 工場ルールの固定** — Cursor と Claude が同じ方針で動く
2. **日本語化** — 説明・ドキュメントを日本語中心に
3. **GitHub 運用** — コードの正本を GitHub に置く
4. **Discord 遠隔操作** — スマホから工場ラインを起動・監視する
5. **製造ライン統合** — 漫画 / キャリアカード / メタバースをパイプライン化する

## フォルダ構成

```
HONRAI_FACTORY/
├── .cursorrules / CLAUDE.md / AGENTS.md
├── README.md
├── bot/                    … Discord 遠隔操作（工場 Bot + discord.js 学習用）
├── workspace/              … 作業入力（原案・ストーリーボード・キャリア等）
├── prompts/                … AI プロンプト資産
├── pipelines/              … 製造ライン定義（YAML）
├── scripts/                … 実行スクリプト・オーケストレータ
├── integrations/           … GAS / Google / Lark 連携
├── unityprojects/          … Unity プロジェクト
├── tools/                  … ComfyUI 等の外部ツール
├── data/                   … マスタデータ
├── config/                 … 工場設定
├── docs/                   … 設計ドキュメント
├── workflow/               … GitHub・日常運用の手順
├── github/                 … サブリポジトリ管理
└── .github/workflows/      … CI/CD
```

## Discord 遠隔操作

`bot/factory_bot.py`（Python / discord.py）が工場の遠隔操作ハブです。

| コマンド | 機能 |
|----------|------|
| `!status` | CPU/RAM/GPU と各ラインの稼働状態 |
| `!gitpull` | GitHub から最新コードを取得 |
| `!manga` | 漫画出力監視を起動 |
| `!comfy_test` | ComfyUI 最小テスト |
| `!unity` | Unity batch ビルド |
| `!logs` | 最新ログを表示 |

起動例:

```powershell
cd C:\Users\honra\HONRAI_FACTORY
python -m bot.factory_bot
```

詳細は `bot/README.md` を参照してください。

## pipelines 構造

`pipelines/` は製造ラインの定義を YAML で管理します。

```
pipelines/
├── manga.yaml           … GPT → ComfyUI → 通知
├── career-card.yaml     … GAS → PDF → 通知
├── metaverse.yaml       … Unity → builds → 通知
├── manga/               … 漫画ライン用の補助定義
├── career-card/
└── metaverse/
```

統合実行の入口は `scripts/orchestrator.py` です。

## 漫画ライン一括実行

PowerShell:

```powershell
python scripts/orchestrator.py pipelines/manga.yaml
```

Discord:

```
!pipeline_manga
```

環境変数（任意）:

| 変数 | 用途 |
|------|------|
| `OPENAI_API_KEY` | GPT 漫画生成 |
| `DISCORD_WEBHOOK_URL` | 完了通知 |
| `MANGA_PIPELINE_TYPE` | `4koma` または `normal`（既定: `4koma`） |
| `MANGA_PIPELINE_INSTRUCTION` | 漫画生成の指示文 |

## integrations 構造

外部サービスとの連携を `integrations/` に集約します。

```
integrations/
├── gas/
│   └── career-card/     … キャリアカード GAS ソース
├── google/              … Sheets / Drive / Slides API
└── lark/                … Lark Webhook / Base 連携
```

既存の Lark 設計・スクリプトは `lark/` にもあり、`integrations/lark/` へ段階的に移行する想定です。

## Unity / Blender ライン

```
blender/
├── input_assets/        … slug 名 FBX を配置（例: torii.fbx）
└── output_assets/       … 軽量化 glb 出力

unityprojects/kaido-walk/Assets/Generated/  … Unity 搬入先

scripts/
├── blender_build.ps1           … Blender 軽量化 + Unity import 自動連鎖
├── import_generated_assets.ps1 … glb → Assets/Generated
└── unity_world_build.ps1       … world_request.json から空間生成
```

Discord コマンド:

| コマンド | 処理 |
|---------|------|
| `!blender` | FBX 軽量化 → glb 生成 → Unity 自動 import |
| `!unity` | import → 空間生成 |
| `!world` | JSON 更新 → import → 空間生成 |

詳細・E2E 手順: `workflow/blender-unity-pipeline.md`

### FBX slug 命名（要約）

- 小文字英数字 + underscore のみ（例: `torii.fbx`, `lava_rock.fbx`）
- 日本語・スペース付きファイル名は NG

## GAS キャリアカードライン

```
integrations/gas/career-card/   … GAS ソース（clasp 管理予定）
pipelines/career-card.yaml        … ライン定義
scripts/career/                   … GAS 呼び出し・後処理
workspace/career/                 … 診断テンプレ・原稿
prompts/career/                   … キャリアカード用プロンプト
```

フロー: Google フォーム → スプレッドシート → GAS → Slides/PDF → 通知

## GitHub 物流構造

```
.github/workflows/
├── lint-bot.yml         … Bot の lint / テスト
└── deploy-gas.yml       … GAS 自動デプロイ

github/                  … サブリポジトリ（career-card-gas 等）
bot/commands/gitpull.py  … Discord から git pull
```

日常の運用フローは `workflow/github-basics.md` を参照してください。

## workspace 構造

```
workspace/
├── manga/          … 漫画原案・キャラクター設定
├── quests/         … クエスト・プロット
├── scenes/         … シーン構成・背景
├── storyboards/    … コマ割り・ストーリーボード
├── career/         … キャリアカード原稿
├── metaverse/      … メタバース空間設計
└── temp/           … 中間生成物（定期削除）
```

## 必要なもの（Windows）

| ツール | 用途 |
|--------|------|
| [Git for Windows](https://git-scm.com/download/win) | バージョン管理 |
| [Node.js LTS](https://nodejs.org/) | Discord bot（Node.js） |
| [Python 3.10+](https://www.python.org/) | 工場 Bot・スクリプト |
| [Cursor](https://cursor.com/) | AI 支援エディタ |
| PowerShell | ターミナル（Windows 標準） |

## クイックスタート（PowerShell）

```powershell
git clone https://github.com/<あなたのユーザー名>/HONRAI_FACTORY.git
cd HONRAI_FACTORY

# Python 工場 Bot
cd bot
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# .env を編集してから:
cd ..
python -m bot.factory_bot
```

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

## ライセンス

未定（必要に応じて追加してください）。
Codex permission test 2026-05-29

# HONRAI_FACTORY DIRECTORY RULES

## 目的

このドキュメントは、HONRAI_FACTORY リポジトリ内の **フォルダ構成と配置ルール** を定義する。
AI・人間のどちらが作業しても、同じ場所に同じ種類のファイルを置くための基準である。

---

# ルート構成

```
HONRAI_FACTORY/
├── docs/              … システム設計・運用ドキュメント
├── bot/               … Discord Bot（工場遠隔操作）
├── scripts/           … ビルド・変換・自動化スクリプト
├── workspace/         … 制作中の原案・素材（作業エリア）
├── output/            … 生成成果物（漫画・画像など）
├── builds/            … バージョン済みビルド成果物
├── logs/              … 操作履歴・ビルドログ・エラー
├── models/            … 学習モデル・大容量データ
├── assets/            … 共通アセット（Blender 等）
├── unityprojects/     … Unity プロジェクト
├── prompts/           … AI への依頼プロンプト例
├── workflow/          … GitHub・日常運用手順
├── workflows/         … 自動化ワークフロー定義
├── lark/              … Lark Base 連携
├── github/            … GitHub 連携スクリプト
├── tools/             … 補助ツール
├── export/            … エクスポート成果物
├── .cursorrules       … Cursor 用ルール
├── CLAUDE.md          … Claude 用ルール
├── AGENTS.md          … AI エージェント向け世界観・製造ルール
└── README.md          … 人間向け概要
```

---

# 各フォルダの役割

## docs/

システム全体の設計・運用ドキュメントを置く。

| ファイル | 内容 |
|----------|------|
| `SYSTEM_MAP.md` | 全体構造・製造ライン・運営思想 |
| `DIRECTORY_RULES.md` | このファイル（フォルダ配置ルール） |
| `AI_ROLE_MAP.md` | AI ツールごとの役割分担 |
| `WORKFLOW.md` | 製造・開発ワークフロー |
| `REMOTE_OPERATION.md` | Discord / 遠隔操作 |

---

## bot/

Discord から工場を遠隔操作する Bot を置く。

```
bot/
├── factory_bot.py     … Python 工場 Bot（本番）
├── commands/          … コマンド実装（manga / unity / gitpull 等）
├── utils/             … ログ・プロセス実行ユーティリティ
├── src/               … discord.js 学習用 scaffold
├── .env.example       … 環境変数テンプレート（commit OK）
└── .env               … 実際のトークン（commit 禁止）
```

---

## scripts/

ビルド・変換・自動化スクリプトを置く。再現可能な実行単位とする。

```
scripts/
├── gpt/               … GPT 漫画生成
├── comfy/             … ComfyUI / Stable Diffusion 連携
├── watch_manga_output.py  … 漫画出力監視・Discord 通知
├── unity_build.ps1    … Unity ビルド
└── README.md          … スクリプト一覧と実行手順
```

---

## workspace/

制作中の原案・素材を置く **作業エリア**。完成品は `output/` または `builds/` へ移す。

```
workspace/
├── manga/             … 漫画原案・キャラクター設定
├── quests/            … クエスト・プロット要素
├── scenes/            … シーン構成・背景・レイアウト
├── storyboards/       … コマ割り・ストーリーボード
└── temp/              … 中間生成物・一時ファイル
```

---

## output/

スクリプトや AI が生成した **成果物** を置く。

```
output/
└── manga/
    ├── 4koma/         … 4コマ漫画（JSON / Markdown）
    ├── normal/        … 普通の漫画
    ├── images/        … ComfyUI 生成画像
    └── prompts_for_comfy.json
```

---

## builds/

バージョン済みパッケージ・リリース成果物を置く。

命名例：

* `builds/YYYYMMDD/`
* `builds/<project-name>/`

---

## logs/

操作履歴・ビルドログ・エラーを置く。日付付きまたはプロジェクト別で管理する。

| ログ | 用途 |
|------|------|
| `bot.log` | Bot 起動・再起動 |
| `manga.log` | 漫画ライン |
| `unity.log` | Unity ビルド |
| `gpt.log` | GPT 生成 |
| `discord.log` | Discord 通知 |
| `error.log` | エラー集約 |

不要な一時ログは定期的に整理する。

---

## models/

学習モデル・チェックポイントなど **大容量データ** を置く。
出力先へは必要最小限のみコピーする。

---

## prompts/

AI への依頼プロンプト例を置く。Cursor / Claude への指示テンプレート。

---

## workflow/

GitHub・Discord Bot・日常運用の手順書を置く。

---

# 配置ルール

## 置いてよいもの

| 種類 | 置き場所 |
|------|----------|
| 設計ドキュメント | `docs/` |
| 自動化スクリプト | `scripts/` |
| 制作中原案 | `workspace/` |
| 生成成果物 | `output/` |
| ビルド成果物 | `builds/` |
| ログ | `logs/` |
| 大容量モデル | `models/` |
| 秘密情報 | `bot/.env`（Git 管理外） |

## 置いてはいけないもの

* `.env` やトークンを Git に commit しない
* 中間ファイルを `workspace/` 直下に散らさない → `workspace/temp/` へ
* 生成物を `scripts/` に混ぜない
* ログを `output/` に混ぜない

---

# 軽量化ルール

* 不要な中間ファイルは `workspace/temp/` に集約し、定期的に削除する
* 画像・3D ファイル・ログは圧縮または最適化する
* `models/` の大容量データは出力先へ必要最小限のみコピーする
* `.venv/` や `node_modules/` は Git 管理しない

---

# 参照

* 全体構造: `docs/SYSTEM_MAP.md`
* AI 役割: `docs/AI_ROLE_MAP.md`
* 製造フロー: `docs/WORKFLOW.md`
* エージェントルール: `AGENTS.md`

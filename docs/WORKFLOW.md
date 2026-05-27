# HONRAI_FACTORY WORKFLOW

## 目的

HONRAI_FACTORY における **製造・開発・運用の標準フロー** を定義する。
漫画・キャリアカード・メタバース・Bot 開発の各ラインで共通の手順を示す。

---

# 基本サイクル

```
設計（司令塔）
    ↓
実装（参謀）
    ↓
生成・ビルド（兵站）
    ↓
成果物出力（output / builds）
    ↓
GitHub 同期（物流）
    ↓
Discord 通知・遠隔確認
    ↓
（継続更新）
```

---

# 漫画ライン

## フロー概要

```
1. 原案作成        workspace/manga/
2. GPT 漫画生成    scripts/gpt/
3. 出力監視        scripts/watch_manga_output.py
4. Discord 通知    Webhook / Bot
5. Prompt 抽出     scripts/comfy/extract_image_prompts.py
6. 画像生成        ComfyUI / Stable Diffusion
7. 成果物保管      output/manga/images/
```

## 1. 原案作成

* キャラクター設定・ストーリーを `workspace/manga/` に置く
* ストーリーボードは `workspace/storyboards/` に置く
* 20タイプ・漫画金型は `AGENTS.md` を参照

## 2. GPT 漫画生成

```powershell
# 4コマ漫画
$env:OPENAI_API_KEY = "sk-xxxxx..."
scripts\gpt\run_gpt_4koma.bat "テーマと指示"

# 普通の漫画
scripts\gpt\run_gpt_normal_manga.bat "テーマと指示"
```

出力先:

* `output/manga/4koma/YYYYMMDD_HHMMSS_title.json`
* `output/manga/normal/YYYYMMDD_HHMMSS_title.json`

## 3. 出力監視と Discord 通知

```powershell
$env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
python scripts\watch_manga_output.py
```

または Discord Bot から:

```
!manga
```

## 4. ComfyUI 用 Prompt 抽出

```powershell
python scripts\comfy\extract_image_prompts.py
```

出力: `output/manga/prompts_for_comfy.json`

## 5. 画像生成

ComfyUI ワークフローを実行し、`output/manga/images/` に保存する。

---

# キャリアカードライン

## フロー概要

```
1. フォーム設計      Google フォーム
2. 回答収集          Spreadsheet / Lark Base
3. 診断・生成        GAS + OpenAI API
4. スライド出力      Google Slides → PDF
5. 結果通知          Discord / メール
```

## データ管理

| DB | 用途 |
|----|------|
| Google Spreadsheet | 顧客DB、回答データ |
| Lark Base | キャリアDB、製造履歴 |
| GitHub | スクリプト・設定の正本 |

---

# メタバースライン

## フロー概要

```
1. 3D モデル制作     Blender → assets/
2. シーン構築        Unity → unityprojects/
3. ビルド            scripts/unity_build.ps1
4. デプロイ          Spatial / KAIDO WALK
5. 状態確認          Discord Bot !unity / !status
```

## Unity ビルド（Discord から）

```
!unity
```

ログ: `logs/unity.log`

---

# Discord Bot 開発

## フロー概要

```
1. 要件整理          prompts/ または Cursor チャット
2. 原因分析          修正前に説明を求める
3. 最小限実装        bot/commands/ または bot/src/
4. 動作確認          ローカル起動
5. GitHub 同期       commit / push（明示依頼時）
6. 本番デプロイ      run_factory_bot.ps1
```

## 工場 Bot 起動

```powershell
cd C:\Users\honra\HONRAI_FACTORY
python -m bot.factory_bot
```

常時起動（自動再起動）:

```powershell
.\run_factory_bot.ps1
```

## 開発用 scaffold（discord.js）

```powershell
cd bot
npm install
npm run deploy-commands
npm start
```

詳細: `bot/README.md`

---

# GitHub 運用フロー

## 日常

```powershell
git status
git add .
git commit -m "feat: 〇〇を追加"
git push
```

## 機能開発（推奨）

```powershell
git checkout -b feature/〇〇
# ... 作業 ...
git add .
git commit -m "feat: 〇〇を追加"
git push -u origin feature/〇〇
# GitHub で PR 作成 → main にマージ
```

## Discord から pull

```
!gitpull
```

詳細: `workflow/github-basics.md`

---

# AI 依頼フロー

## Cursor / Claude への依頼

1. **依頼内容の確認** — 何をしたいか一文で
2. **関連ファイルの読み取り** — 推測で書かない
3. **原因・影響の説明** — 修正前に説明を求める
4. **小さな修正案の提示** — 変更行数・理由を明示
5. **ユーザー承認後に実装**
6. **動作確認手順の提示**

## プロンプトテンプレート

| 用途 | ファイル |
|------|----------|
| 新機能追加 | `prompts/discord-bot-new-feature.md` |
| バグ修正 | `prompts/discord-bot-bugfix.md` |
| コードレビュー | `prompts/discord-bot-review.md` |

---

# ビルドルール

* スクリプトは `scripts/` に置く
* 成果物は `builds/YYYYMMDD/` または `builds/<project-name>/` に出力
* 入力データと設定を明記し、再現可能にする
* 主要イベント完了時に Discord へ通知する

---

# ログと通知

## ログ出力

| ログ | 内容 |
|------|------|
| `logs/bot.log` | Bot 起動・再起動 |
| `logs/manga.log` | 漫画ライン |
| `logs/unity.log` | Unity ビルド |
| `logs/gpt.log` | GPT 生成 |
| `logs/error.log` | エラー集約 |

Discord から確認:

```
!logs
!status
```

## 通知方針

重要なビルド結果・エラー・完了通知のみ Discord へ送る。
毎ビルドではなく **主要イベントごと** に送信する。

通知に含める項目:

* プロジェクト名
* 実行時間
* 成果物の場所
* エラー発生時はスタックトレース概要

---

# トラブルシューティング

| 症状 | 確認先 |
|------|--------|
| Bot が反応しない | `bot/.env` の `DISCORD_TOKEN`, `ALLOWED_CHANNEL_ID` |
| 漫画が生成されない | `logs/gpt.log`, `OPENAI_API_KEY` |
| Discord 通知失敗 | `logs/error.log`, `DISCORD_WEBHOOK_URL` |
| Unity ビルド失敗 | `logs/unity.log` |
| git pull 失敗 | `!gitpull` の出力、競合ファイル |

---

# 参照

* 全体構造: `docs/SYSTEM_MAP.md`
* フォルダルール: `docs/DIRECTORY_RULES.md`
* AI 役割: `docs/AI_ROLE_MAP.md`
* 遠隔操作: `docs/REMOTE_OPERATION.md`
* スクリプト詳細: `scripts/README.md`

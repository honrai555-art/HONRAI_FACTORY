# scripts

HONRAI_FACTORY の自動化スクリプト管理フォルダです。

## 漫画生成ワークフロー

```
1. GPT 漫画生成
   └─ gpt/gpt_manga_generate.py
      └─ output/manga/4koma/
      └─ output/manga/normal/

2. 監視と通知
   └─ watch_manga_output.py
      └─ Discord Webhook 通知（通知センターへ送信）

3. ComfyUI 準備
   └─ comfy/extract_image_prompts.py
      └─ output/manga/prompts_for_comfy.json

4. 画像生成 (ComfyUI)
   └─ Workflow実行
      └─ output/manga/images/
```

## 1. GPT 漫画生成

### 4コマ漫画
```bash
set OPENAI_API_KEY=sk-xxxxx...
scripts\gpt\run_gpt_4koma.bat "テーマと指示"
```

出力:
- JSON: `output/manga/4koma/YYYYMMDD_HHMMSS_title.json`
- Markdown: `output/manga/4koma/YYYYMMDD_HHMMSS_title.md`

### 普通の漫画
```bash
set OPENAI_API_KEY=sk-xxxxx...
scripts\gpt\run_gpt_normal_manga.bat "テーマと指示"
```

出力:
- JSON: `output/manga/normal/YYYYMMDD_HHMMSS_title.json`
- Markdown: `output/manga/normal/YYYYMMDD_HHMMSS_title.md`

詳細は [gpt/README.md](gpt/README.md) を参照してください。

## 2. 出力監視と Discord 通知センター

### 自動監視と通知
```bash
set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/XXXXXXXX/YYYYYYYY
python scripts\watch_manga_output.py
```

または:
```bash
scripts\run_watch_manga_output.bat
```

### 対応ファイル形式
- `.json` - 漫画データ
- `.md` - Markdown形式
- `.png`, `.jpg`, `.jpeg` - 画像

ログ:
- `logs/discord.log` - 送信成功ログ
- `logs/error.log` - エラーログ

### 通知センターで維持する出力
- 漫画プレビュー
- Blender生成プレビュー
- Unity `BuildPreviews/preview.png`
- エラー通知
- 完了通知

Discordは操作入口ではなく通知センターとして扱い、Webhookと画像付き通知を壊さないことを優先します。

### 手動通知
```bash
python scripts\discord_webhook_notify.py --webhook-url "YOUR_WEBHOOK_URL" --preview "output\manga\preview.png"
```

## 3. ComfyUI 用 Image Prompt 抽出

### 実行
```bash
python scripts\comfy\extract_image_prompts.py
```

または:
```bash
scripts\comfy\extract_image_prompts.bat
```

### 入力
- `output/manga/4koma/*.json`
- `output/manga/normal/*.json`

### 出力
`output/manga/prompts_for_comfy.json`

構造:
```json
[
  {
    "type": "4koma",
    "title": "タイトル",
    "panel_number": 1,
    "scene": "シーン説明",
    "image_prompt": "Stable Diffusion用プロンプト"
  },
  ...
]
```

詳細は [comfy/README.md](comfy/README.md) を参照してください。

## ログファイル

- `logs/gpt.log` - GPT生成ログ
- `logs/discord.log` - Discord通知ログ
- `logs/error.log` - エラーログ

## トラブルシューティング

### OpenAI API エラー
- `OPENAI_API_KEY` が設定されているか確認
- API キーが有効か確認
- `logs/gpt.log` でエラーメッセージ確認

### Discord通知失敗
- `DISCORD_WEBHOOK_URL` が設定されているか確認
- Webhook URL が有効か確認
- `logs/error.log` でエラーメッセージ確認

### ファイルが検出されない
- `output/manga/` フォルダが存在するか確認
- ファイル拡張子が対応形式（.json, .md, .png, .jpg）か確認

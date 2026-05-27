# GPT Manga Generator

OpenAI GPT API を使用して、4コマ漫画または普通の漫画を生成します。

## 動作環境
- Python 3.7+
- 環境変数 `OPENAI_API_KEY` が設定されていること

## インストール
```bash
set OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 使用方法

### 4コマ漫画を生成
```bash
scripts\gpt\run_gpt_4koma.bat "ATタイプで、決断をテーマに4コマ漫画を作る"
```

### 普通の漫画を生成
```bash
scripts\gpt\run_gpt_normal_manga.bat "KAIDO WALKの普通の漫画。主人公が街道で歴史AIに出会う回を作る"
```

## 出力

### 4コマ漫画
- **出力先:** `output/manga/4koma/YYYYMMDD_HHMMSS_title.{json,md}`
- **形式:** JSON + Markdown
- **項目:**
  - `title`: 漫画のタイトル
  - `theme`: テーマ
  - `type`: 種類（コメディ、ドラマなど）
  - `mold`: 金型・テンプレート
  - `panels`: 4つのパネルデータ
    - `panel_number`: パネル番号（1-4）
    - `scene`: シーンの説明
    - `dialogue`: セリフ
    - `narration`: ナレーション
    - `image_prompt`: 画像生成用プロンプト
  - `post_text`: 後記・コメント

### 普通の漫画
- **出力先:** `output/manga/normal/YYYYMMDD_HHMMSS_title.{json,md}`
- **形式:** JSON + Markdown
- **項目:**
  - `title`: エピソードタイトル
  - `theme`: テーマ
  - `episode_summary`: エピソード概要
  - `pages`: ページ情報
    - `page_number`: ページ番号
    - `page_goal`: ページの目的
    - `panels`: パネル情報
      - `panel_number`: パネル番号
      - `scene`: シーン説明
      - `dialogue`: セリフ
      - `narration`: ナレーション
      - `image_prompt`: 画像生成用プロンプト
  - `next_episode_hook`: 次話への伏線

## ログ
- **実行ログ:** `logs/gpt.log`
- **エラーログ:** `logs/error.log`

## Discord連携
生成後、Discord に通知するには以下を実行：
```bash
python scripts\discord_webhook_notify.py --webhook-url "YOUR_WEBHOOK_URL" --preview "output\manga\4koma\YYYYMMDD_HHMMSS_title.json"
```

または、生成済みの画像があれば：
```bash
python scripts\discord_webhook_notify.py --webhook-url "YOUR_WEBHOOK_URL" --preview "output\manga\4koma\generated_image.png"
```

## 参考設定
- 推奨モデル: `gpt-4o-mini`
- API温度: 0.7（創造性と一貫性のバランス）
- 最大トークン数: 3000

## トラブルシューティング
1. **API キーが見つからない**
   ```bash
   echo %OPENAI_API_KEY%
   ```
   環境変数が設定されているか確認してください。

2. **API呼び出し失敗**
   - `logs/error.log` を確認してください。
   - API キーが有効か確認してください。
   - レート制限に達していないか確認してください。

3. **JSON パースエラー**
   - API の応答が有効な JSON でない可能性があります。
   - `logs/gpt.log` を確認してください。

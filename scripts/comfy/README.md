# ComfyUI Integration

ComfyUI との連携用スクリプトと設定を管理します。

## Image Prompt 抽出

### 目的
GPT で生成された漫画 JSON から `image_prompt` を抽出し、ComfyUI で画像生成できる形に整形します。

### 実行方法
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
- `output/manga/prompts_for_comfy.json`

### 出力例
```json
[
  {
    "type": "4koma",
    "title": "決断の瞬間",
    "panel_number": 1,
    "scene": "主人公が二つの道の前に立っている",
    "image_prompt": "A character standing at a fork in the road, looking confused..."
  },
  {
    "type": "normal",
    "title": "歴史の道で出会ったAI",
    "page_number": 1,
    "panel_number": 1,
    "scene": "静かな街道を歩く主人公...",
    "image_prompt": "A serene countryside road with a young man walking..."
  }
]
```

## ComfyUI 画像生成

### 前提条件
1. ComfyUI が起動していること（デフォルト: http://127.0.0.1:8188）
2. Stable Diffusion モデル（model.safetensors）が配置されていること

### 実行方法

**1枚だけ生成（最小実装）:**
```bash
scripts\comfy\run_comfy_generate_from_prompts.bat
```

**複数枚生成:**
```bash
python scripts\comfy\run_comfy_generate_from_prompts.py --limit 5
```

**カスタム API URL:**
```bash
python scripts\comfy\run_comfy_generate_from_prompts.py --api-url http://192.168.1.100:8188 --limit 3
```

### ファイル命名規則

**4コマ:**
```
4koma_タイトル_panel1.png
4koma_タイトル_panel2.png
...
```

**普通の漫画:**
```
normal_タイトル_p1_panel1.png
normal_タイトル_p1_panel2.png
normal_タイトル_p2_panel1.png
...
```

### 出力先
- `output/manga/images/` に PNG 形式で保存

### ログ
- 実行ログ: `logs/comfy.log`
- エラーログ: `logs/error.log`

## ワークフロー全体

```
1. GPT 漫画生成
   └─ gpt_manga_generate.py
      ↓
2. Prompt 抽出
   └─ extract_image_prompts.py
      ↓
3. ComfyUI 画像生成
   └─ run_comfy_generate_from_prompts.py
      ↓
4. 出力画像
   └─ output/manga/images/
```

## トラブルシューティング

### "ComfyUI is not running" エラー
```bash
# ComfyUI を起動
python tools\comfyui\ComfyUI-master\main.py

# または
scripts\ComfyUI\run_comfyui_manga.bat
```

### ワークフロー送信エラー
- ComfyUI ログで詳細を確認
- モデルファイルが正しく配置されているか確認
- API URL が正しいか確認（デフォルト: http://127.0.0.1:8188）

### 画像がダウンロードできない
- ComfyUI の `/view` エンドポイントが有効か確認
- ファイアウォール設定を確認

## 次のステップ
- 生成画像を Markdown やレイアウトツールに統合
- ComfyUI ワークフロー設定をカスタマイズ（ステップ数、CFG 値など）
- バッチ処理の並列化

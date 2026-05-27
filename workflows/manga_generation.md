# HONRAI_FACTORY Manga Generation Workflow

## 目的
HONRAI_FACTORY の漫画生成ラインを ComfyUI と連携して構築します。
出力先は `output/manga` です。

## 連携概要
- ComfyUI 本体: `tools/comfyui/ComfyUI-master`
- ローンチエントリ: `tools/ComfyUI/run_comfyui_manga.bat`
- 漫画出力先: `output/manga`
- プロジェクト素材: `workspace/`
- プロンプト素材: `prompts/`

## はじめ方
1. `tools/ComfyUI/run_comfyui_manga.bat` を実行して ComfyUI を起動します。
2. ComfyUI の UI でワークフローを作成または読み込みます。
3. 出力画像の保存先を `output/manga` に設定します。

## 漫画生成ラインの雛形
1. `workspace/manga/` に漫画原案とキャラクター設定を配置する。
2. `workspace/storyboards/` にページ構成とコマ割りを保存する。
3. `prompts/manga/` にプロンプトテンプレートを用意する。
4. `prompts/characters/`, `prompts/quests/`, `prompts/world/` から世界観・キャラクター描写を組み合わせる。
5. ComfyUI で次のようなノード構成を作成する。
   - テキストプロンプト生成
   - 画像生成ノード（例: Stable Diffusion）
   - シード / バッチ設定
   - 画像出力ノード
6. 生成した素材を `output/manga` に保存し、`workspace/scenes/` や `workspace/storyboards/` に戻して編集する。

## 推奨ワークフロー構成
- 入力: `prompts/manga/` の JSON / テキストファイル
- キャラクター: `prompts/characters/` の設定を反映
- 舞台: `prompts/world/` のロケーション描写
- 物語要素: `prompts/quests/` のクエスト文脈
- 出力: `output/manga` へ PNG/JPEG を保存

## 注意点
- ComfyUI のモデルは `tools/comfyui/ComfyUI-master/models` 配下に配置する。
- 出力先 `output/manga` は既に生成済みなので、必要に応じてサブフォルダを作る。
- 中間ファイルは `workspace/temp` にまとめて管理する。

## 次のステップ
- `scripts/` に自動化スクリプトを追加して、ワークフローの一括実行を実現する。
- `docs/` に漫画生成手順と ComfyUI セットアップ手順を追記する。

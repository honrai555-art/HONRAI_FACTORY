# AGENTS.md — 02_game-object

## この製造ラインの目的
FBX → Blender 軽量化 → Unity import → ワールド生成までを製造する。

## 入力
- `SPA_MODEL/02_game-object/blender/input_assets/*.fbx`（slug 命名）
- `world_request.json`（ルート）
- `SPA_MODEL/shared-data/` のタグ・世界観

## 出力
- `SPA_MODEL/02_game-object/blender/output_assets/*.glb`
- `SPA_MODEL/02_game-object/unity/kaido-walk/Assets/Generated/`
- `BuildPreviews/preview.png`

## 使用ツール
- Blender、Unity、PowerShell
- `SPA_MODEL/02_game-object/scripts/`

## 起動方法
```powershell
.\SPA_MODEL\02_game-object\run_line.ps1
```
Discord: `!blender` → `!unity` または `!world`

## テスト方法
1. `honrai_kun.fbx` 等を input に配置
2. `run_line.ps1` または `!blender`
3. Generated フォルダと `logs/blender_build.log` を確認

## 禁止事項
- `.env` 編集・移動、API キー直書き、ファイル削除

## Codex作業ルール
- `SPEC.md` → `TASKS.md` → 最小 diff
- パス変更時は `bot/commands/blender.py` `unity.py` とセットで確認

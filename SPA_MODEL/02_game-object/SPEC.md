# SPEC.md
## 完成形
Discord から FBX → glb → Unity 配置まで遠隔実行可能。
## 入力
FBX、`world_request.json`、環境変数（PROJECT_ROOT, BLENDER_EXE 等）。
## 出力
glb、Generated Prefab、プレビュー画像。
## 処理
前処理 → Blender → glb → import → world build。
## 成功条件
`!blender` 後に Generated にアセットが増える。
## 失敗条件
パス不一致、手動 Unity 必須、通知なし。

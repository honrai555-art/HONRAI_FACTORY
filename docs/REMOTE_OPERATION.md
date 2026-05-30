# REMOTE OPERATION

## 目的

HONRAI_FACTORY の遠隔運用では、Discordを工場の操作入口ではなく通知センターとして使う。
製造指示、コード修正、GitHub反映、ファイル整理は ChatGPT / Codex / GitHub が担当し、Discord は完成通知・エラー通知・画像付きプレビュー確認を受け取る場所に限定する。

---

# 使用ツール

* ChatGPT
* Codex
* Chrome Remote Desktop
* Discord
* GitHub
* Cursor

---

# 基本構成

ChatGPT（企画・指示・レビュー）
↓
Codex（Windows上で実行・修正・GitHub反映）
↓
Tripo / Blender / Unity（ゲーム空間・オブジェクト製造）
↓
preview.png 生成
↓
Discord通知（完成・エラー・画像プレビュー）
↓
スマホ確認 / チーム共有

---

# Discordの位置づけ

Discordは以下の通知センターとして扱う。

* 完成通知
* エラー通知
* 漫画プレビュー
* Blender生成プレビュー
* Unity `BuildPreviews/preview.png`
* チーム共有
* スマホ確認

`!manga` / `!unity` / `!blender` などの操作コマンドは削除しないが、今後の主軸ではない。必要時に使う補助機能として整理する。

---

# 緊急時

Chrome Remote Desktop で直接操作する。

---

# 遠隔操作対象

通常の操作対象は Codex / Cursor / PowerShell / Unity / Blender / Docker / ComfyUI とする。Discordからの直接操作は補助扱いにし、通知と画像プレビューの安定性を優先する。

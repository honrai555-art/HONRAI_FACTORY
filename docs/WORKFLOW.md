# WORKFLOW

## GitHub同期手順

変更後：

```bash
git add .
git commit -m "更新内容"
git push
```

---

## 作業フロー

① ChatGPTで企画・指示・レビュー
② CodexでWindows上の実行・修正・GitHub反映
③ Tripo / Blender / Unityでゲーム空間・オブジェクト製造
④ GitHubに記録・保管・バージョン管理
⑤ `preview.png` または `BuildPreviews/preview.png` を生成
⑥ Discordへ完成通知・エラー通知・画像付きプレビューを送信
⑦ スマホ確認 / チーム共有

---

## 役割分担

| 担当 | 役割 |
|------|------|
| ChatGPT | 企画、指示、レビュー |
| Codex | Windows上で実行、修正、GitHub反映 |
| Tripo / Blender / Unity | ゲーム空間・オブジェクト製造 |
| GitHub | 記録、保管、バージョン管理 |
| Discord | 通知、画像プレビュー、チーム共有 |

---

## Discord運用ルール

* Discord Botは削除しない
* 既存Webhook通知は壊さない
* 画像付き通知機能は維持する
* 操作コマンド開発は優先度を下げる
* `!manga` / `!unity` / `!blender` などは補助機能として扱う
* チーム共有が必要な成果物はDiscordに送る

---

## AI作業ルール

* AI生成コードは必ず確認
* 破壊的変更前にcommit
* modelsはGitHubへ上げない

# Discordの役割

## 結論
Discordは遠隔操作の主役ではなく、完成通知・エラー通知・画像プレビューを受け取る通知センターとして使う。

## 役割
- 完成通知
- エラー通知
- `preview.png` の画像付き共有
- チームメンバーへの共有
- スマホ確認

## 主役ではないもの
- 製造指示
- コード修正
- GitHub反映
- ファイル整理

これらはChatGPT / Codex / GitHubが担当する。

## 新しい製造フロー
ChatGPT
↓
Codex
↓
Tripo / Blender / Unity
↓
`preview.png` 生成
↓
Discord通知
↓
スマホ確認

## 運用ルール
- Discordは削除しない
- 操作コマンド開発は優先度を下げる
- 通知と画像プレビューの安定性を優先する
- チーム共有が必要な成果物はDiscordに送る

## 通知対象
以下の出力は、Discordへ画像付きまたは要約付きで届く構造を維持する。

- 漫画プレビュー
- Blender生成プレビュー
- Unity `BuildPreviews/preview.png`
- エラー通知
- 完了通知

## 補助機能として残すもの
既存のDiscord Botや `!manga` / `!unity` / `!blender` / `!gitpull` などの操作コマンドは削除しない。ただし、今後の主軸は操作入口ではなく通知センターであるため、これらは必要時に使う補助機能として扱う。

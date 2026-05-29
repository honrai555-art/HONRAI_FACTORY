# HONRAI_FACTORY AGENTS

## HONRAI世界観
HONRAI_FACTORY は AI 漫画と 3D コンテンツ制作を融合した創造工場です。
この世界ではキャラクター、クエスト、舞台、ストーリーが連動し、AI が漫画原案、シーン制作、ストーリーボード生成、3D 表現の組み合わせをサポートします。

## 20タイプ
HONRAI 世界は 20 の基本タイプで構成されます。
1. 主人公
2. 相棒
3. ライバル
4. メンター
5. 敵対勢力
6. サポートAI
7. 町／都市
8. 森林／自然
9. 研究施設
10. 工場／基地
11. 武器／道具
12. 秘宝／資源
13. クエスト目的
14. 戦闘シーン
15. 日常シーン
16. 重要事件
17. 感情表現
18. テーマ／モチーフ
19. 技術／ガジェット
20. 進化／変化

## 漫画金型
- 漫画制作は "金型" として以下を意識します。
  - キャラクター設定
  - コマ割りと構図
  - セリフとナレーション
  - 感情のリズム
  - 行動と結果の連続性
- ワークフローでは `workspace/manga` に原案やレイアウトを保持し、`workspace/storyboards` にストーリーボードとページ設計を保存します。

## buildルール
- `scripts/` にビルドや変換用スクリプトを置く。
- `builds/` は生成アセット、ビルド成果物、バージョン済みパッケージの出力先。
- ビルドは再現可能性を優先し、入力データと設定を明記する。
- 各ビルドごとに `builds/YYYYMMDD` や `builds/<project-name>` などのサブディレクトリを使う。

## 軽量化ルール
- 生成プロセスでは不要なファイルを除外する。
- 中間ファイルは `workspace/temp` に集約し、必要がなくなれば定期的に削除する。
- 画像、3D ファイル、ログは圧縮または最適化してサイズを抑える。
- 学習モデルや大容量データは `models/` など専用フォルダに置き、出力先へは必要最小限のみコピーする。

## Discord通知方針
- 重要なビルド結果、エラー、完了通知は Discord へ送信する。
- 通知メッセージには以下を含める。
  - プロジェクト名
  - 実行時間
  - 成果物の場所
  - エラー発生時はスタックトレース概要
- 通知はスパムにならないよう、毎ビルドではなく主要イベントごとに送信する。

## logs出力方針
- `logs/` フォルダへは操作履歴、ビルドログ、エラー、メトリクスを出力する。
- ログは日付付きファイルまたはプロジェクト別ファイルで管理する。
- 詳細ログと概要ログを分け、必要に応じてフィルタできるようにする。
- `logs/` には不要な一時ログを残さず、定期的に整理する。

## Cursor Cloud specific instructions

### Services overview

This repo has **two Discord bots** (separate processes, same `bot/` directory):

| Bot | Runtime | Entry point | Framework |
|-----|---------|-------------|-----------|
| Factory Bot (main) | Python 3.10+ | `python3 -m bot.factory_bot` (from repo root) | discord.py |
| Learning scaffold | Node.js ≥ 18 | `node src/index.js` (from `bot/`) | discord.js v14 |

Both require `DISCORD_TOKEN` in `bot/.env`. Without a valid token they exit with `LoginFailure` / `TokenInvalid` — this is expected.

### Running and testing

- **Python tests**: `python3 test_commands.py` (from repo root) — exercises `!status`, `!manga`, `!unity` commands offline.
- **Python bot imports**: all 12 command/utility modules load with no errors.
- **Node.js syntax check**: `node -c src/index.js` (from `bot/`).
- No ESLint config or CI lint workflows exist for the main project (the ComfyUI tool under `tools/comfyui/` has its own workflows but is independent).
- Use `python3` instead of `python` in this environment (no `python` symlink by default).

### Environment file

`bot/.env` must exist before running either bot. Create it from `bot/.env.example` if missing:
```
cp bot/.env.example bot/.env
```
Then set `DISCORD_TOKEN` to a valid token. Other keys (`OPENAI_API_KEY`, `UNITY_EXE`, etc.) are optional for basic bot operation.

### Gotchas

- The `tools/comfyui/` directory is a large vendored copy of ComfyUI with heavy ML dependencies — **do not** install its `requirements.txt` unless working specifically on the ComfyUI pipeline.
- `pip install` defaults to `--user` in this environment; packages go to `~/.local/lib/`. This is fine for dev.

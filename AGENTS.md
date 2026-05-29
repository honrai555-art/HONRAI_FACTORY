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

| Service | Language | Entry point | Run command |
|---------|----------|-------------|-------------|
| Python Factory Bot | Python 3.10+ | `bot/factory_bot.py` | `python -m bot.factory_bot` (from repo root) |
| Node.js Discord Bot | Node.js 18+ | `bot/src/index.js` | `cd bot && npm start` or `npm run dev` |
| Orchestrator | Python | `scripts/orchestrator.py` | `python scripts/orchestrator.py pipelines/<name>.yaml` |

### Required secrets

- `DISCORD_TOKEN` — the only hard requirement. Without it, both bots exit immediately.
- Copy `bot/.env.example` to `bot/.env` and fill in the token. The Python bot reads from `bot/.env` via `python-dotenv`.
- The Node.js bot also reads `DISCORD_TOKEN` from `bot/.env`.

### Lint and test

- **Python lint**: `python3 -m ruff check bot/ scripts/ --exclude tools/ --exclude SPA_MODEL/` (15 pre-existing warnings in the codebase).
- **Node.js syntax**: `node --check bot/src/index.js` — no ESLint config exists.
- **No automated test suite**: verify manually by importing bot modules and running command functions (e.g. `from bot.commands.status import get_status; get_status()`).

### Gotchas

- `tools/comfyui/` is a vendored copy of ComfyUI with its own `requirements.txt` and `pyproject.toml`. Do **not** install those unless working on ComfyUI integration.
- Many scripts in `scripts/` are PowerShell (`.ps1`) intended for Windows. On Linux, only the Python scripts are runnable.
- The bot's `_validate_startup()` raises `RuntimeError` if `DISCORD_TOKEN` is unset — this is intentional and correct.
- Logs are written to `logs/` at the repo root (created automatically by `bot/utils/logger.py`).

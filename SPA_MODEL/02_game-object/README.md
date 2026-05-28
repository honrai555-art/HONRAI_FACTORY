# 02_game-object — ゲームオブジェクト製造ライン

## shared-data 参照

[`../shared-data/character_rules.csv`](../shared-data/character_rules.csv)（FBX slug）、[`../shared-data/tags.csv`](../shared-data/tags.csv)

---

## 起動方法

```powershell
cd C:\Users\honra\HONRAI_FACTORY\SPA_MODEL\02_game-object
.\run_line.ps1
```

1 コマンドで **Blender → Unity import → Unity world → Discord 通知**（Webhook 設定時）まで実行します。

## 必要ツール

| ツール | 用途 |
|--------|------|
| Blender | FBX 軽量化・glb 出力 |
| Unity Editor | import / ワールドビルド |
| PowerShell | スクリプト実行 |
| Python 3.10+ | `notify_blender_build.py` |

環境変数（`bot/.env` — **Codex は編集しない**）:

| 変数 | 用途 |
|------|------|
| `PROJECT_ROOT` | リポジトリルート |
| `BLENDER_EXE` | Blender 実行ファイル（任意・自動検出可） |
| `UNITY_EXE` | Unity 実行ファイル |
| `DISCORD_WEBHOOK_URL` | 完了通知 |

## FBX 投入場所（正本）

```text
SPA_MODEL/02_game-object/blender/input_assets/
```

- 小文字 slug のみ（例: `torii.fbx`, `honrai_kun.fbx`）
- 旧 `blender/input_assets/` は [`../../blender/README_redirect.md`](../../blender/README_redirect.md) を参照

## Unity プロジェクト（正本）

```text
SPA_MODEL/02_game-object/unity/kaido-walk/
Assets/Generated/   … glb 搬入先
```

## Discord 確認方法

1. `.\run_line.ps1` 完了後 `logs/success.log` に `Discord notification sent`
2. Bot: `!blender` / `!unity` / `!status`
3. チャンネルに Webhook メッセージ（`DISCORD_WEBHOOK_URL` 設定時）

## ログ

| ファイル | 内容 |
|----------|------|
| `logs/success.log` | ライン成功ログ |
| `logs/error.log` | ラインエラー |
| `../../logs/blender_build.log` | Blender 詳細 |
| `../../logs/unity_import.log` | Unity import |
| `../../logs/unity_world_build.log` | ワールドビルド |

## よくあるエラー

| 症状 | 対処 |
|------|------|
| FBX 0 件 | `blender/input_assets/` に slug 名 FBX を配置 |
| Blender 未検出 | `BLENDER_EXE` を `bot/.env` に設定（人間が設定） |
| Unity 失敗 | `logs/unity_world_build.log` を確認 |
| 通知なし | `DISCORD_WEBHOOK_URL` を確認 |

## 移行メモ

- `blender/` → `SPA_MODEL/02_game-object/blender/`（ルートは README_redirect のみ）
- `unityprojects/kaido-walk/` → `SPA_MODEL/02_game-object/unity/kaido-walk/`
- スクリプト正本: `SPA_MODEL/02_game-object/scripts/`
- バックアップ: `99_archive/backup_before_game_object_move/`

## 最終更新

フェーズ2-A: blender / unity 本体移行、run_line フルパイプライン、SPA 基準パス

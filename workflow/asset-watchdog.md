# Asset Watchdog — FBX 自動監視

`blender/input_assets/` に FBX を置くと、Blender → Unity → World Build まで自動実行します。

## 起動

```powershell
cd C:\Users\honra\HONRAI_FACTORY
.\scripts\start_asset_watchdog.ps1
```

- 落ちたら 5 秒後に自動再起動
- `Ctrl+C` で終了

## 監視対象

```
blender/input_assets/*.fbx
```

## 自動処理

1. 新しい FBX を検知（hash + mtime + 2 回安定確認）
2. `world_request.json` を自動更新
3. `scripts/blender_build.ps1`
4. `scripts/import_generated_assets.ps1`
5. `scripts/unity_world_build.ps1`
6. Discord 通知

## world_request.json 自動生成

`torii.fbx` + `bridge.fbx` を置いた場合:

```json
{
  "world_name": "AUTO_20260527_2200",
  "theme": "auto detected assets",
  "route_length": 500,
  "objects": ["bridge", "torii"],
  "characters": ["honrai_kun"],
  "mood": "探索",
  "target": "Spatial軽量版"
}
```

`honrai_kun.fbx` のようなキャラ slug は `characters` に入ります。

## Discord 通知

- FBX detected
- Blender build started
- Unity import started
- World build started
- Preview complete

## 重複防止

- SHA256 hash + last modified + file size
- 成功後のみ `logs/asset_watchdog_state.json` に記録
- 失敗時は 120 秒クールダウン後に再試行
- 処理中はキューで直列実行

## ログ

| ファイル | 内容 |
|---------|------|
| `logs/asset_watchdog.log` | 監視・パイプライン全体 |
| `logs/blender_build.log` | Blender 処理 |
| `logs/unity_import.log` | Unity import |
| `logs/unity_world_build.log` | 空間生成 |

## 人間の作業

```
FBX を blender/input_assets/ に置く
```

それ以外（Blender / Unity / Preview / Discord）は自動です。

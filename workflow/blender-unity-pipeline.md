# Blender → Unity 物流ライン

Blender で軽量化した glb を Unity へ自動搬入し、`!world` で配置する手順です。

## FBX slug 命名ルール

`blender/input_assets/` に置く FBX は **slug 名** にしてください。

| ルール | 内容 |
|--------|------|
| 文字種 | 半角英数字 |
| 大文字小文字 | 小文字 |
| スペース | 禁止 |
| 日本語 | 禁止 |
| 単語区切り | underscore (`_`) |

### OK 例

- `torii.fbx`
- `bridge.fbx`
- `lava_rock.fbx`
- `post_town.fbx`
- `honrai_kun.fbx`

### NG 例

- `鳥居.fbx`
- `Torii FBX.fbx`
- `bridge final.fbx`
- `橋モデル.fbx`

### 理由

`world_request.json` の `objects` / `characters` と `Assets/Generated/*.glb` を安定対応させるため。

## world_request.json の asset 命名

`objects` / `characters` には slug を使います。

```json
{
  "world_name": "KAIDO_FIRE_ROUTE",
  "theme": "火山の街道",
  "route_length": 500,
  "objects": ["torii", "lava_rock", "bridge"],
  "characters": ["honrai_kun"],
  "mood": "熱い・挑戦・敗者復活",
  "target": "Spatial軽量版"
}
```

Unity は以下を優先探索します。

- `Assets/Generated/torii.glb`
- `Assets/Generated/lava_rock.glb`
- `Assets/Generated/bridge.glb`
- `Assets/Generated/honrai_kun.glb`

存在しない場合は Primitive fallback です。

## 処理フロー

```
blender/input_assets/*.fbx
        ↓ !blender
scripts/blender_build.ps1
        ↓
blender/output_assets/*.glb
        ↓ 自動
scripts/import_generated_assets.ps1
        ↓
Assets/Generated/*.glb
        ↓ !world
GenerateWorldFromJson.cs
        ↓
BuildPreviews/preview.png → Discord
```

## 常時監視（Asset Watchdog）

FBX を `blender/input_assets/` に置くだけで、以下が自動実行されます。

```
FBX 検知 → Blender → Unity Import → World Build → Preview → Discord
```

起動:

```powershell
cd C:\Users\honra\HONRAI_FACTORY
.\scripts\start_asset_watchdog.ps1
```

ログ: `logs/asset_watchdog.log`

`world_request.json` は FBX ファイル名 slug から自動生成されます（`world_name`: `AUTO_日時`）。

## E2E 手動確認

### 1. FBX 配置

```
blender/input_assets/torii.fbx
```

### 2. Discord で実行

```
!blender
```

### 3. 確認

| 確認項目 | パス |
|---------|------|
| glb 出力 | `blender/output_assets/torii.glb` |
| Unity 搬入 | `unityprojects/kaido-walk/Assets/Generated/torii.glb` |
| Blender ログ | `logs/blender_build.log` |
| Import ログ | `logs/unity_import.log` |

### 4. 空間生成

```
!world 火山 torii bridge
```

### 5. 確認

| 確認項目 | パス |
|---------|------|
| preview | `BuildPreviews/preview.png` |
| Discord | Webhook 通知 |

## 失敗時のログ

| 症状 | 確認ログ |
|------|---------|
| Blender 失敗 | `logs/blender_build.log` 末尾 20 行 |
| Import 失敗 | `logs/unity_import.log` 末尾 20 行 |
| 空間生成失敗 | `logs/unity_world_build.log` |

Discord Webhook 通知にも末尾ログが含まれます。

## 手動実行

```powershell
cd C:\Users\honra\HONRAI_FACTORY

# Blender + Import 一括
.\scripts\blender_build.ps1

# Import のみ
.\scripts\import_generated_assets.ps1

# 空間生成
.\scripts\unity_world_build.ps1
```

## !status で見える項目

- Blender input FBX count
- Blender output glb count
- Last blender build time
- Unity Generated asset count
- Last import time
- Last import error

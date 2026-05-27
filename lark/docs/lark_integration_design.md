# Lark Base / Docs 設計

## 目的
Lark を HONRAI_FACTORY の「製造ラインの管制塔」として使うため、通知・同期・進捗管理の基盤設計を定義します。

## 1. Lark Base の役割

- 案件・タスク・進捗・エラー・成果物を一元管理
- 通知テンプレートを使って関係者へ一斉連絡
- 週次報告で現場と経営の共通認識を維持
- ローカルスクリプトと API 連携で自動更新を目指す

## 2. 情報の構造

- `Base`：案件・タスクマスタ、ステータスマスタ、担当者マスタなどの骨組み
- `Docs`：運用ルール、通知テンプレート、運用手順、品質基準
- `Rules`：通知運用方針、エスカレーションルール、データ更新ルール

## 3. 連携設計

### 3.1 通知フロー
1. ローカルスクリプトが成果物生成やエラーを検知
2. Discord / Lark 通知テンプレートを選択
3. Lark に webhook 送信または Bot 通知
4. 重要通知は `@担当者` や `@チーム` で展開
5. 返信/承認に応じて `進捗状態` を更新

### 3.2 同期フロー
- `output/manga/prompts_for_comfy.json` の `image_prompt` を ComfyUI に投げる
- 生成開始 / 完了 / 失敗の状態を Lark に通知
- 生成結果は `output/manga/images/` へ保存し、URL を通知
- 生成エラーは `エラー管理` に記録し、即時通知

### 3.3 進捗管理
- 案件・タスクは Lark Base の `状態` で管理
- 進捗更新は `確認待ち` / `修正中` / `完了` などを使う
- 週次報告で `生成件数`・`エラー件数`・`保留件数` を報告

## 4. 運用の分担

- `現場`：データ入力、進捗更新、エラー報告
- `運営`：通知テンプレート作成、Lark Base 監視、週次報告作成
- `技術`：API 連携・自動化スクリプト開発、ComfyUI 運用
- `QA`：成果物チェック、修正依頼、報告レビュー

## 5. 推奨運用ルール

- 重要通知は必ず `Lark` でも共有する
- 状態変更時は `更新日` を更新する
- エラー発生時は `エラーID` を振って記録
- 定期的に `Base` の整合性を確認する
- `Docs` は常に最新に保ち、変更履歴を残す

## 6. 参考ファイル
- `lark/base/manufacturing_line_base_schema.md`
- `lark/base/manufacturing_line_base_sample.csv`
- `lark/base/status_master.csv`
- `lark/rules/lark_notification_rules.md`
- `lark/rules/lark_docs_usage_rules.md`

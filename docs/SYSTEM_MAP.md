# HONRAI_FACTORY SYSTEM MAP

## 目的

HONRAI_FACTORY は、AIを活用した「継続学習コンテンツ製造工場」である。

目的：

* 漫画コンテンツ製造
* ゲームコンテンツ製造
* キャリアカード生成
* メタバース制作
* Discord通知センター
* AIによる自動化
* GitHub物流管理

を統合すること。

---

# 全体構造

## 戦略司令塔

* ChatGPT
* Claude

役割：

* 企画
* 指示
* レビュー
* 設計
* 戦略
* 世界観
* キャリア設計
* 組織設計

---

## 実装参謀

* Cursor
* VSCode

役割：

* コード編集
* AI実装
* 構造整理
* ファイル修正

---

## 製造兵站

* Codex
* Docker
* WSL2

役割：

* Windows上での実行
* 自動生成
* 大量修正
* GitHub反映
* 実行環境
* AI Agent

---

## 物流倉庫

* GitHub

役割：

* 記録
* コード保管
* 成果物保管
* バージョン管理
* AI共有
* 自動同期

---

## ゲーム空間・オブジェクト製造

* Tripo
* Blender
* Unity

役割：

* 3Dオブジェクト製造
* ゲーム空間制作
* プレビュー生成
* `preview.png` / `BuildPreviews/preview.png` 出力

---

## 通知センター

* Discord Webhook
* Discord Bot

役割：

* 完成通知
* エラー通知
* 漫画プレビュー共有
* Blender生成プレビュー共有
* Unity `BuildPreviews/preview.png` 共有
* チーム共有
* スマホ確認

Discordは遠隔操作の主役ではない。`!manga` / `!unity` / `!blender` / `!gitpull` などの既存操作コマンドは削除せず、必要時の補助機能として残す。

---

# 新しい製造フロー

ChatGPT
↓
Codex
↓
Tripo / Blender / Unity
↓
preview.png生成
↓
Discord通知
↓
スマホ確認

---

# 製造ライン

## 漫画ライン

使用：

* ComfyUI
* StableDiffusion
* GPT

成果物：

* 漫画
* キャラクター
* 世界観素材
* 漫画プレビュー

---

## キャリアカードライン

使用：

* Googleフォーム
* GAS
* Google Slides
* OpenAI API

成果物：

* キャリアカード
* PDF
* 診断結果

---

## メタバースライン

使用：

* Tripo
* Unity
* Blender
* Spatial

成果物：

* 3D物語空間
* KAIDO WALK
* 地域空間
* Blender生成プレビュー
* Unity `BuildPreviews/preview.png`

---

# データベース

使用：

* Google Spreadsheet
* Lark Base
* GitHub

役割：

* 顧客DB
* キャリアDB
* 製造履歴
* 更新履歴

---

# 今後追加予定

* AI Agent自律化
* 自動ビルド
* 自動通知
* AIプロジェクト管理
* 財務管理自動化

Discord自動命令は優先度を下げ、通知と画像プレビューの安定性を優先する。

---

# 運営思想

HONRAI_FACTORY は、
「継続学習コンテンツを製造・更新し続けるAI工場」である。

目的は：

* 個人の成長
* キャリア進化
* 世界観構築
* 地域との接続

を、AIと製造ラインによって継続的に支援すること。

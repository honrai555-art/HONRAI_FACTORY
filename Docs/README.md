# HONRAI Career Card AGI Input System

Google Apps Script Webアプリとして動く、キャリアカードAGI入力装置のMVPです。
ユーザー入力を`CARD_MASTER`シートへ保存し、STRUCT JSONを生成してOpenAI APIへ送信し、街道WALK用の`layout_command.json`形式を画面表示します。

## 成果物

```text
/Frontend
  index.html
  style.css
  app.js
/GAS
  Code.gs
/Docs
  README.md
/output
  sample_struct.json
  sample_layout_command.json
```

## Spreadsheet構造

シート名: `CARD_MASTER`

| 列 | 説明 |
| --- | --- |
| `card_id` | `CM001`形式のカードID |
| `user_id` | ユーザーID。未指定時は`anonymous` |
| `type` | HONRAIタイプ |
| `fit_score` | 適合率 |
| `phase` | キャリアフェーズ |
| `role_candidate` | 役割候補 |
| `stop` | やめる項目。複数行テキストとして保存 |
| `keep` | 残す項目。複数行テキストとして保存 |
| `start` | やる項目。複数行テキストとして保存 |
| `experience` | 経験。複数行テキストとして保存 |
| `skill` | スキル。複数行テキストとして保存 |
| `environment` | 環境。複数行テキストとして保存 |
| `desired_change` | 望む変化 |
| `created_at` | 作成日時ISO文字列 |
| `updated_at` | 更新日時ISO文字列 |

`saveCard()`実行時にシートが存在しない場合は自動作成され、ヘッダーも自動補正されます。

## デプロイ手順

1. Google Spreadsheetを作成します。
2. Spreadsheetから「拡張機能」→「Apps Script」を開きます。
3. `GAS/Code.gs`の内容をApps Scriptの`Code.gs`へ貼り付けます。
4. `Frontend/index.html`、`Frontend/style.css`、`Frontend/app.js`をApps Scriptプロジェクトへ追加します。
   - Apps Script側のファイル名は`Frontend/index`、`Frontend/style`、`Frontend/app`として扱える構成にしてください。
   - `index.html`は`<?!= include('Frontend/style'); ?>`と`<?!= include('Frontend/app'); ?>`でCSS/JSをインライン化します。
5. Apps Scriptの「プロジェクトの設定」→「スクリプト プロパティ」に以下を登録します。
   - `OPENAI_API_KEY`: OpenAI APIキー
   - 任意: `MOCK_AGI=true`（APIキーなしで画面確認したい場合）
6. 「デプロイ」→「新しいデプロイ」→種類「ウェブアプリ」を選択します。
7. 実行ユーザーを「自分」、アクセス権を用途に合わせて設定してデプロイします。

## API関数

### `getCard(cardId)`

`CARD_MASTER`からカードIDに一致する行を取得し、カードオブジェクトを返します。

### `saveCard(data)`

フォーム入力をSpreadsheetへ保存します。
`card_id`が空の場合は`CM001`から連番で採番します。
保存後、正規化されたカードオブジェクトを返します。

### `generateStruct(cardId)`

保存済みカードを以下のSTRUCT JSONへ変換します。

```json
{
  "card_id": "CM001",
  "type": "主人公",
  "fit_score": 72,
  "phase": "探索",
  "role_candidate": "explorer",
  "decision": {
    "stop": ["目的のない応募"],
    "keep": ["顧客理解"],
    "start": ["AIツール検証"]
  },
  "career_material": {
    "experience": ["営業企画"],
    "skill": ["データ分析"],
    "environment": ["リモート可"],
    "desired_change": "創造性を活かせるAIプロダクト職へ移る"
  }
}
```

### `generateLayout(cardId)`

`generateStruct(cardId)`の結果をOpenAI APIへ送信し、文章なしのJSONとしてAGI判定結果を受け取り、`card_id`を付与した`layout_command.json`形式を返します。

## 完了条件チェック

### STEP1: 保存

1. Webアプリ画面でフォームを入力します。
2. 「保存」を押します。
3. `CARD_MASTER`に行が追加または更新されます。
4. 画面のSTRUCT JSON欄に生成結果が表示されます。

### STEP2: AGI判定

1. 「AGI判定実行」を押します。
2. `generateStruct(cardId)`でSTRUCTが生成されます。
3. `requestAgiLayout_(struct)`がOpenAI APIへ`{"struct": {...}}`を送信します。

### STEP3: layout_command表示

1. OpenAI APIのJSON応答を受け取ります。
2. `generateLayout(cardId)`が`layout_command.json`形式へ正規化します。
3. 画面の`layout_command.json`欄に表示されます。

## 今回やらないこと

- Unity接続
- Spatial接続
- 3D生成
- 認証機能
- 決済機能
- NFT機能

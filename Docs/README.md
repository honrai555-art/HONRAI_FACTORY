# HONRAI Career Card AGI Input System

Google Apps Script Webアプリとして動く、キャリアカードAGI入力装置のMVPです。
ユーザー入力を`CARD_MASTER`シートへ保存し、STRUCT JSONを生成してOpenAI APIへ送信し、街道WALK用の`layout_command.json`形式を画面表示します。

## 成果物

```text
/Frontend
  index.html
  style.css
  style.html   # GAS include('Frontend/style')用（style.cssと同内容）
  app.js
  app.html     # GAS include('Frontend/app')用（app.jsと同内容）
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

## GASデプロイ手順

### 1. Spreadsheetを作る

1. Google Driveで新しいGoogle Spreadsheetを作成します。
2. Spreadsheet名を任意で設定します（例: `HONRAI Career Card MVP`）。
3. Spreadsheet上部メニューの「拡張機能」→「Apps Script」を開きます。
4. `CARD_MASTER`シートは初回保存時に自動作成されます。手動作成する場合は、上記「Spreadsheet構造」のヘッダーを1行目に置いてください。

### 2. GASへコードをコピーする

Apps Scriptエディタで以下の4ファイルを作成し、GitHub上の同名ファイル内容をコピーします。

| Apps Script側のファイル名 | コピー元 | 内容 |
| --- | --- | --- |
| `Code.gs` | `GAS/Code.gs` | サーバー処理 |
| `Frontend/index.html` | `Frontend/index.html` | WebアプリHTML |
| `Frontend/style.html` | `Frontend/style.html`（または`Frontend/style.css`） | インラインCSS |
| `Frontend/app.html` | `Frontend/app.html`（または`Frontend/app.js`） | インラインJavaScript |

`GAS/Code.gs`の`doGet()`は`HtmlService.createTemplateFromFile('Frontend/index')`を読み込みます。
`Frontend/index.html`内では以下の2つを使ってCSS/JSをインライン展開します。

```html
<?!= include('Frontend/style'); ?>
<?!= include('Frontend/app'); ?>
```

そのため、Apps Script側ではHTMLファイルとして`Frontend/style.html`と`Frontend/app.html`を作成してください。`style.css`と`app.js`はGitHub上での編集・確認用ファイルで、GASへ貼り付ける内容は同じです。

### 3. Script Propertiesを設定する

Apps Scriptエディタ左メニューの「プロジェクトの設定」→「スクリプト プロパティ」で以下を登録します。

| プロパティ | 値 | 用途 |
| --- | --- | --- |
| `MOCK_AGI` | `true` | OpenAI APIキーなしで`buildMockLayout_()`を使うテストモード |
| `OPENAI_API_KEY` | OpenAI APIキー | 本番時のみ設定。`MOCK_AGI=true`の場合は未設定でOK |

最初の動作確認では必ず`MOCK_AGI=true`を設定してください。これによりOpenAI APIを呼ばず、モックの`layout_command.json`を表示できます。

### 4. Webアプリとしてデプロイする

1. Apps Scriptエディタ右上の「デプロイ」→「新しいデプロイ」を開きます。
2. 種類で「ウェブアプリ」を選択します。
3. 「実行ユーザー」は「自分」を選択します。
4. 「アクセスできるユーザー」は用途に合わせて選択します（まずは自分のみで確認するのがおすすめです）。
5. 「デプロイ」を押し、初回は権限承認を完了します。
6. 表示されたWebアプリURLを開きます。

### 5. テスト手順

1. WebアプリURLを開き、フォームへ以下のような値を入力します。
   - タイプ: `主人公`
   - 適合率: `72`
   - フェーズ: `探索`
   - 役割候補: `explorer`
   - やめる/残す/やる/経験/スキル/環境/望む変化: 任意
2. 「保存」ボタンを押します。
3. Spreadsheetに`CARD_MASTER`シートが作成され、1行追加されます。
4. `card_id`が`CM001`形式で発行されます。
5. 画面の`STRUCT JSON`欄に保存済みカードから生成したSTRUCTが表示されます。
6. 「AGI判定実行」ボタンを押します。
7. `generateStruct(cardId)`と`generateLayout(cardId)`が実行されます。
8. `MOCK_AGI=true`の場合はOpenAI APIを呼ばず、`buildMockLayout_()`由来の`layout_command.json`が画面に表示されます。

## デプロイ前チェックリスト

- GitHub上に`Frontend/index.html`, `Frontend/app.js`, `Frontend/style.css`, `GAS/Code.gs`が存在する。
- GAS側に`Frontend/index.html`, `Frontend/style.html`, `Frontend/app.html`, `Code.gs`を作成済み。
- `Script Properties`に`MOCK_AGI=true`を設定済み。
- 保存ボタンで`CARD_MASTER`に行が追加される。
- `CM001`形式の`card_id`が発行される。
- `STRUCT JSON`欄にJSONが表示される。
- `AGI判定実行`で`layout_command.json`欄にJSONが表示される。

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

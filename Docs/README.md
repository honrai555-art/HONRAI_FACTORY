# HONRAI Career Card AGI Input System

Google Apps Script Webアプリとして動く、キャリアカードAGI入力装置のMVPです。
ユーザー入力を`CARD_MASTER`シートへ保存し、STRUCT JSONを生成してOpenAI APIへ送信し、街道WALK用の`layout_command.json`形式を画面表示します。

## 成果物

```text
/Frontend
  index.html
  app.html        # Apps Script同期用: include('Frontend/app')で読み込む画面JS
  style.html      # Apps Script同期用: include('Frontend/style')で読み込むCSS
  app.js          # GitHub編集用のJS元ファイル
  style.css       # GitHub編集用のCSS元ファイル
/GAS
  Code.gs
/Docs
  README.md
/scripts
  deploy-gas.md
  gas-sync-check.md
/output
  sample_struct.json
  sample_layout_command.json
.clasp.json.example
appsscript.json
.claspignore
```

## GAS同期方針

GitHub上のCareer Card AGI Input SystemをGoogle Apps Scriptへ反映する方法は、次の優先順位で運用します。

1. **clasp同期を優先**します。
   - `.clasp.json.example`を`.clasp.json`へコピーし、自分のScript IDを設定して`clasp push`します。
   - `.clasp.json`本体には個人の`scriptId`が入るため、GitHubへコミットしません。
   - `.claspignore`により、GASへ必要なファイルだけを同期します。
2. **clasp認証が難しい場合は手動コピー**します。
   - このREADMEの「GASデプロイ手順」に沿ってApps Scriptエディタへ貼り付けます。
3. **将来的にGitHub Actions自動デプロイへ拡張**できます。
   - 自動デプロイには`CLASP_CREDENTIALS`、`CLASP_TOKEN`、`SCRIPT_ID`のSecretsが必要です。
   - OAuth認証とトークン管理が複雑なため、今回は必須にしていません。

詳細は`scripts/deploy-gas.md`、同期前チェックは`scripts/gas-sync-check.md`を参照してください。


## 進路エラー診断GASの所在

進路エラー診断の既存GASは、次のGoogle Slides「診断結果同期用」に紐づくApps Scriptプロジェクト内にあります。

- Google Slides: https://docs.google.com/presentation/d/1GyGTyDwCgBqufNxxHJKZ2Qmvw669KIOrG0ucrhTq4FM/edit?slide=id.g3d58b00a9cd_0_0#slide=id.g3d58b00a9cd_0_0

このSlides内のGASを同期先または移植元として使う場合は、Slidesを開いて「拡張機能」→「Apps Script」から紐づくGASプロジェクトを開きます。claspを使う場合は、そのGASプロジェクトの「プロジェクトの設定」→「スクリプト ID」を`.clasp.json`の`scriptId`へ設定してください。

注意: このリポジトリの`GAS/Code.gs`はSpreadsheet上の`CARD_MASTER`へ保存するWebアプリ実装です。Slides側の既存GASを上書きする前に、Apps Scriptエディタで現行コードをバックアップし、`generateStruct()`と`generateLayout()`のJSON構造を変更しないことを確認してください。

## GASで必要なファイル名

Apps Script上では、次の構成になるようにします。

```text
Code.gs
Frontend/index.html
Frontend/app.html
Frontend/style.html
```

GitHub上では管理しやすいように、サーバーコードを`GAS/Code.gs`に置いています。手動コピー時は`GAS/Code.gs`の内容をApps Script側の`Code.gs`へ貼り付けてください。

`Frontend/index.html`は以下のincludeでCSS/JSをインライン化します。

```html
<?!= include('Frontend/style'); ?>
<?!= include('Frontend/app'); ?>
```

`GAS/Code.gs`の`include(filename)`が`HtmlService.createHtmlOutputFromFile(filename).getContent()`を返すため、Apps Script側に`Frontend/app.html`と`Frontend/style.html`を作成しておけば正しく動作します。

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

### A. 手動コピーでWebアプリ公開する場合

1. Googleスプレッドシートを新規作成します。
2. 「拡張機能」→「Apps Script」を開きます。
3. `GAS/Code.gs`をApps Script側の`Code.gs`に貼り付けます。
4. `Frontend/index.html`を作成して貼り付けます。
   - Apps Scriptエディタでは「ファイルを追加」→「HTML」を選び、ファイル名を`Frontend/index`にします。
5. `Frontend/app.html`を作成して貼り付けます。
   - Apps Scriptエディタではファイル名を`Frontend/app`にします。
6. `Frontend/style.html`を作成して貼り付けます。
   - Apps Scriptエディタではファイル名を`Frontend/style`にします。
7. Script Propertiesに以下を設定します。

   ```text
   MOCK_AGI=true
   ```

   OpenAI APIを使う本番確認では、追加で`OPENAI_API_KEY`も設定します。
8. 「デプロイ」→「新しいデプロイ」を選択します。
9. 種類は「ウェブアプリ」を選択します。
10. 実行ユーザーは「自分」を選択します。
11. アクセスできるユーザーは「自分」、または「リンクを知っている全員」を選択します。
12. デプロイしてWebアプリURLを取得します。

### B. claspで同期する場合

1. Apps Script APIを有効化します。
2. `npm install -g @google/clasp`でclaspをインストールします。
3. `clasp login`でGoogleアカウントへログインします。
4. `.clasp.json.example`を`.clasp.json`へコピーします。
5. `.clasp.json`の`scriptId`へ自分のScript IDを設定します。
6. `clasp status`で同期対象を確認します。
7. `clasp push`でGASへ反映します。
8. Script Propertiesに`MOCK_AGI=true`を設定し、必要に応じて`OPENAI_API_KEY`も設定します。
9. Apps ScriptエディタからWebアプリとしてデプロイします。

## テスト手順

WebアプリURL取得後、以下を確認します。

1. WebアプリURLを開ける。
2. フォームが表示される。
3. 保存ボタンを押すと`CARD_MASTER`シートが自動作成される。
4. `CM001`形式の`card_id`が発行される。
5. STRUCT JSONが画面に表示される。
6. Script Propertiesで`MOCK_AGI=true`になっている状態で「AGI判定実行」を押すと、`layout_command.json`が表示される。

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
`MOCK_AGI=true`の場合はOpenAI APIを呼ばず、`buildMockLayout_()`の結果から確認用JSONを返します。

## 完了条件チェック

### STEP1: 保存

1. Webアプリ画面でフォームを入力します。
2. 「保存」を押します。
3. `CARD_MASTER`に行が追加または更新されます。
4. 画面のSTRUCT JSON欄に生成結果が表示されます。

### STEP2: AGI判定

1. 「AGI判定実行」を押します。
2. `generateStruct(cardId)`でSTRUCTが生成されます。
3. `MOCK_AGI=true`の場合はモックJSONを返します。
4. `MOCK_AGI`が`true`でない場合は、`requestAgiLayout_(struct)`がOpenAI APIへ`{"struct": {...}}`を送信します。

### STEP3: layout_command表示

1. OpenAI APIまたはモックのJSON応答を受け取ります。
2. `generateLayout(cardId)`が`layout_command.json`形式へ正規化します。
3. 画面の`layout_command.json`欄に表示されます。

## 今回やらないこと

- GitHub ActionsによるGAS自動デプロイ
- Unity接続
- Spatial接続
- 3D生成
- 認証機能
- 決済機能
- NFT機能

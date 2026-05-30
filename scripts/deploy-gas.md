# GAS同期・デプロイ手順（clasp優先）

Career Card AGI Input SystemをGitHub管理ファイルからGoogle Apps Scriptへ反映する手順です。

## 対象ファイル

| GitHub上のファイル | Apps Script上のファイル名 | 用途 |
| --- | --- | --- |
| `GAS/Code.gs` | `GAS/Code.gs`（手動コピー時は`Code.gs`へ貼り付け） | Webアプリ / Spreadsheet操作 / AGI判定 |
| `Frontend/index.html` | `Frontend/index.html` | Webアプリ画面 |
| `Frontend/app.html` | `Frontend/app.html` | `include('Frontend/app')`で読み込む画面JS |
| `Frontend/style.html` | `Frontend/style.html` | `include('Frontend/style')`で読み込むCSS |
| `appsscript.json` | `appsscript.json` | Apps Script manifest |

`Frontend/app.js`と`Frontend/style.css`は編集しやすい元ファイルとして残しています。Apps Scriptへ同期する場合は、`Frontend/app.html`と`Frontend/style.html`を同期対象にしてください。


## 進路エラー診断SlidesのGASを使う場合

進路エラー診断の既存GASは、Google Slides「診断結果同期用」に紐づくApps Scriptプロジェクト内にあります。

- https://docs.google.com/presentation/d/1GyGTyDwCgBqufNxxHJKZ2Qmvw669KIOrG0ucrhTq4FM/edit?slide=id.g3d58b00a9cd_0_0#slide=id.g3d58b00a9cd_0_0

この既存GASへ同期する場合は、Slidesを開いて「拡張機能」→「Apps Script」を選択し、Apps Scriptの「プロジェクトの設定」からScript IDを取得します。そのScript IDをローカルの`.clasp.json`へ設定してから`clasp status`で差分を確認し、問題がなければ`clasp push`します。

既存SlidesのGASを壊さないため、初回は必ずApps Scriptエディタ側で現行コードをコピー保存してから同期してください。

## 1. claspで同期する場合

1. Apps Script APIを有効化します。
   - https://script.google.com/home/usersettings
2. claspをインストールします。

   ```bash
   npm install -g @google/clasp
   ```

3. Googleアカウントへログインします。

   ```bash
   clasp login
   ```

4. Spreadsheetに紐づくApps Scriptプロジェクトを作成、または既存プロジェクトを開いてScript IDを控えます。
5. `.clasp.json.example`をコピーして`.clasp.json`を作成します。

   ```bash
   cp .clasp.json.example .clasp.json
   ```

6. `.clasp.json`の`YOUR_SCRIPT_ID_HERE`を自分のScript IDに置き換えます。
   - `.clasp.json`には個人のScript IDが入るため、Git管理へ追加しないでください。
7. 同期対象を確認します。

   ```bash
   clasp status
   ```

8. GASへ反映します。

   ```bash
   clasp push
   ```

`.claspignore`により、GASへ必要な`appsscript.json`、`GAS/Code.gs`、`Frontend/index.html`、`Frontend/app.html`、`Frontend/style.html`のみを同期します。

## 2. 手動コピーする場合

clasp認証が難しい場合は、`Docs/README.md`の「GASデプロイ手順」に従ってApps Scriptエディタへ手動コピーしてください。

## 3. 将来のGitHub Actions自動デプロイ

GitHub Actionsから`clasp push`または`clasp deploy`を実行する構成に拡張できます。ただし、以下のSecretsが必要です。

- `CLASP_CREDENTIALS`
- `CLASP_TOKEN`
- `SCRIPT_ID`

OAuthトークンとApps Script API認証の運用が複雑なため、今回の完成条件では自動デプロイは必須にしていません。

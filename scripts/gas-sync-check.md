# GAS同期前チェック

GASへ同期する前に確認するチェックリストです。

## 必須ファイル

- `.clasp.json.example`
- `appsscript.json`
- `.claspignore`
- `GAS/Code.gs`
- `Frontend/index.html`
- `Frontend/app.html`
- `Frontend/style.html`


## 進路エラー診断Slides確認

進路エラー診断の既存GASを同期先にする場合は、次のSlidesから「拡張機能」→「Apps Script」を開いて対象プロジェクトを確認します。

- https://docs.google.com/presentation/d/1GyGTyDwCgBqufNxxHJKZ2Qmvw669KIOrG0ucrhTq4FM/edit?slide=id.g3d58b00a9cd_0_0#slide=id.g3d58b00a9cd_0_0

同期前に確認すること:

- Apps Scriptエディタで現行GASをバックアップした
- Script IDを`.clasp.json`に設定した
- `clasp status`で上書き対象ファイルを確認した
- `generateStruct()`と`generateLayout()`のJSON構造を変更していない

## include確認

`Frontend/index.html`には以下のincludeが必要です。

```html
<?!= include('Frontend/style'); ?>
<?!= include('Frontend/app'); ?>
```

`GAS/Code.gs`には以下の関数が必要です。

```javascript
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}
```

## MOCK_AGI確認

Apps ScriptのScript Propertiesに以下を設定すると、OpenAI APIキーなしでAGI判定画面を確認できます。

```text
MOCK_AGI=true
```

この状態で「AGI判定実行」を押すと、`buildMockLayout_()`由来の`layout_command.json`が表示されます。

## ローカルでできる軽量チェック

```bash
python -m json.tool appsscript.json >/dev/null
python -m json.tool .clasp.json.example >/dev/null
rg -n "include\('Frontend/(app|style)'\)|function include|MOCK_AGI|CARD_MASTER" GAS Frontend Docs scripts
```

## Apps Script上での最終確認

- WebアプリURLを開ける
- フォームが表示される
- 保存ボタンで`CARD_MASTER`シートが自動作成される
- `CM001`形式の`card_id`が発行される
- STRUCT JSONが画面に表示される
- `MOCK_AGI=true`でAGI判定実行を押すと`layout_command.json`が表示される

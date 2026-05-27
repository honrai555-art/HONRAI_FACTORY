# Windows + PowerShell 初期設定

Discord bot 開発と GitHub 運用のための、Windows 側の準備手順です。

## 1. PowerShell の確認

```powershell
$PSVersionTable.PSVersion
```

PowerShell 5.1 以上、または PowerShell 7（`pwsh`）が使えれば OK です。

## 2. Git のインストール確認

```powershell
git --version
```

未インストールの場合: https://git-scm.com/download/win

初回のみ、名前とメールを設定（GitHub アカウントに合わせる）:

```powershell
git config --global user.name "あなたの名前"
git config --global user.email "you@example.com"
```

## 3. Node.js のインストール確認

```powershell
node --version
npm --version
```

未インストールの場合: https://nodejs.org/ （LTS 推奨）

## 4. Cursor の設定（任意）

- デフォルトターミナルを PowerShell にする
- プロジェクトルート `HONRAI_FACTORY` を Cursor で開く
- `.cursorrules` が自動的に読み込まれる

## 5. 環境変数ファイル（Bot 開発時）

Bot 用フォルダを作ったら、ルートまたは bot フォルダに:

```
.env.example   … キー名だけ（GitHub に commit して OK）
.env           … 実際のトークン（.gitignore に入れ、commit 禁止）
```

PowerShell でコピー:

```powershell
Copy-Item .env.example .env
notepad .env
```

## 6. よく使う PowerShell コマンド

| コマンド | 意味 |
|----------|------|
| `cd パス` | フォルダ移動 |
| `ls` / `Get-ChildItem` | ファイル一覧 |
| `mkdir 名前` | フォルダ作成 |
| `Copy-Item A B` | ファイルコピー |

パスにスペースがある場合は引用符で囲みます:

```powershell
cd "C:\Users\honra\HONRAI_FACTORY"
```

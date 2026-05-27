# GitHub 基本運用（初心者向け）

HONRAI_FACTORY は **GitHub を正本** として運用します。

## 用語の整理

| 用語 | 意味 |
|------|------|
| リポジトリ | プロジェクトのフォルダ + 履歴 |
| commit | 変更の保存（スナップショット） |
| push | ローカルの commit を GitHub に送る |
| pull | GitHub の最新をローカルに取り込む |
| ブランチ | 本流（main）から分岐した作業線 |

## 初回: GitHub に上げる

```powershell
cd C:\Users\honra\HONRAI_FACTORY

# 状態確認
git status

# すべてステージ
git add .

# 保存（メッセージは内容が分かるもの）
git commit -m "docs: AI工場ルールとDiscord bot開発の土台を追加"

# main ブランチ名（既に main なら不要）
git branch -M main

# リモート登録（URL は自分のリポジトリに置き換え）
git remote add origin https://github.com/<ユーザー名>/HONRAI_FACTORY.git

# 初回 push
git push -u origin main
```

## 日常: 変更を送る

```powershell
git status
git add .
git commit -m "feat: 〇〇を追加"
git push
```

## 機能開発: ブランチを切る（推奨）

```powershell
git checkout -b feature/add-ping-command
# ... 作業 ...
git add .
git commit -m "feat: /ping コマンドを追加"
git push -u origin feature/add-ping-command
```

GitHub 上で **Pull Request（PR）** を作成し、内容を確認してから main にマージします。

## やってはいけないこと

- Bot トークンや `.env` を commit する
- `git push --force` を main に対して実行する（特別な理由がない限り）
- AI に確認なしで push させる

## トラブル: push が拒否された

```powershell
git pull --rebase origin main
git push
```

競合（conflict）が出た場合は、該当ファイルを手動で直してから:

```powershell
git add .
git rebase --continue
git push
```

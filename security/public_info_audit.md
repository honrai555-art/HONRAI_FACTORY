# 公開情報・秘密情報監査レポート

作成日: 2026-05-30  
対象: HONRAI_FACTORY リポジトリ（Git管理対象ファイル、作業ツリー内のテキスト、Git履歴の直近/著者情報）  
目的: 小縄泰平／HONRAI関連の公開情報を棚卸しし、漏洩リスク・公開範囲・削除/非公開化すべき情報を整理する。

## 1. 監査方法

以下を中心に、勝手な削除・改変は行わず監査レポートのみ作成した。

- リポジトリ内テキスト検索
  - メールアドレス正規表現
  - 電話番号らしき正規表現
  - `Apple ID`, `iCloud`, `Gmail`, `Outlook`, `PayPal`, `Stripe`
  - `OPENAI_API_KEY`, `DISCORD_TOKEN`, `DISCORD_WEBHOOK_URL`, `API_KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `.env`
  - URL (`http://`, `https://`)
  - `小縄泰平`, `小縄`, `泰平`, `Kowana`, `Tahei`, `HONRAI`, `honrai`
- Git管理ファイルの確認
  - `.env` 系ファイルが Git 管理されていないか
  - Git履歴上の author/committer メールの確認
- 画像・スクリーンショット候補の確認
  - Git管理対象の画像拡張子および `screenshot`, `screen`, `capture`, `preview` を含むファイル名を確認

> 注: `bot/node_modules/` と `tools/comfyui/` は依存物・外部ツール由来のノイズが非常に多いため、主なリスク判定では除外した。ただし、Git管理対象画像の一覧確認では vendor 配下の画像も候補として把握した。

## 2. 総合評価

- 実値の API キー、Discord Bot Token、Discord Webhook URL、Stripe/PayPal 等の決済キーは、今回の検索範囲では確認されなかった。
- `.env` 実体は Git 管理されておらず、Git管理対象は `bot/.env.example` のみだった。
- `bot/.env.example` には `DISCORD_TOKEN=your_bot_token_here` などのプレースホルダーが含まれる。実値ではないため低リスクだが、サンプルであることを維持する必要がある。
- Git履歴の author 情報に個人/ブランドに紐づく可能性がある Gmail アドレス `honrai555@gmail.com` が確認された。GitHub公開リポジトリでは履歴から見える可能性が高いため、中〜高リスク。
- `.gitmodules` に GitHub アカウント名 `honrai555-art` を含む公開リポジトリ URL が確認された。ブランド/運用主体の公開アカウントとして残すなら低〜中リスク、個人と紐づけたくない場合は中リスク。
- Windows のローカルユーザーパス `C:\Users\honra\HONRAI_FACTORY` が複数箇所にある。住所・電話ほどの高リスクではないが、ローカルユーザー名や環境を推測されるため中リスク。
- README/ドキュメントには、実値ではないサンプル Webhook URL や OpenAI API Key 形式のダミーがある。誤って実値に置き換える運用事故を避けるため、明確に「ダミー」と書くのが望ましい。
- 小縄泰平の氏名そのものは、リポジトリ内テキスト検索では確認されなかった。

## 3. 観点別の棚卸し

### 3.1 氏名・屋号・ブランド名

| 種別 | 検出内容 | 主な場所 | 危険度 | 対応案 |
|---|---|---|---|---|
| ブランド名 | `HONRAI_FACTORY`, `HONRAI`, `honrai_kun` など | README、AGENTS、スクリプト、Unity設定など多数 | 低 | 公開ブランドとして意図しているなら残してよい。個人と紐づけたくない場合はプロフィールや外部URL側での紐づけを制限する。 |
| 氏名 | `小縄泰平`, `小縄`, `泰平`, `Kowana`, `Tahei` | 該当なし | 低 | なし。今後も個人名を README・設定・画像に入れない。 |
| Git author名 | `ホンライ`, `honrai555-art` | Git履歴 | 中 | 公開リポジトリでは履歴に残る。今後は GitHub noreply メールと公開用ユーザー名を使う。履歴改変は影響が大きいため、必要性を判断してから実施。 |

### 3.2 メールアドレス

| 検出内容 | 場所 | 該当箇所 | 危険度 | 対応案 |
|---|---|---|---|---|
| `you@example.com` | `workflow/powershell-setup.md` | Git設定例 | 低 | サンプルメールであり残してよい。実メールへ置き換えない。 |
| `honrai555@gmail.com` | Git履歴 author/committer | `honrai555-art <honrai555@gmail.com>`, `ホンライ <honrai555@gmail.com>` | 中〜高 | 公開したくない個人メールなら GitHub noreply メールへ変更し、今後の commit では使わない。過去履歴から消すには履歴書き換えが必要。 |
| `cursoragent@cursor.com` | Git履歴 author/committer | Cursor Agent のコミット | 低 | ツール由来の公開情報として残してよい。 |

### 3.3 電話番号

| 検出内容 | 場所 | 危険度 | 対応案 |
|---|---|---|---|
| 実電話番号らしき情報は確認されず | 該当なし | 低 | 今後も README、docs、画像、サンプルCSV等に電話番号を入れない。 |
| 数字列の誤検出 | CSSカラーコード、Unityの小数/ゼロ列 | 低 | 電話番号ではないため対応不要。 |

### 3.4 SNSリンク

| 検出内容 | 場所 | 危険度 | 対応案 |
|---|---|---|---|
| X/Twitter, Instagram, Facebook, YouTube, TikTok 等のSNSプロフィールURLは確認されず | 該当なし | 低 | 公開したい公式SNSのみ README に掲載。個人SNSは掲載しない。 |

### 3.5 WebサイトURL

| 検出内容 | 場所 | 危険度 | 対応案 |
|---|---|---|---|
| `https://github.com/honrai555-art/career-card-gas.git` | `.gitmodules` | 中 | 公開GitHubアカウント名が露出。ブランド用なら残してよい。個人アカウントと切り離すなら organization/別アカウントへ移行。 |
| `https://github.com/<あなたのユーザー名>/HONRAI_FACTORY.git` | `README.md`, `workflow/github-basics.md` | 低 | プレースホルダーなので残してよい。 |
| `https://discord.com/api/webhooks/XXXXXXXX/YYYYYYYY` | `scripts/README.md` | 低 | ダミーURL。残してよいが「実値ではない」と明記推奨。 |
| `https://open.larksuite.com/open-apis/bot/v2/hook/xxx...` | `lark/README.md` | 低 | ダミーURL。残してよいが「実値ではない」と明記推奨。 |
| `https://api.openai.com/...`, `https://discord.com/developers/applications`, `https://git-scm.com/...`, `https://nodejs.org/` 等 | README、コード、設定例 | 低 | 公式サービスURLのため残してよい。 |
| Google Drive/Sheets の `xxx`, `yyy`, `zzz`, `aaa`, `bbb` サンプルURL | `lark/base/manufacturing_line_base_sample.csv` | 低 | ダミー。残してよいが、実Drive URLへ置換しない。 |

### 3.6 GitHub上の公開情報

| 検出内容 | 場所 | 危険度 | 対応案 |
|---|---|---|---|
| GitHubアカウント名 `honrai555-art` | `.gitmodules`, Git履歴 author名 | 中 | ブランド/屋号用なら公開情報として残せる。個人と分離したい場合は、organization化・別リポジトリ化・author設定変更を検討。 |
| Git履歴上の Gmail | Git履歴 author/committer | 中〜高 | 今後の commit author email を GitHub noreply へ変更。過去分は必要なら履歴書き換え。 |
| README の clone URL `<あなたのユーザー名>` | README | 低 | プレースホルダー。残してよい。 |

### 3.7 APIキー・トークン・Webhook URLの露出有無

| 検出内容 | 場所 | 該当箇所 | 危険度 | 対応案 |
|---|---|---|---|---|
| `DISCORD_TOKEN=your_bot_token_here` | `bot/.env.example` | サンプル値 | 低 | 実値ではないため残してよい。`.env.example` のまま維持し、実トークンを入れない。 |
| `OPENAI_API_KEY=` | `bot/.env.example` ほか | 空値/環境変数参照 | 低 | 実値なし。残してよい。 |
| `DISCORD_WEBHOOK_URL=` | `bot/.env.example` ほか | 空値/環境変数参照 | 低 | 実値なし。残してよい。 |
| `set OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | `scripts/gpt/README.md` | ダミー形式 | 低〜中 | ダミーだが実キー形式に見える。`sk-REPLACE_WITH_YOUR_KEY` 等へ変更案を検討。今回は未変更。 |
| `set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/XXXXXXXX/YYYYYYYY` | `scripts/README.md` | ダミーURL | 低〜中 | ダミーだがWebhook形式に見える。`<YOUR_WEBHOOK_URL>` 表記へ変更案を検討。今回は未変更。 |
| Lark Webhook ダミーURL | `lark/README.md`, `lark/scripts/*` | `xxx...` など | 低 | ダミー。残してよい。 |
| Unity `ps4NPTitleSecret`, `metroCertificatePassword` | Unity ProjectSettings | 空値 | 低 | 空値。残してよい。 |

### 3.8 `.env` や秘密情報ファイルがGit管理されていないか

| 確認内容 | 結果 | 危険度 | 対応案 |
|---|---|---|---|
| Git管理対象の `.env` 実体 | `bot/.env.example` のみ | 低 | 現状維持。`.env.example` はキー名だけにし、実値を入れない。 |
| `.gitignore` | `.env`, `bot/.env`, `*.env`, `.env.local`, `.env.*.local` を除外済み | 低 | 良好。`lark/config/lark_config.json` も除外済み。 |
| 作業ツリー内の `.env` 実体 | `bot/.env.example` のみ確認 | 低 | 良好。 |

### 3.9 READMEやドキュメント内の個人情報

| 検出内容 | 場所 | 危険度 | 対応案 |
|---|---|---|---|
| `C:\Users\honra\HONRAI_FACTORY` | `run_factory_bot.bat`, `workflow/blender-unity-pipeline.md`, `workflow/github-basics.md`, `workflow/asset-watchdog.md`, `workflow/powershell-setup.md`, `scripts/import_generated_assets.ps1` など | 中 | ローカルユーザー名 `honra` を公開したくない場合、`%USERPROFILE%\HONRAI_FACTORY` や `<PROJECT_ROOT>` に置換する。ただし今回は監査のみで未変更。 |
| Git設定例 `you@example.com` | `workflow/powershell-setup.md` | 低 | サンプルなので残してよい。 |
| 個人の住所・電話・Apple ID・iCloud・Gmail本文・Outlook・PayPal・Stripe は確認されず | 該当なし | 低 | 今後もドキュメントやサンプルデータに入れない。 |

### 3.10 スクリーンショット画像内の個人情報

| 確認内容 | 結果 | 危険度 | 対応案 |
|---|---|---|---|
| Git管理対象の画像ファイル | 主に `tools/comfyui/` 配下のサンプルPNGのみ確認 | 低 | vendorサンプル画像であり、HONRAI個人情報のスクリーンショットは確認されず。 |
| `screenshot`, `screen`, `capture`, `preview` を含むファイル名 | `screen_design.md`, preview関連スクリプト、ComfyUI previewコード等 | 低 | 実スクリーンショット画像ではない。対応不要。 |

## 4. 見つかった文字列別チェック結果

| 検索対象 | 結果 | 主な該当 | 危険度 | 対応案 |
|---|---|---|---|---|
| メールアドレス | あり | `you@example.com`（サンプル）、Git履歴の `honrai555@gmail.com` | 低〜高 | サンプルはOK。Git履歴のGmailは公開したくなければ今後noreplyへ変更。 |
| 電話番号 | 実電話番号なし | CSSカラー、Unity数値の誤検出のみ | 低 | 対応不要。 |
| Apple ID | なし | - | 低 | 対応不要。 |
| iCloud | なし | - | 低 | 対応不要。 |
| Gmail | Git履歴にあり | `honrai555@gmail.com` | 中〜高 | 今後のGit author emailを変更。 |
| Outlook | なし | - | 低 | 対応不要。 |
| PayPal | なし | - | 低 | 対応不要。 |
| Stripe | なし | - | 低 | 対応不要。 |
| OPENAI_API_KEY | あり | README、`bot/.env.example`, GAS, GPTスクリプト | 低 | 実値なし。環境変数名として残してよい。 |
| DISCORD_TOKEN | あり | `AGENTS.md`, `bot/.env.example`, botコード | 低 | 実値なし。環境変数名として残してよい。 |
| DISCORD_WEBHOOK_URL | あり | README、`bot/.env.example`, scripts, Unity Editor scripts | 低 | 実値なし。環境変数名として残してよい。 |
| API_KEY | あり | `OPENAI_API_KEY` の一部、コード引数名 | 低 | 実値なし。 |
| TOKEN | あり | `DISCORD_TOKEN`、コード変数名、ドキュメント | 低 | 実値なし。 |
| SECRET | あり | `AGENTS.md` の見出し、Unity空値、Client Secret注意書き | 低 | 実値なし。 |
| PASSWORD | あり | Unity `metroCertificatePassword:` 空値 | 低 | 空値。 |
| `.env` | あり | `.gitignore`, README, `bot/.env.example`, scripts | 低 | `.env` 実体はGit管理されていない。 |

## 5. 削除/非公開化した方がよい情報

優先度順:

1. **Git履歴の Gmail アドレス `honrai555@gmail.com`**
   - 公開リポジトリでは commit author として見える可能性がある。
   - まず今後の Git 設定を GitHub noreply に変更する。
   - 既存履歴から完全に消す場合は、リポジトリ利用者への影響を理解したうえで履歴書き換えを行う。
2. **ローカルユーザーパス `C:\Users\honra\HONRAI_FACTORY`**
   - 個人PCのユーザー名/環境推測につながる。
   - ドキュメントは `<PROJECT_ROOT>`、`%USERPROFILE%\HONRAI_FACTORY`、`$env:USERPROFILE\HONRAI_FACTORY` へ置換するのが望ましい。
3. **実キー形式に近いダミー例**
   - `sk-xxxxxxxx...` や Discord Webhook のダミーURLは実値と誤認されやすい。
   - `OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>`、`DISCORD_WEBHOOK_URL=<YOUR_DISCORD_WEBHOOK_URL>` のように、明らかなプレースホルダーへ統一する。
4. **GitHubアカウント名 `honrai555-art` の公開範囲**
   - ブランド用アカウントとして公開するなら問題なし。
   - 個人と切り離したい場合は organization や別アカウントへ移行を検討する。

## 6. 残してよい公開情報

- `HONRAI_FACTORY`, `HONRAI`, `honrai_kun` などのブランド/プロダクト名
- 公式サービスURL
  - OpenAI API endpoint
  - Discord Developer Portal
  - Node.js / Python / Git / Cursor などの公式URL
- `.env.example` に含まれるキー名と空値/明確なサンプル値
- READMEの運用方針「トークン等は `.env` に置き、GitHub に上げない」
- Lark/Discord/Google Drive等の `xxx` や `<あなたのユーザー名>` を含む明確なダミーURL
- Unity ProjectSettings の空値 secret/password フィールド

## 7. READMEへ追記する案

README の「ルールの要点」付近に、以下の文言を追記する案:

> 秘密情報・個人情報はGitHubに保存しない。APIキー、トークン、Webhook URL、電話番号、Apple ID、個人メールアドレスは `.env` または外部の安全な保管場所で管理する。

今回はユーザー指示に従い、READMEへの実追記は行っていない。

## 8. 今後の運用ルール

1. **秘密情報は Git に入れない**
   - APIキー、トークン、Webhook URL、パスワード、Client Secret、Apple ID、個人メール、電話番号は `.env` または外部の安全な保管場所で管理する。
2. **`.env.example` はキー名だけにする**
   - 実値・実URL・本物に見える長いトークンを入れない。
3. **Git author email は公開用に固定する**
   - 個人メールを避け、GitHub noreply またはブランド用メールを使う。
4. **ローカル絶対パスをドキュメントに書かない**
   - `C:\Users\名前\...` ではなく `<PROJECT_ROOT>` や `%USERPROFILE%` を使う。
5. **スクリーンショット投入前に目視/OCR確認する**
   - ブラウザのアカウント名、メール、通知、チャンネルURL、Webhook URL、OSユーザー名が写っていないか確認する。
6. **PR前のセルフチェックを行う**
   - `rg` で `OPENAI_API_KEY|DISCORD_TOKEN|DISCORD_WEBHOOK_URL|SECRET|PASSWORD|Apple ID|iCloud|Gmail|PayPal|Stripe|\.env` を確認する。
7. **漏洩時は即ローテーションする**
   - Discord Token は Reset、Webhook は削除/再発行、OpenAI/Stripe/PayPal等は管理画面で revoke/rotate する。
8. **公開用/非公開用の情報を分離する**
   - ブランド名・公式URLは公開可。個人連絡先・運用アカウント・内部URL・顧客データは非公開にする。

## 9. 次の判断ポイント

- `honrai555@gmail.com` を公開履歴から消す必要があるか。
- `honrai555-art` を個人アカウントとして扱うか、ブランド公開アカウントとして扱うか。
- `C:\Users\honra\HONRAI_FACTORY` のようなローカルパスを削除/置換するか。
- READMEへ追記案を実際に反映するか。
- ダミーキー/ダミーWebhook例を、より安全なプレースホルダー表記へ統一するか。

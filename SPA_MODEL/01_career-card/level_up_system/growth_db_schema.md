# growth_db_schema.md

## 成長DBの目的

成長DBは、ユーザーが自分で設定したゴールに向かって更新し続けた記録を蓄積するためのデータベースです。

Ver3では「相応しい仕事」だけに固定せず、学習習慣、志望校、資格、講師化、作品化、収益化など、ユーザーごとの「相応しい次のステージ」を扱います。

## テーブル方針

最初は1レコードで運用しやすいように、ユーザー、ゴール、行動、キャリアブロック、レベル状態を同じ行にまとめます。実装が進んだら、`user_goals`、`career_blocks`、`action_logs`、`level_histories` に分割できます。

## 必須カラム

| カラム名 | 型 | 説明 | 更新タイミング |
|---|---|---|---|
| user_id | string | ユーザーID | 初回登録時 |
| user_name | string | 表示名 | 初回登録時 / プロフィール更新時 |
| childhood_dream | text | 子供の頃の夢、好きだったこと | 初回診断 / 再診断時 |
| honrai_theme | text | 本来性テーマ | 初回診断 / 再診断時 |
| current_state | text | 今の状態。ユーザーの現在地・悩み | フォーム入力時 / 再診断時 |
| next_stage | text | ユーザーが設定した「相応しい次のステージ」。Ver3の最優先項目で最終決定者はユーザー。`user_goal` の正式な入力元 | ゴール設定 / ゴール修正時 |
| next_stage_source | string | 次ステージ候補の出どころ。user / diagnosis / mentor。提案由来でも最終確定はユーザー | ゴール設定 / ゴール修正時 |
| user_goal | text | 成長DB上の正式ゴール。`next_stage` の確定値を保持（後方互換のため継続） | ゴール設定 / ゴール修正時 |
| goal_category | string | 仕事化、学習習慣、志望校、資格など | ゴール設定 / ゴール修正時 |
| goal_reason | text | なぜそのゴールに向かうのか | ゴール設定 / ゴール修正時 |
| desired_state | text | ゴール達成時の状態 | ゴール設定 / ゴール修正時 |
| success_condition | text | 達成判定条件 | ゴール設定 / ゴール修正時 |
| deadline | date | 達成期限 | ゴール設定 / ゴール修正時 |
| current_gap | text | 現在地とゴールの差分 | 診断 / 行動更新時 |
| goal_progress_rate | integer | ゴール進捗率。0〜100 | 行動記録 / ブロック生成時 |
| honrai_alignment_score | integer | ゴールと本来性の一致率。0〜100 | 診断 / ゴール修正時 |
| route_error_rate | integer | ゴールと本来性・現在行動のズレ率。0〜100 | 診断 / 行動更新時 |
| route_error_type | string | 進路エラータイプ。ズレなし / 目標未設定型 / 本来性ズレ型 / 行動停滞型 / 過負荷型 / 方向転換型 | 診断 / 行動更新時 |
| current_level | integer | 現在レベル。Lv.1〜Lv.10 | レベルアップ時 |
| current_rank | string | 冠位 | レベルアップ時 |
| next_quest | text | 次に行うクエスト | 診断 / レベルアップ / 行動更新時 |
| career_block_type | string | 分かった、できた、経験、仕事化 | 行動記録後 |
| career_block_summary | text | 獲得したキャリアブロックの要約 | 行動記録後 |
| action_log | text | 今日やったこと | 行動入力時 |
| insight_log | text | 気付き | 行動入力時 |
| result_log | text | 成果、反応、学習結果 | 行動入力時 |
| workization_status | string | 未着手、試作、仮説、初回提供、継続など | 仕事化ゴール更新時 |
| goal_status | string | 未設定、設定済み、実行中、達成、修正中、中止 | ゴール状態更新時 |
| level_up_reason | text | レベルアップ理由 | レベルアップ時 |
| updated_at | datetime | 最終更新日時 | 全更新時 |

## route_error_rate の扱い

進路エラー率は、失敗度ではなく「ゴール・本来性・現在行動のズレを修正する必要度」です。

| 値 | 状態 | 推奨アクション |
|---:|---|---|
| 0〜20 | ゴールと行動がかなり一致 | 行動継続、記録強化 |
| 21〜50 | 小さなズレがある | next_quest を軽く修正 |
| 51〜80 | ゴール理由や行動がズレている | goal_reason / current_gap を再確認 |
| 81〜100 | ゴール再設計が必要 | goal_status を修正中にして診断し直す |

## route_error_type の扱い

進路エラータイプは `route_error_rate`（数値）を補足する分類です。責める分類ではなく、どの修正が必要かを示します。詳細は `form_design.md` を参照します。

| タイプ | 説明 | 主な修正アクション |
|---|---|---|
| ズレなし | ゴールと行動が一致している | 行動継続、記録強化 |
| 目標未設定型 | 相応しい次のステージが未設定 | next_stage を設定する |
| 本来性ズレ型 | ゴールが本来性と離れている | goal_reason / next_stage を見直す |
| 行動停滞型 | ゴールはあるが行動が止まっている | next_quest を軽くして1行動だけ実行 |
| 過負荷型 | 目標や行動が大きすぎる | success_condition を小さく分解する |
| 方向転換型 | ゴール自体を変えたほうがよい | goal_status を修正中にして再設定 |

## フォーム入力項目との対応

ユーザー記入フォーム（`form_design.md`）の必須10項目は、以下のカラムへ保存します。

| フォーム項目 | 成長DBカラム |
|---|---|
| ユーザー名 | user_name |
| 今の状態 | current_state |
| 子供の頃の夢 | childhood_dream |
| 相応しい次のステージ | next_stage（確定値を user_goal にも保持） |
| next_stage_source | next_stage_source |
| 進路エラータイプ | route_error_type |
| 今日の行動 | action_log |
| 気づき | insight_log |
| キャリアブロック | career_block_type / career_block_summary |
| 次のクエスト | next_quest |

Ver3 では `next_stage` の最終決定者はユーザーです。`next_stage_source` が `diagnosis` や `mentor` でも、採用判断はユーザーが行います。

## career_block_type

| 種類 | 意味 | 例 |
|---|---|---|
| 分かったブロック | 気付き、理解、発見 | 朝学習が続きやすいと分かった |
| できたブロック | 実践、行動、挑戦 | サービスを1人に説明できた |
| 経験ブロック | 成果、習慣、継続 | 7日連続で学習できた |
| 仕事化ブロック | 販売、収益、顧客獲得 | 初回相談で報酬を受け取った |

## goal_status

| ステータス | 説明 |
|---|---|
| 未設定 | ゴール未設定 |
| 設定済み | ゴールはあるが行動前 |
| 実行中 | クエストと記録が進んでいる |
| 達成 | success_condition を満たした |
| 修正中 | 進路エラー修正中 |
| 中止 | ユーザー判断で停止 |

## 更新率KPI

```text
更新率 = 対象期間内にゴール更新、行動記録、キャリアブロック生成、ゴール進捗更新のいずれかを行ったユーザー数 ÷ 登録ユーザー数
```

旧設計の `action_log / result_log / current_level / workization_status` 更新も、Ver3では更新率の一部として継続して数えます。

# growth_db_schema.md

## Ver3における成長DBの位置付け

成長DBは、ユーザーが直接見る主役ではありません。

ユーザーが体験する主役は「自分で設定したゴールへ向かってレベルアップし続けるゲーム」であり、成長DBはその裏側で蓄積される資産です。

## 成長DBの定義

成長DBとは、ユーザーが設定した相応しい次のステージへ向かう過程で生まれる進化の記録です。

Ver3では、以下を中心に保存します。

- ユーザーゴール
- ゴールカテゴリー
- ゴール理由
- 達成条件
- 期限
- 現在のギャップ
- ゴール進捗率
- 本来性一致スコア
- ゴールステータス
- キャリアブロック
- 行動履歴
- 成果履歴
- 仕事化履歴
- 冠位履歴

## ユーザーレコード項目

| 項目名 | 型 | 必須 | 説明 | 更新タイミング |
|---|---|---:|---|---|
| user_id | string | Yes | ユーザーを一意に識別するID。 | 初回登録時 |
| user_name | string | Yes | ユーザー名または表示名。 | 初回登録時／変更時 |
| childhood_dream | string | Yes | 子供の頃の夢、好きだったこと、自然にできること。 | 初回診断時／再発見時 |
| honrai_theme | string | Yes | 本来性テーマ。夢や自然にできることの奥にある継続テーマ。 | 診断時／言語化更新時 |
| user_goal | string | Yes | ユーザー自身が設定した現在ゴール。 | ゴール設定時 |
| goal_category | string | Yes | ゴールカテゴリー。仕事化、学習習慣、志望校など。 | ゴール設定時 |
| goal_reason | text | Yes | なぜそのゴールを目指すのか。 | ゴール設定時／修正時 |
| success_condition | text | Yes | ゴール達成の判定条件。 | ゴール設定時／修正時 |
| deadline | date | No | 達成期限。 | ゴール設定時／修正時 |
| current_gap | text | Yes | 現在地とゴールとの差分。 | 診断時／定期更新時 |
| goal_progress_rate | number | Yes | ゴール進捗率。0〜100。 | 行動記録／ブロック生成時 |
| honrai_alignment_score | integer | Yes | ユーザーゴールと本来性の一致率。0〜100。 | ゴール診断時 |
| goal_status | string | Yes | ゴール状態。未設定、設定済み、実行中、達成、修正中、中止。 | ゴール更新時 |
| route_error_type | string | Yes | ゴールと本来性のズレの種類。 | 進路エラー診断時 |
| route_error_rate | number | Yes | 進路エラー率。0〜100。高いほどズレが大きい。 | 進路エラー診断時 |
| current_job | string | No | 現在の仕事、役割、主活動。学習塾では現在の学習状態でもよい。 | 初回登録時／変化時 |
| current_level | integer | Yes | Lv.1〜Lv.10 の現在レベル。 | ブロック生成後 |
| current_rank | string | Yes | 現在冠位。レベルやゴール進捗率に応じて上昇する。 | レベルアップ時 |
| next_quest | string | Yes | ゴールへ近づく次のクエスト。 | 診断後／レベル判定後 |
| next_skill | string | No | 次のクエストに必要なスキル。 | クエスト生成時 |
| learning_task | string | No | 今日実行できる学習タスク。 | クエスト生成時 |
| career_block_count | integer | Yes | 4種ブロックの合計数。 | ブロック生成時 |
| understood_block_count | integer | Yes | 分かったブロック数。 | 気付き保存時 |
| did_block_count | integer | Yes | できたブロック数。 | 行動保存時 |
| experience_block_count | integer | Yes | 経験ブロック数。 | 成果・継続保存時 |
| work_block_count | integer | Yes | 仕事化ブロック数。学習塾では提出・挑戦・外部評価ブロックにも読み替え可能。 | 販売・提出・挑戦・顧客獲得時 |
| action_log | text | Yes | 今日やったことの履歴。 | 行動入力時 |
| result_log | text | Yes | 成果、反応、継続、学びの履歴。 | 行動入力時 |
| workization_status | string | No | 仕事化段階。フリーランス向けで主に使用。 | 仕事化進展時 |
| level_up_reason | text | Yes | レベルアップ理由。 | レベル更新時 |
| rank_history | text | Yes | 冠位の変化履歴。 | 冠位上昇時 |
| updated_at | datetime | Yes | 最終更新日時。更新率KPIの算出に使う。 | すべての更新時 |

## ゴールステータス

| goal_status | 説明 |
|---|---|
| 未設定 | ゴールがまだない |
| 設定済み | ゴールはあるが行動前 |
| 実行中 | クエストと行動記録が進んでいる |
| 達成 | success_condition を満たした |
| 修正中 | ゴールを見直している |
| 中止 | ユーザー判断で停止した |

## キャリアブロック項目

キャリアブロックは、成長DBの最小単位として別テーブルまたはJSON配列で保存します。

| 項目名 | 型 | 必須 | 説明 |
|---|---|---:|---|
| block_id | string | Yes | キャリアブロックの一意ID。 |
| user_id | string | Yes | 紐づくユーザーID。 |
| goal_id | string | No | 紐づくゴールID。 |
| block_type | enum | Yes | `分かった` / `できた` / `経験になった` / `仕事になった`。 |
| block_title | string | Yes | ブロックの短いタイトル。 |
| block_description | text | Yes | 気付き、行動、成果、仕事化内容。 |
| source_action | text | Yes | 生成元になった行動入力。 |
| related_quest | string | Yes | 関連するゴール連動クエスト。 |
| goal_progress_delta | number | No | ゴール進捗率への加算値。 |
| score_delta | integer | No | 本来性一致スコアへの加点。 |
| created_at | datetime | Yes | ブロック生成日時。 |

## ゴールカテゴリー

| カテゴリー | 説明 |
|---|---|
| 仕事化 | 本来性を仕事に接続する |
| 学習習慣 | 学習を継続できる状態にする |
| 志望校 | 志望校合格へ向かう |
| 資格 | 資格取得へ向かう |
| 収益化 | 売上や報酬を得る |
| 講師化 | 教える側になる |
| 作品化 | 作品やポートフォリオを完成する |
| 起業 | 事業仮説やサービスを作る |
| 自己理解 | 本来性や将来像を言語化する |
| その他 | 上記に当てはまらない個別ゴール |

## 進路エラー診断の保存値

進路エラー診断では以下を保存します。

- 現在地
- 本来性スコア / honrai_alignment_score
- ゴール一致率
- 進路エラー率 / route_error_rate
- 次のクエスト

## 更新率に関わる主要項目

更新率を上げるため、特に以下を更新対象にします。

- user_goal
- goal_progress_rate
- goal_status
- action_log
- result_log
- career_block_count
- current_level
- current_rank
- next_quest
- updated_at

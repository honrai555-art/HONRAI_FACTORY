# level_rules.md

## レベルアップルールの目的

このルールは、ユーザーが「本来の自分に還り続けることで、相応しい仕事を手に入れる」までの進化を Lv.1〜Lv.10 で判定するための基準です。

レベルアップ判定では、成長DBの更新率を最優先します。大きな成果だけでなく、小さな行動、気づき、顧客反応、仕事化仮説も成長として扱います。

## レベル一覧

| レベル | 名称 | 条件 | 主な更新項目 |
|---:|---|---|---|
| Lv.1 | 夢を思い出した | childhood_dream が記録され、子供の頃の夢を言語化した | childhood_dream, updated_at |
| Lv.2 | 本来性を言語化した | honrai_theme が記録され、夢の奥にあるテーマを説明できた | honrai_theme, honrai_score |
| Lv.3 | 小さな行動を書き込んだ | 本来テーマに関連する action_log を1件以上記録した | action_log, updated_at |
| Lv.4 | 成果を記録した | 行動の結果、反応、気づき、失敗を result_log に記録した | result_log, level_up_reason |
| Lv.5 | 仕事化の仮説を立てた | desired_job と workization_status=仮説 を記録した | desired_job, workization_status |
| Lv.6 | 顧客に提供した | 試作品、相談、企画、制作物などを他者または顧客に提供した | action_log, result_log, workization_status |
| Lv.7 | 収益が発生した | 金銭、報酬、仕事依頼、支援などの経済的反応が発生した | result_log, workization_status |
| Lv.8 | 継続提供できた | 同じ価値を複数回または一定期間提供できた | action_log, result_log, workization_status |
| Lv.9 | 他者に教えられた | 自分の方法を他者に教え、再現可能な型として説明できた | learning_task, result_log |
| Lv.10 | 相応しい仕事になった | 本来性、提供価値、継続性、収益、役割が一致した | current_level, workization_status, level_up_reason |

## レベル別詳細

### Lv.1 夢を思い出した

- childhood_dream が空欄でない
- 子供の頃の夢を1文で説明できる
- 夢を思い出した日を updated_at に記録する

### Lv.2 本来性を言語化した

- honrai_theme が空欄でない
- 夢の表面的な職業名ではなく、奥にあるテーマを言語化している
- honrai_score の初期値を記録する

例：漫画家 → 物語で人の本来性を起動する

### Lv.3 小さな行動を書き込んだ

- action_log に本来テーマへ近づく行動が記録されている
- 行動は小さくてよい
- 更新率向上のため、1行ログも有効とする

### Lv.4 成果を記録した

- result_log に行動結果が記録されている
- 成功、失敗、気づき、他者反応のいずれかがある
- レベルアップ理由を level_up_reason に保存する

### Lv.5 仕事化の仮説を立てた

- desired_job が設定されている
- workization_status が「仮説」以上になっている
- 子供の頃の夢を現代の提供価値へ翻訳している

### Lv.6 顧客に提供した

- 他者、顧客、仲間、コミュニティのいずれかに価値を提供した
- 無償提供でもよい
- 提供内容と反応を action_log / result_log に記録する

### Lv.7 収益が発生した

- 報酬、販売、依頼、投げ銭、紹介、契約などの経済的反応がある
- 金額の大小は問わない
- workization_status を「収益化」に更新する

### Lv.8 継続提供できた

- 同じ価値提供を複数回実施した
- 継続顧客、定期開催、反復依頼、改善履歴がある
- 仕組みとして続けられる状態を記録する

### Lv.9 他者に教えられた

- 自分の成長方法や提供方法を他者に説明できる
- テンプレート、チェックリスト、講座、マニュアルのいずれかがある
- AI工場で再利用できる型になっている

### Lv.10 相応しい仕事になった

- childhood_dream と desired_job がつながっている
- honrai_theme と日々の仕事が一致している
- 継続提供と収益がある
- 本人が「これは相応しい仕事だ」と言語化できる
- workization_status を「相応しい仕事」に更新する

## レベルアップ判定の基本式

```text
レベルアップ候補 = action_log + result_log + workization_status + honrai_score の変化
```

AIは、以下の順で判定します。

1. 必須項目が埋まっているか確認する
2. 直近の action_log と result_log を読む
3. workization_status の段階を確認する
4. 現在レベルより上の条件を満たすか確認する
5. level_up_reason を生成する
6. current_level と updated_at を更新する

## 降格ではなく再接続

HONRAI LEVEL UP SYSTEM では、ユーザーを罰するための降格は行いません。更新が止まった場合は「進路エラー通知」として扱い、本来の自分へ再接続するための小さな行動を提示します。

# HONRAI AGI - Data → Transform → Place Engine

Google Apps Script MVP for converting Career Card input into KAIDO WALK `layout_command.json`.

## MVP scope

Implemented:

- Input form for Career Card fields.
- Save to `CARD_MASTER` in Google Spreadsheet.
- `generateObjectRecipe()` Transform AGI using a fixed object dictionary.
- `generatePlacement()` Placement AGI using a fixed environment dictionary.
- `generateKaido()` end-to-end JSON output for `layout_command.json`.

Not implemented in this MVP:

- Unity placement runtime integration.
- Spatial connection.
- NFT, payment, and authentication.

## Spreadsheet

Create or bind a spreadsheet and deploy this folder as a Google Apps Script web app. The script creates/repairs `CARD_MASTER` with these columns:

```text
card_id,user_id,type,fit_score,phase,role,experience,skill,environment,emotion,stop,keep,start,created_at,updated_at
```

If the Apps Script project is not bound to a spreadsheet, set script property `SPREADSHEET_ID` to the target Google Spreadsheet ID.

## API functions

- `saveCard(card)` saves or updates a Career Card row.
- `generateObjectRecipe(card)` converts Career Card data into object recipe JSON.
- `generatePlacement(input)` converts object IDs into zone placement JSON.
- `generateKaido(card)` runs save → transform → placement and returns `layout_command_json`.

## Example output

```json
{
  "card_id": "CM20260529010101999",
  "zone": "sea",
  "avatar_type": "explorer",
  "objects": ["inn", "bridge", "lantern"],
  "placements": [
    { "part_id": "inn", "x": 8, "y": 0, "z": 4 },
    { "part_id": "bridge", "x": 0, "y": 0, "z": 0 },
    { "part_id": "lantern", "x": 12, "y": 0, "z": 4 }
  ]
}
```

## PayPal paid PDF pipeline

This Apps Script also supports the paid Career Card PDF flow:

```text
診断結果 → PayPal決済完了Webhook → 診断結果検索 → Google Slides金型コピー → PDF保存
```

### Required Script Properties

Set these in Apps Script **Project Settings → Script properties** unless the same IDs are hard-coded in `Code.gs`:

- `SPREADSHEET_ID` — spreadsheet containing diagnosis result data.
- `CAREER_CARD_TEMPLATE_SLIDE_ID` — Google Slides template ID for the fixed Career Card design.
- `CAREER_CARD_OUTPUT_FOLDER_ID` — optional Drive folder ID for generated PDFs. If blank, PDFs are saved to Drive root.
- `DIAGNOSIS_RESULT_SHEET_NAME` — optional preferred diagnosis-result sheet name.

### Sheets and columns

The generator reads:

- `content_20types` — required. Expected columns include `type_key`, `p5_basic`, `p5_role_main`, `p5_role_desc`, and `p5_summary_title`.
- `render` — optional. Used to merge visual/render data such as character image URLs.
- Diagnosis result sheets — searched in this order: `DIAGNOSIS_RESULT_SHEET_NAME`, `診断結果`, `diagnosis_results`, `render`, and `CARD_MASTER`.

Supported aliases include `resultId`/`result_id`/`card_id`, `email`/`メールアドレス`, `name`/`名前`, `main_type`/`type`/`p5_role_main`, `sub_type`, and `type_key`.

### Functions

- `doPost(e)` receives PayPal webhook events and calls `createCareerCardPdf_(data)` when the payment status/event is completed.
- `createCareerCardPdf_(data)` copies the Slides template, merges diagnosis/content/render values, replaces placeholders, exports PDF, and saves it to Drive.
- `testGenerateAll20CareerCards()` reads the first 20 rows from `content_20types`, generates one PDF per type, and logs `OK: <type_key> <type_name>` or `NG: <type_key> <error>`.

The PDF filename format is `HONRAIキャリアカード_名前_タイプ名.pdf`.

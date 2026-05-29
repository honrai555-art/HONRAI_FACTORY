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

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const codePath = path.join(__dirname, '..', 'github', 'career-card-gas', 'Code.gs');
const code = fs.readFileSync(codePath, 'utf8');
const rows = [];
const sheet = {
  headers: [],
  getRange(row, column, numRows, numColumns) {
    return {
      getValues() {
        if (row === 1) {
          return [sheet.headers];
        }
        return rows.slice(row - 2, row - 2 + numRows).map((entry) => [entry[0]]);
      },
      setValues(values) {
        if (row === 1) {
          sheet.headers = values[0];
          return;
        }
        rows[row - 2] = values[0];
      }
    };
  },
  setFrozenRows() {},
  appendRow(row) {
    rows.push(row);
  },
  getLastRow() {
    return rows.length + 1;
  }
};
const spreadsheet = {
  getSheetByName(name) {
    return name === 'CARD_MASTER' ? sheet : null;
  },
  insertSheet() {
    return sheet;
  }
};
const context = {
  console,
  Date,
  HtmlService: {
    createHtmlOutputFromFile() {
      return {
        setTitle() { return this; },
        setXFrameOptionsMode() { return this; }
      };
    },
    XFrameOptionsMode: { ALLOWALL: 'ALLOWALL' }
  },
  PropertiesService: {
    getScriptProperties() {
      return { getProperty() { return ''; } };
    }
  },
  SpreadsheetApp: {
    getActiveSpreadsheet() { return spreadsheet; },
    openById() { return spreadsheet; }
  },
  Utilities: {
    formatDate() { return '20260529010101999'; }
  }
};
vm.createContext(context);
vm.runInContext(code, context, { filename: codePath });

const sampleCard = {
  user_id: 'U001',
  type: '主人公',
  fit_score: '88',
  phase: '探索',
  role: '企画者',
  experience: 'イベント開催10回',
  skill: '企画',
  environment: '海',
  emotion: '仲間作りが楽しい',
  stop: '',
  keep: '交流の場',
  start: '定期開催を始める'
};

const recipe = context.generateObjectRecipe(sampleCard);
assert.strictEqual(
  JSON.stringify(recipe.objects.map((object) => object.object_type).slice(0, 3)),
  JSON.stringify(['inn', 'bridge', 'lantern'])
);

const placement = context.generatePlacement({ environment: '海', objects: ['bridge', 'inn', 'lantern'] });
assert.strictEqual(placement.zone, 'sea');
assert.strictEqual(
  JSON.stringify(placement.placements[0]),
  JSON.stringify({ part_id: 'bridge', x: 0, y: 0, z: 0 })
);

const result = context.generateKaido(sampleCard);
assert.strictEqual(result.zone, 'sea');
assert.strictEqual(result.avatar_type, 'explorer');
assert.strictEqual(result.layout_command_json.card_id, 'CM20260529010101999');
assert.ok(result.layout_command_json.objects.includes('bridge'));
assert.ok(result.layout_command_json.objects.includes('inn'));
assert.ok(result.layout_command_json.objects.includes('lantern'));
assert.strictEqual(rows.length, 1);

console.log('career-card-gas engine tests passed');

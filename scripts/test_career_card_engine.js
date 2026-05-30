const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const codePath = path.join(__dirname, '..', 'github', 'career-card-gas', 'Code.gs');
const code = fs.readFileSync(codePath, 'utf8');
const rows = [];
const content20Rows = [
  ['type_key', 'p5_role_main', 'p5_basic', 'p5_role_desc', 'p5_summary_title'],
  ['FA_CT', 'サラマンダー', '情熱の実行者', '火を灯す役割', '突破する炎'],
  ['AT_CT', 'アルケミスト', '変換の探究者', '素材を価値へ変える役割', '変化を設計する']
];
function createReadOnlySheet(name, values) {
  return {
    getName() { return name; },
    getDataRange() {
      return {
        getValues() { return values; }
      };
    }
  };
}
const sheet = {
  headers: [],
  getName() { return 'CARD_MASTER'; },
  getDataRange() {
    return {
      getValues() { return [sheet.headers].concat(rows); }
    };
  },
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
    if (name === 'CARD_MASTER') return sheet;
    if (name === 'content_20types') return createReadOnlySheet(name, content20Rows);
    return null;
  },
  insertSheet() {
    return sheet;
  }
};
const context = {
  console,
  Date,
  Logger: { log() {} },
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

const paypalPayload = {
  event_type: 'PAYMENT.CAPTURE.COMPLETED',
  resource: {
    status: 'COMPLETED',
    custom_id: 'resultId=R001&type_key=FA_CT',
    payer: {
      email_address: 'buyer@example.com',
      name: { given_name: 'Honrai', surname: 'Taro' }
    }
  }
};
assert.strictEqual(context.isPayPalPaymentCompleted_(paypalPayload), true);
const webhookData = context.extractPayPalCareerCardData_(paypalPayload);
assert.strictEqual(webhookData.resultId, 'R001');
assert.strictEqual(webhookData.type_key, 'FA_CT');
assert.strictEqual(webhookData.email, 'buyer@example.com');
assert.strictEqual(webhookData.name, 'Honrai Taro');

const typeContent = context.findContent20Type_('FA_CT', '');
assert.strictEqual(typeContent.p5_role_main, 'サラマンダー');
const merged = context.buildCareerCardMergeData_(
  { name: 'テスト', type_key: 'FA_CT', main_type: '' },
  { main_type: 'サラマンダー', p5_basic: '診断本文' },
  typeContent,
  {}
);
assert.strictEqual(merged.main_type, 'サラマンダー');
assert.strictEqual(merged.p5_summary_title, '突破する炎');

console.log('career-card-gas engine tests passed');

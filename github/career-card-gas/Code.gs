/**
 * HONRAI AGI - Data → Transform → Place Engine
 * Google Apps Script backend for Career Card input, CARD_MASTER storage,
 * object recipe generation, placement generation, and KAIDO WALK JSON output.
 */

const SHEET_NAME = 'CARD_MASTER';
const CARD_MASTER_HEADERS = [
  'card_id',
  'user_id',
  'type',
  'fit_score',
  'phase',
  'role',
  'experience',
  'skill',
  'environment',
  'emotion',
  'stop',
  'keep',
  'start',
  'created_at',
  'updated_at'
];

const OBJECT_DICTIONARY = [
  {
    object_type: 'bridge',
    label: '橋',
    reason: '人との接続',
    keywords: ['接続', '紹介', '仲介', '仲間', '交流', 'つなぐ', 'マッチング']
  },
  {
    object_type: 'tea_house',
    label: '茶屋',
    reason: '小さな成果',
    keywords: ['小さな成果', '達成', '試作', '一歩', '実験', '休憩', '共有']
  },
  {
    object_type: 'inn',
    label: '宿場',
    reason: '継続活動',
    keywords: ['継続活動', 'イベント', '開催', '運営', '交流活動', 'コミュニティ', '定期']
  },
  {
    object_type: 'castle',
    label: '城',
    reason: '仕事化',
    keywords: ['仕事化', '事業', '収益', '経営', '役割', '案件', 'プロジェクト']
  },
  {
    object_type: 'lantern',
    label: '灯籠',
    reason: '気付き・学び',
    keywords: ['気付き', '気づき', '学び', '発見', '理解', '内省', '楽しい']
  },
  {
    object_type: 'fork',
    label: '分岐',
    reason: '決断・方向転換',
    keywords: ['決断', '方向転換', 'やめる', '始める', '変化', '選択', '転機']
  }
];

const ENVIRONMENT_DICTIONARY = [
  {
    zone: 'sea',
    label: '海',
    avatar_type: 'explorer',
    keywords: ['海', '探索', '企画', '発見']
  },
  {
    zone: 'forest',
    label: '森',
    avatar_type: 'mentor',
    keywords: ['森', '教育', '育成', '学習']
  },
  {
    zone: 'mountain',
    label: '山',
    avatar_type: 'researcher',
    keywords: ['山', '専門性', '研究', '分析']
  },
  {
    zone: 'rocky',
    label: '岩場',
    avatar_type: 'strategist',
    keywords: ['岩場', '経営', '意思決定', '判断']
  },
  {
    zone: 'sky',
    label: '空',
    avatar_type: 'broadcaster',
    keywords: ['空', '編集', '発信', '表現']
  }
];

const PLACEMENT_PRESETS = {
  bridge: { x: 0, y: 0, z: 0 },
  inn: { x: 8, y: 0, z: 4 },
  lantern: { x: 12, y: 0, z: 4 },
  tea_house: { x: 6, y: 0, z: -4 },
  castle: { x: 18, y: 0, z: 8 },
  fork: { x: 4, y: 0, z: 8 }
};

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('HONRAI AGI - Data → Transform → Place Engine')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function saveCard(cardInput) {
  const now = new Date().toISOString();
  const card = normalizeCard_(cardInput || {});
  card.card_id = card.card_id || createCardId_();
  card.created_at = card.created_at || now;
  card.updated_at = now;

  const sheet = getCardMasterSheet_();
  const rowIndex = findCardRow_(sheet, card.card_id);
  const row = CARD_MASTER_HEADERS.map((header) => serializeCell_(card[header]));

  if (rowIndex > 0) {
    sheet.getRange(rowIndex, 1, 1, CARD_MASTER_HEADERS.length).setValues([row]);
  } else {
    sheet.appendRow(row);
  }

  return card;
}

function generateObjectRecipe(cardInput) {
  const card = normalizeCard_(cardInput || {});
  const sourceTexts = [
    card.experience,
    card.skill,
    card.environment,
    card.emotion,
    card.stop,
    card.keep,
    card.start,
    card.role,
    card.phase
  ];
  const objects = OBJECT_DICTIONARY
    .map((entry) => {
      const score = countKeywordHits_(sourceTexts, entry.keywords);
      return {
        object_type: entry.object_type,
        label: entry.label,
        reason: score > 0 ? entry.reason : '',
        score: score
      };
    })
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score || dictionaryIndex_(a.object_type) - dictionaryIndex_(b.object_type))
    .map((entry) => ({
      object_type: entry.object_type,
      reason: entry.reason
    }));

  if (objects.length === 0) {
    objects.push({
      object_type: 'lantern',
      reason: '入力内容から最初の気付きとして生成'
    });
  }

  return {
    card_id: card.card_id || '',
    objects: objects
  };
}

function generatePlacement(input) {
  const payload = input || {};
  const environment = payload.environment || payload.zone || '';
  const objects = normalizeObjects_(payload.objects || []);
  const zoneInfo = resolveZone_(environment, payload);
  const placements = objects.map((partId, index) => {
    const preset = PLACEMENT_PRESETS[partId] || fallbackPlacement_(index);
    return {
      part_id: partId,
      x: preset.x,
      y: preset.y,
      z: preset.z
    };
  });

  return {
    zone: zoneInfo.zone,
    avatar_type: zoneInfo.avatar_type,
    placements: placements
  };
}

function generateKaido(cardInput) {
  const savedCard = saveCard(cardInput || {});
  const objectRecipe = generateObjectRecipe(savedCard);
  const objectTypes = objectRecipe.objects.map((object) => object.object_type);
  const placement = generatePlacement({
    environment: savedCard.environment,
    objects: objectTypes,
    card: savedCard
  });

  return {
    card_id: savedCard.card_id,
    zone: placement.zone,
    avatar_type: placement.avatar_type,
    objects: objectTypes,
    object_recipe: objectRecipe,
    placements: placement.placements,
    layout_command_json: {
      card_id: savedCard.card_id,
      zone: placement.zone,
      avatar_type: placement.avatar_type,
      objects: objectTypes,
      placements: placement.placements
    }
  };
}

function getCardMasterSheet_() {
  const spreadsheetId = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  const spreadsheet = spreadsheetId
    ? SpreadsheetApp.openById(spreadsheetId)
    : SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
  ensureHeaders_(sheet);
  return sheet;
}

function ensureHeaders_(sheet) {
  const headerRange = sheet.getRange(1, 1, 1, CARD_MASTER_HEADERS.length);
  const currentHeaders = headerRange.getValues()[0];
  const needsHeaders = CARD_MASTER_HEADERS.some((header, index) => currentHeaders[index] !== header);
  if (needsHeaders) {
    headerRange.setValues([CARD_MASTER_HEADERS]);
    sheet.setFrozenRows(1);
  }
}

function findCardRow_(sheet, cardId) {
  if (!cardId || sheet.getLastRow() < 2) {
    return -1;
  }
  const values = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues();
  for (let index = 0; index < values.length; index += 1) {
    if (values[index][0] === cardId) {
      return index + 2;
    }
  }
  return -1;
}

function normalizeCard_(card) {
  const normalized = {};
  CARD_MASTER_HEADERS.forEach((header) => {
    normalized[header] = deserializeCell_(card[header]);
  });
  return normalized;
}

function normalizeObjects_(objects) {
  return objects
    .map((object) => (typeof object === 'string' ? object : object.object_type || object.part_id || ''))
    .filter(Boolean);
}

function resolveZone_(environment, payload) {
  const texts = [environment];
  if (payload.card) {
    texts.push(payload.card.skill, payload.card.experience, payload.card.role);
  }
  const matched = ENVIRONMENT_DICTIONARY
    .map((entry) => ({
      entry: entry,
      score: countKeywordHits_(texts, entry.keywords) + (environment === entry.zone ? 3 : 0)
    }))
    .sort((a, b) => b.score - a.score)[0];

  if (matched && matched.score > 0) {
    return {
      zone: matched.entry.zone,
      avatar_type: matched.entry.avatar_type
    };
  }

  return {
    zone: 'sea',
    avatar_type: 'explorer'
  };
}

function countKeywordHits_(texts, keywords) {
  const joined = texts.map((text) => arrayText_(text)).join('\n').toLowerCase();
  return keywords.reduce((score, keyword) => {
    return joined.indexOf(String(keyword).toLowerCase()) >= 0 ? score + 1 : score;
  }, 0);
}

function dictionaryIndex_(objectType) {
  return OBJECT_DICTIONARY.findIndex((entry) => entry.object_type === objectType);
}

function fallbackPlacement_(index) {
  return {
    x: index * 6,
    y: 0,
    z: Math.floor(index / 2) * 4
  };
}

function createCardId_() {
  return 'CM' + Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyyMMddHHmmssSSS');
}

function serializeCell_(value) {
  if (Array.isArray(value)) {
    return value.join('\n');
  }
  if (value === null || value === undefined) {
    return '';
  }
  return value;
}

function deserializeCell_(value) {
  if (Array.isArray(value)) {
    return value.filter(Boolean).join('\n');
  }
  if (value === null || value === undefined) {
    return '';
  }
  return value;
}

function arrayText_(value) {
  if (Array.isArray(value)) {
    return value.join('\n');
  }
  if (value === null || value === undefined) {
    return '';
  }
  return String(value);
}

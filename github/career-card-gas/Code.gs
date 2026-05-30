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

// -----------------------------------------------------------------------------
// PayPal paid Career Card PDF pipeline
// 診断結果 → PayPal決済完了Webhook → キャリアカードPDF生成 → Drive保存
// -----------------------------------------------------------------------------
const CAREER_CARD_OUTPUT_FOLDER_ID = '';
const CAREER_CARD_TEMPLATE_SLIDE_ID = '';
const CAREER_CARD_CONTENT_20TYPES_SHEET_NAME = 'content_20types';
const CAREER_CARD_RENDER_SHEET_NAME = 'render';
const CAREER_CARD_DIAGNOSIS_SHEET_CANDIDATES = ['診断結果', 'diagnosis_results', 'render', 'CARD_MASTER'];
const CAREER_CARD_RESULT_ID_ALIASES = ['resultId', 'result_id', 'diagnosis_id', 'card_id', 'id'];
const CAREER_CARD_EMAIL_ALIASES = ['email', 'メール', 'メールアドレス', 'buyer_email', 'payer_email'];
const CAREER_CARD_NAME_ALIASES = ['name', '名前', '氏名', 'buyer_name', 'payer_name'];
const CAREER_CARD_MAIN_TYPE_ALIASES = ['main_type', '主タイプ', 'メインタイプ', 'type', 'p5_role_main'];
const CAREER_CARD_SUB_TYPE_ALIASES = ['sub_type', '副タイプ', 'サブタイプ'];
const CAREER_CARD_TYPE_KEY_ALIASES = ['type_key', 'タイプキー', 'key', 'typeKey'];
const CAREER_CARD_DIAGNOSIS_ALIASES = ['diagnosis', '診断結果', 'result', 'summary', 'p5_basic'];

function doPost(e) {
  Logger.log('WEBHOOK RECEIVED');
  const payload = parseWebhookPayload_(e);
  if (!isPayPalPaymentCompleted_(payload)) {
    Logger.log('WEBHOOK IGNORED: payment is not completed');
    return jsonResponse_({ ok: true, ignored: true, reason: 'payment_not_completed' });
  }

  Logger.log('PAYMENT COMPLETED');
  const data = extractPayPalCareerCardData_(payload);
  const pdfResult = createCareerCardPdf_(data);
  Logger.log('DONE');
  return jsonResponse_({ ok: true, pdf: pdfResult });
}

function createCareerCardPdf_(data) {
  const seed = normalizeCareerCardData_(data || {});
  const resultData = findDiagnosisResult_(seed);
  Logger.log('RESULT DATA FOUND');

  const typeKey = resultData.type_key || seed.type_key || resultData.main_type || seed.main_type || '';
  Logger.log('TYPE KEY: ' + typeKey);

  const typeContent = findContent20Type_(typeKey, resultData.main_type || seed.main_type);
  const renderData = findRenderData_(seed, resultData);
  const cardData = buildCareerCardMergeData_(seed, resultData, typeContent, renderData);

  const templateId = getScriptPropertyOrDefault_('CAREER_CARD_TEMPLATE_SLIDE_ID', CAREER_CARD_TEMPLATE_SLIDE_ID);
  if (!templateId) {
    throw new Error('CAREER_CARD_TEMPLATE_SLIDE_ID is not set. Set Script Properties or fill the const.');
  }

  const outputFolder = getCareerCardOutputFolder_();
  const slideCopyName = buildCareerCardFileName_(cardData, 'slides');
  const slideCopy = DriveApp.getFileById(templateId).makeCopy(slideCopyName, outputFolder);
  Logger.log('SLIDE COPY CREATED: ' + slideCopy.getId());

  const presentation = SlidesApp.openById(slideCopy.getId());
  replaceCareerCardText_(presentation, cardData);
  Logger.log('TEXT REPLACED');
  replaceCareerCardImages_(presentation, cardData);
  Logger.log('IMAGE REPLACED');
  presentation.saveAndClose();

  const pdfBlob = DriveApp.getFileById(slideCopy.getId())
    .getAs(MimeType.PDF)
    .setName(buildCareerCardFileName_(cardData, 'pdf'));
  Logger.log('PDF CREATED');

  const pdfFile = outputFolder.createFile(pdfBlob);
  Logger.log('PDF SAVED: ' + pdfFile.getUrl());
  Logger.log('DONE');

  return {
    fileId: pdfFile.getId(),
    fileName: pdfFile.getName(),
    fileUrl: pdfFile.getUrl(),
    slideId: slideCopy.getId(),
    folderId: outputFolder.getId(),
    type_key: cardData.type_key || '',
    main_type: cardData.main_type || ''
  };
}

function testGenerateAll20CareerCards() {
  const contentRows = getSheetRecords_(CAREER_CARD_CONTENT_20TYPES_SHEET_NAME);
  const targets = contentRows.slice(0, 20);
  const results = [];

  targets.forEach((typeRow, index) => {
    const typeKey = getFirstValue_(typeRow, CAREER_CARD_TYPE_KEY_ALIASES) || typeRow.type_key || typeRow.key || ('TYPE_' + (index + 1));
    const typeName = getFirstValue_(typeRow, CAREER_CARD_MAIN_TYPE_ALIASES) || typeRow.p5_role_main || typeRow.type_name || typeKey;
    try {
      const result = createCareerCardPdf_({
        name: 'テストユーザー' + String(index + 1).padStart(2, '0'),
        email: 'test+' + typeKey + '@example.com',
        resultId: 'TEST_' + typeKey,
        main_type: typeName,
        sub_type: typeRow.sub_type || '',
        type_key: typeKey,
        diagnosis: typeRow.p5_basic || typeRow.diagnosis || '',
        p5_basic: typeRow.p5_basic || '',
        p5_role_main: typeRow.p5_role_main || typeName,
        p5_role_desc: typeRow.p5_role_desc || '',
        p5_summary_title: typeRow.p5_summary_title || ''
      });
      Logger.log('OK: ' + typeKey + ' ' + typeName);
      results.push({ ok: true, type_key: typeKey, type_name: typeName, fileUrl: result.fileUrl });
    } catch (error) {
      Logger.log('NG: ' + typeKey + ' ' + (error && error.message ? error.message : error));
      results.push({ ok: false, type_key: typeKey, type_name: typeName, error: String(error && error.message ? error.message : error) });
    }
  });

  return results;
}

function parseWebhookPayload_(e) {
  if (!e || !e.postData || !e.postData.contents) {
    return {};
  }
  try {
    return JSON.parse(e.postData.contents);
  } catch (error) {
    Logger.log('Webhook payload JSON parse failed: ' + error.message);
    return { raw: e.postData.contents };
  }
}

function isPayPalPaymentCompleted_(payload) {
  const eventType = String(payload.event_type || payload.eventType || payload.type || '').toUpperCase();
  const resource = payload.resource || payload;
  const status = String(resource.status || payload.status || '').toUpperCase();
  return eventType === 'PAYMENT.CAPTURE.COMPLETED'
    || eventType === 'CHECKOUT.ORDER.COMPLETED'
    || eventType === 'PAYMENT.SALE.COMPLETED'
    || status === 'COMPLETED';
}

function extractPayPalCareerCardData_(payload) {
  const resource = payload.resource || payload;
  const payer = resource.payer || payload.payer || {};
  const payerName = payer.name || {};
  const purchaseUnit = resource.purchase_units && resource.purchase_units[0] ? resource.purchase_units[0] : {};
  const customId = resource.custom_id || purchaseUnit.custom_id || resource.invoice_id || purchaseUnit.invoice_id || '';
  const customData = parseCustomCareerCardData_(customId);

  return Object.assign({
    name: [payerName.given_name, payerName.surname].filter(Boolean).join(' ') || resource.name || '',
    email: payer.email_address || resource.email_address || '',
    resultId: customData.resultId || customData.result_id || customId || '',
    main_type: customData.main_type || '',
    sub_type: customData.sub_type || '',
    type_key: customData.type_key || ''
  }, customData);
}

function parseCustomCareerCardData_(value) {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch (error) {
    return String(value).split('&').reduce((data, pair) => {
      const parts = pair.split('=');
      if (parts.length === 2) {
        data[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1]);
      }
      return data;
    }, {});
  }
}

function normalizeCareerCardData_(data) {
  return {
    name: data.name || data.buyer_name || '',
    email: data.email || data.buyer_email || '',
    resultId: data.resultId || data.result_id || data.card_id || '',
    main_type: data.main_type || data.type || data.p5_role_main || '',
    sub_type: data.sub_type || '',
    type_key: data.type_key || data.typeKey || '',
    diagnosis: data.diagnosis || data.result || data.p5_basic || '',
    p5_basic: data.p5_basic || data.diagnosis || '',
    p5_role_main: data.p5_role_main || data.main_type || data.type || '',
    p5_role_desc: data.p5_role_desc || '',
    p5_summary_title: data.p5_summary_title || ''
  };
}

function findDiagnosisResult_(seed) {
  const spreadsheet = getCareerCardSpreadsheet_();
  const candidates = [getScriptPropertyOrDefault_('DIAGNOSIS_RESULT_SHEET_NAME', '')]
    .concat(CAREER_CARD_DIAGNOSIS_SHEET_CANDIDATES)
    .filter(Boolean);

  for (let i = 0; i < candidates.length; i += 1) {
    const sheet = spreadsheet.getSheetByName(candidates[i]);
    if (!sheet) continue;
    const records = getSheetRecordsFromSheet_(sheet);
    Logger.log('Sheet columns [' + sheet.getName() + ']: ' + Object.keys(records[0] || {}).join(', '));
    const found = records.find((record) => matchesDiagnosisRecord_(record, seed));
    if (found) {
      return normalizeDiagnosisRecord_(found, seed);
    }
  }

  if (seed.type_key || seed.main_type || seed.diagnosis || seed.p5_basic) {
    return normalizeDiagnosisRecord_(seed, seed);
  }

  throw new Error('Diagnosis result not found. resultId=' + seed.resultId + ', email=' + seed.email);
}

function matchesDiagnosisRecord_(record, seed) {
  const resultId = getFirstValue_(record, CAREER_CARD_RESULT_ID_ALIASES);
  const email = getFirstValue_(record, CAREER_CARD_EMAIL_ALIASES);
  const typeKey = getFirstValue_(record, CAREER_CARD_TYPE_KEY_ALIASES);
  return Boolean((seed.resultId && resultId && String(resultId) === String(seed.resultId))
    || (seed.email && email && String(email).toLowerCase() === String(seed.email).toLowerCase())
    || (seed.type_key && typeKey && String(typeKey) === String(seed.type_key)));
}

function normalizeDiagnosisRecord_(record, seed) {
  return Object.assign({}, record, {
    name: getFirstValue_(record, CAREER_CARD_NAME_ALIASES) || seed.name || '',
    email: getFirstValue_(record, CAREER_CARD_EMAIL_ALIASES) || seed.email || '',
    resultId: getFirstValue_(record, CAREER_CARD_RESULT_ID_ALIASES) || seed.resultId || '',
    main_type: getFirstValue_(record, CAREER_CARD_MAIN_TYPE_ALIASES) || seed.main_type || '',
    sub_type: getFirstValue_(record, CAREER_CARD_SUB_TYPE_ALIASES) || seed.sub_type || '',
    type_key: getFirstValue_(record, CAREER_CARD_TYPE_KEY_ALIASES) || seed.type_key || '',
    diagnosis: getFirstValue_(record, CAREER_CARD_DIAGNOSIS_ALIASES) || seed.diagnosis || '',
    p5_basic: record.p5_basic || seed.p5_basic || getFirstValue_(record, CAREER_CARD_DIAGNOSIS_ALIASES) || '',
    p5_role_main: record.p5_role_main || seed.p5_role_main || getFirstValue_(record, CAREER_CARD_MAIN_TYPE_ALIASES) || '',
    p5_role_desc: record.p5_role_desc || seed.p5_role_desc || '',
    p5_summary_title: record.p5_summary_title || seed.p5_summary_title || ''
  });
}

function findContent20Type_(typeKey, mainType) {
  const records = getSheetRecords_(CAREER_CARD_CONTENT_20TYPES_SHEET_NAME);
  Logger.log('Sheet columns [' + CAREER_CARD_CONTENT_20TYPES_SHEET_NAME + ']: ' + Object.keys(records[0] || {}).join(', '));
  const found = records.find((record) => {
    const recordKey = getFirstValue_(record, CAREER_CARD_TYPE_KEY_ALIASES);
    const recordType = getFirstValue_(record, CAREER_CARD_MAIN_TYPE_ALIASES);
    return (typeKey && String(recordKey) === String(typeKey)) || (mainType && String(recordType) === String(mainType));
  });
  if (!found) {
    throw new Error('content_20types row not found. type_key=' + typeKey + ', main_type=' + mainType);
  }
  return found;
}

function findRenderData_(seed, resultData) {
  try {
    const records = getSheetRecords_(CAREER_CARD_RENDER_SHEET_NAME);
    Logger.log('Sheet columns [' + CAREER_CARD_RENDER_SHEET_NAME + ']: ' + Object.keys(records[0] || {}).join(', '));
    return records.find((record) => matchesDiagnosisRecord_(record, seed) || matchesDiagnosisRecord_(record, resultData)) || {};
  } catch (error) {
    Logger.log('render sheet lookup skipped: ' + error.message);
    return {};
  }
}

function buildCareerCardMergeData_(seed, resultData, typeContent, renderData) {
  const merged = mergeNonEmptyObjects_(typeContent, renderData, resultData, seed);
  merged.name = merged.name || 'お客様';
  merged.email = merged.email || '';
  merged.resultId = merged.resultId || merged.result_id || '';
  merged.type_key = merged.type_key || merged.typeKey || getFirstValue_(typeContent, CAREER_CARD_TYPE_KEY_ALIASES) || '';
  merged.main_type = merged.main_type || merged.type || merged.p5_role_main || getFirstValue_(typeContent, CAREER_CARD_MAIN_TYPE_ALIASES) || '';
  merged.sub_type = merged.sub_type || '';
  merged.p5_basic = merged.p5_basic || merged.diagnosis || typeContent.p5_basic || '';
  merged.p5_role_main = merged.p5_role_main || merged.main_type || typeContent.p5_role_main || '';
  merged.p5_role_desc = merged.p5_role_desc || typeContent.p5_role_desc || '';
  merged.p5_summary_title = merged.p5_summary_title || typeContent.p5_summary_title || '';
  merged.generated_at = new Date().toISOString();
  return merged;
}


function mergeNonEmptyObjects_() {
  const merged = {};
  for (let index = 0; index < arguments.length; index += 1) {
    const source = arguments[index] || {};
    Object.keys(source).forEach((key) => {
      const value = source[key];
      if (value !== '' && value !== null && value !== undefined) {
        merged[key] = value;
      }
    });
  }
  return merged;
}

function replaceCareerCardText_(presentation, data) {
  Object.keys(data).forEach((key) => {
    const value = formatPlaceholderValue_(data[key]);
    presentation.replaceAllText('{{' + key + '}}', value);
    presentation.replaceAllText('<<' + key + '>>', value);
    presentation.replaceAllText('{' + key + '}', value);
  });
}

function replaceCareerCardImages_(presentation, data) {
  const imageUrl = data.character_image_url || data.image_url || data.char_image_url || data.avatar_url || '';
  if (!imageUrl) {
    Logger.log('IMAGE REPLACED: skipped (no image URL)');
    return;
  }
  const imageBlob = UrlFetchApp.fetch(imageUrl).getBlob();
  presentation.getSlides().forEach((slide) => {
    slide.getShapes().forEach((shape) => {
      const text = shape.getText ? shape.getText().asString().trim() : '';
      if (['{{character_image}}', '{{character_image_url}}', '{{image_url}}'].indexOf(text) >= 0) {
        const left = shape.getLeft();
        const top = shape.getTop();
        const width = shape.getWidth();
        const height = shape.getHeight();
        shape.remove();
        slide.insertImage(imageBlob, left, top, width, height);
      }
    });
  });
}

function buildCareerCardFileName_(data, extension) {
  const typeName = sanitizeDriveFileName_(data.main_type || data.p5_role_main || data.type_key || 'タイプ未設定');
  const name = sanitizeDriveFileName_(data.name || 'お客様');
  const suffix = extension === 'pdf' ? '.pdf' : '';
  return 'HONRAIキャリアカード_' + name + '_' + typeName + suffix;
}

function sanitizeDriveFileName_(value) {
  return String(value || '').replace(/[\\/:*?"<>|#%{}~&]/g, '_').trim() || '未設定';
}

function getCareerCardOutputFolder_() {
  const folderId = getScriptPropertyOrDefault_('CAREER_CARD_OUTPUT_FOLDER_ID', CAREER_CARD_OUTPUT_FOLDER_ID);
  return folderId ? DriveApp.getFolderById(folderId) : DriveApp.getRootFolder();
}

function getCareerCardSpreadsheet_() {
  const spreadsheetId = getScriptPropertyOrDefault_('SPREADSHEET_ID', '');
  return spreadsheetId ? SpreadsheetApp.openById(spreadsheetId) : SpreadsheetApp.getActiveSpreadsheet();
}

function getSheetRecords_(sheetName) {
  const sheet = getCareerCardSpreadsheet_().getSheetByName(sheetName);
  if (!sheet) {
    throw new Error('Sheet not found: ' + sheetName);
  }
  return getSheetRecordsFromSheet_(sheet);
}

function getSheetRecordsFromSheet_(sheet) {
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    return [];
  }
  const headers = values[0].map((header) => String(header || '').trim());
  return values.slice(1).filter((row) => row.some((value) => value !== '' && value !== null)).map((row) => {
    return headers.reduce((record, header, index) => {
      if (header) record[header] = row[index];
      return record;
    }, {});
  });
}

function getFirstValue_(record, aliases) {
  if (!record) return '';
  for (let i = 0; i < aliases.length; i += 1) {
    const key = aliases[i];
    if (record[key] !== undefined && record[key] !== null && record[key] !== '') {
      return record[key];
    }
  }
  return '';
}

function formatPlaceholderValue_(value) {
  if (Array.isArray(value)) {
    return value.join('\n');
  }
  if (value === null || value === undefined) {
    return '';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

function getScriptPropertyOrDefault_(key, fallback) {
  const properties = PropertiesService.getScriptProperties();
  const value = properties.getProperty(key);
  return value !== null && value !== undefined && value !== '' ? value : fallback;
}

function jsonResponse_(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

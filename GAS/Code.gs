const SHEET_NAME = 'CARD_MASTER';
const OPENAI_ENDPOINT = 'https://api.openai.com/v1/responses';
const OPENAI_MODEL = 'gpt-4.1-mini';
const HEADERS = [
  'card_id',
  'user_id',
  'type',
  'fit_score',
  'phase',
  'role_candidate',
  'stop',
  'keep',
  'start',
  'experience',
  'skill',
  'environment',
  'desired_change',
  'created_at',
  'updated_at',
];
const LIST_FIELDS = ['stop', 'keep', 'start', 'experience', 'skill', 'environment'];

function doGet() {
  return HtmlService.createTemplateFromFile('Frontend/index')
    .evaluate()
    .setTitle('HONRAI Career Card AGI Input System')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

function getCard(cardId) {
  const sheet = getCardSheet_();
  const rowIndex = findRowByCardId_(sheet, cardId);
  if (rowIndex < 0) {
    throw new Error(`Card not found: ${cardId}`);
  }
  return rowToCard_(sheet.getRange(rowIndex, 1, 1, HEADERS.length).getValues()[0]);
}

function saveCard(data) {
  const sheet = getCardSheet_();
  const now = new Date().toISOString();
  const normalized = normalizeCardData_(data || {});
  const cardId = normalized.card_id || nextCardId_(sheet);
  const existingRowIndex = findRowByCardId_(sheet, cardId);

  const existing = existingRowIndex > 0
    ? rowToCard_(sheet.getRange(existingRowIndex, 1, 1, HEADERS.length).getValues()[0])
    : {};

  const card = Object.assign({}, existing, normalized, {
    card_id: cardId,
    created_at: existing.created_at || now,
    updated_at: now,
  });

  const row = cardToRow_(card);
  if (existingRowIndex > 0) {
    sheet.getRange(existingRowIndex, 1, 1, HEADERS.length).setValues([row]);
  } else {
    sheet.appendRow(row);
  }

  return rowToCard_(row);
}

function generateStruct(cardId) {
  const card = getCard(cardId);
  return {
    card_id: card.card_id,
    type: card.type,
    fit_score: Number(card.fit_score || 0),
    phase: card.phase,
    role_candidate: card.role_candidate,
    decision: {
      stop: asList_(card.stop),
      keep: asList_(card.keep),
      start: asList_(card.start),
    },
    career_material: {
      experience: asList_(card.experience),
      skill: asList_(card.skill),
      environment: asList_(card.environment),
      desired_change: card.desired_change || '',
    },
  };
}

function generateLayout(cardId) {
  const struct = generateStruct(cardId);
  const agiResult = requestAgiLayout_(struct);
  const layoutCommand = {
    card_id: struct.card_id,
    zone: agiResult.zone || '',
    avatar_type: agiResult.avatar_type || '',
    role: agiResult.role || struct.role_candidate || '',
    placements: Array.isArray(agiResult.placements) ? agiResult.placements.map(normalizePlacement_) : [],
  };
  return layoutCommand;
}

function requestAgiLayout_(struct) {
  const scriptProperties = PropertiesService.getScriptProperties();
  const apiKey = scriptProperties.getProperty('OPENAI_API_KEY');
  if (isMockAgiEnabled_(scriptProperties)) {
    return buildMockLayout_(struct);
  }
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not set in Script Properties. Set MOCK_AGI=true for local demo mode.');
  }

  const schema = {
    type: 'object',
    additionalProperties: false,
    required: ['zone', 'avatar_type', 'role', 'placements'],
    properties: {
      zone: { type: 'string' },
      avatar_type: { type: 'string' },
      role: { type: 'string' },
      placements: {
        type: 'array',
        items: {
          type: 'object',
          additionalProperties: false,
          required: ['part_id', 'x', 'y', 'z'],
          properties: {
            part_id: { type: 'string' },
            x: { type: 'number' },
            y: { type: 'number' },
            z: { type: 'number' },
          },
        },
      },
    },
  };

  const payload = {
    model: OPENAI_MODEL,
    input: [
      {
        role: 'system',
        content: [
          {
            type: 'input_text',
            text: 'You are an AGI layout judge for HONRAI Kaido WALK. Return JSON only. Do not return prose, markdown, or explanations.',
          },
        ],
      },
      {
        role: 'user',
        content: [
          {
            type: 'input_text',
            text: JSON.stringify({ struct: struct }),
          },
        ],
      },
    ],
    text: {
      format: {
        type: 'json_schema',
        name: 'layout_command_body',
        strict: true,
        schema: schema,
      },
    },
  };

  const response = UrlFetchApp.fetch(OPENAI_ENDPOINT, {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: `Bearer ${apiKey}` },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });

  const status = response.getResponseCode();
  const body = response.getContentText();
  if (status < 200 || status >= 300) {
    throw new Error(`OpenAI API error ${status}: ${body}`);
  }

  const parsed = JSON.parse(body);
  const outputText = extractResponseText_(parsed);
  return JSON.parse(outputText);
}

function isMockAgiEnabled_(scriptProperties) {
  return String(scriptProperties.getProperty('MOCK_AGI') || '').trim().toLowerCase() === 'true';
}

function getCardSheet_() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  if (!spreadsheet) {
    throw new Error('Active spreadsheet is not available. Bind this script to a Spreadsheet or run it from a container-bound Web app.');
  }
  const sheet = spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
  const headerRange = sheet.getRange(1, 1, 1, HEADERS.length);
  const currentHeaders = headerRange.getValues()[0];
  const needsHeader = HEADERS.some((header, index) => currentHeaders[index] !== header);
  if (needsHeader) {
    headerRange.setValues([HEADERS]);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function normalizeCardData_(data) {
  const normalized = {};
  HEADERS.forEach((header) => {
    if (data[header] !== undefined && data[header] !== null) {
      normalized[header] = LIST_FIELDS.indexOf(header) >= 0 ? asList_(data[header]) : data[header];
    }
  });
  normalized.fit_score = Number(normalized.fit_score || 0);
  normalized.user_id = normalized.user_id || 'anonymous';
  return normalized;
}

function findRowByCardId_(sheet, cardId) {
  if (!cardId || sheet.getLastRow() < 2) return -1;
  const values = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues();
  for (let index = 0; index < values.length; index += 1) {
    if (values[index][0] === cardId) {
      return index + 2;
    }
  }
  return -1;
}

function nextCardId_(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return 'CM001';
  const ids = sheet.getRange(2, 1, lastRow - 1, 1).getValues().flat();
  const maxNumber = ids.reduce((max, id) => {
    const match = String(id || '').match(/^CM(\d+)$/);
    return match ? Math.max(max, Number(match[1])) : max;
  }, 0);
  return `CM${String(maxNumber + 1).padStart(3, '0')}`;
}

function cardToRow_(card) {
  return HEADERS.map((header) => {
    const value = card[header];
    if (LIST_FIELDS.indexOf(header) >= 0) {
      return asList_(value).join('\n');
    }
    return value === undefined || value === null ? '' : value;
  });
}

function rowToCard_(row) {
  return HEADERS.reduce((card, header, index) => {
    const value = row[index];
    card[header] = LIST_FIELDS.indexOf(header) >= 0 ? asList_(value) : value;
    return card;
  }, {});
}

function asList_(value) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean);
  }
  return String(value || '')
    .split(/[\n,、]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizePlacement_(placement) {
  return {
    part_id: String(placement.part_id || ''),
    x: Number(placement.x || 0),
    y: Number(placement.y || 0),
    z: Number(placement.z || 0),
  };
}

function extractResponseText_(response) {
  if (response.output_text) return response.output_text;
  const message = (response.output || []).find((item) => item.type === 'message');
  const textPart = message && (message.content || []).find((item) => item.type === 'output_text');
  if (!textPart || !textPart.text) {
    throw new Error(`OpenAI response did not include output text: ${JSON.stringify(response)}`);
  }
  return textPart.text;
}

function buildMockLayout_(struct) {
  const type = struct.type || '';
  if (type.indexOf('技術') >= 0 || type.indexOf('サポートAI') >= 0) {
    return {
      zone: 'lab',
      avatar_type: 'navigator_ai',
      role: struct.role_candidate || 'builder',
      placements: [
        { part_id: 'lab_base', x: 0, y: 0, z: 0 },
        { part_id: 'console_gate', x: 3, y: 0, z: 2 },
      ],
    };
  }
  return {
    zone: 'sea',
    avatar_type: 'seagull',
    role: struct.role_candidate || 'explorer',
    placements: [
      { part_id: 'sea_base', x: 0, y: 0, z: 0 },
      { part_id: 'lighthouse', x: 5, y: 0, z: 3 },
    ],
  };
}

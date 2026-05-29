const form = document.getElementById('careerCardForm');
const saveButton = document.getElementById('saveButton');
const agiButton = document.getElementById('agiButton');
const statusBadge = document.getElementById('statusBadge');
const structOutput = document.getElementById('structOutput');
const layoutOutput = document.getElementById('layoutOutput');

const listFields = ['stop', 'keep', 'start', 'experience', 'skill', 'environment'];

function setStatus(message, state = '') {
  statusBadge.textContent = message;
  statusBadge.className = `status-badge ${state}`.trim();
}

function setBusy(isBusy) {
  saveButton.disabled = isBusy;
  agiButton.disabled = isBusy;
}

function parseList(value) {
  return String(value || '')
    .split(/[\n,、]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function stringifyList(value) {
  if (Array.isArray(value)) {
    return value.join('\n');
  }
  return String(value || '');
}

function formToCardData() {
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());
  listFields.forEach((field) => {
    data[field] = parseList(data[field]);
  });
  data.fit_score = Number(data.fit_score || 0);
  return data;
}

function applyCardToForm(card) {
  Object.entries(card || {}).forEach(([key, value]) => {
    const input = form.elements[key];
    if (!input) return;
    input.value = listFields.includes(key) ? stringifyList(value) : value ?? '';
  });
}

function printJson(element, value) {
  element.textContent = JSON.stringify(value || {}, null, 2);
}

function gasRun(functionName, ...args) {
  return new Promise((resolve, reject) => {
    if (!window.google?.script?.run) {
      reject(new Error('google.script.run が見つかりません。Google Apps Script Webアプリとしてデプロイして実行してください。'));
      return;
    }

    window.google.script.run
      .withSuccessHandler(resolve)
      .withFailureHandler((error) => reject(new Error(error?.message || error)))
      [functionName](...args);
  });
}

async function saveCurrentCard(options = {}) {
  const shouldToggleBusy = options.toggleBusy !== false;
  if (shouldToggleBusy) setBusy(true);
  setStatus('保存中...');
  try {
    const savedCard = await gasRun('saveCard', formToCardData());
    applyCardToForm(savedCard);
    const struct = await gasRun('generateStruct', savedCard.card_id);
    printJson(structOutput, struct);
    setStatus(`保存済み: ${savedCard.card_id}`, 'success');
    return savedCard;
  } catch (error) {
    setStatus('保存エラー', 'error');
    throw error;
  } finally {
    if (shouldToggleBusy) setBusy(false);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    await saveCurrentCard();
  } catch (error) {
    window.alert(error.message);
  }
});

agiButton.addEventListener('click', async () => {
  setBusy(true);
  setStatus('AGI判定中...');
  try {
    let cardId = form.elements.card_id.value;
    if (!cardId) {
      const savedCard = await saveCurrentCard({ toggleBusy: false });
      cardId = savedCard.card_id;
    }

    const struct = await gasRun('generateStruct', cardId);
    printJson(structOutput, struct);

    const layoutCommand = await gasRun('generateLayout', cardId);
    printJson(layoutOutput, layoutCommand);
    setStatus(`AGI判定完了: ${cardId}`, 'success');
  } catch (error) {
    setStatus('AGI判定エラー', 'error');
    window.alert(error.message);
  } finally {
    setBusy(false);
  }
});

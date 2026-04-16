import Chart from "chart.js/auto";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5056";

function validateApiUrl(url) {
  if (!url || !/^https?:\/\//i.test(url)) {
    throw new Error(
      `Invalid VITE_API_BASE_URL: "${url}". Set it to a backend URL like http://127.0.0.1:5055`
    );
  }
}

const form = document.getElementById("prompt-form");
const input = document.getElementById("prompt-input");
const chatLog = document.getElementById("chat-log");
const sendBtn = document.getElementById("send-btn");
const keyNotesList = document.getElementById("key-notes-list");
const noteForm = document.getElementById("note-form");
const noteInput = document.getElementById("note-input");
const infoBachelor = document.getElementById("info-bachelor");
const infoMaster = document.getElementById("info-master");
const lensBreakEven = document.getElementById("lens-break-even");

const noteKeySet = new Set();

function autoResizePromptField() {
  const styles = window.getComputedStyle(input);
  const lineHeight = Number.parseFloat(styles.lineHeight) || 22;
  const paddingTop = Number.parseFloat(styles.paddingTop) || 0;
  const paddingBottom = Number.parseFloat(styles.paddingBottom) || 0;
  const maxHeight = (lineHeight * 4) + paddingTop + paddingBottom;

  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, maxHeight)}px`;
}

const BASELINE_SCENARIO = {
  bachelorDebt: 27437,
  masterDebt: 61667,
  repaymentYears: 10,
  interestRate: 5,
  bachelorSalary: 85500,
  masterSalary: 95400,
  growthRate: 3,
  taxRate: 24,
  costIndex: 1
};

function addMessage(role, content) {
  const node = document.createElement("article");
  node.className = `message ${role}`;
  node.textContent = content;
  chatLog.appendChild(node);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function addChartMessage(graph) {
  if (!graph?.data || !graph?.type) return;

  const wrapper = document.createElement("article");
  wrapper.className = "message assistant message-graph";

  const title = document.createElement("p");
  title.className = "graph-title";
  title.textContent = graph.title || "ROI visualization";

  const canvas = document.createElement("canvas");
  canvas.className = "graph-frame";
  canvas.setAttribute("aria-label", graph.title || "Chart output");
  canvas.setAttribute("role", "img");

  wrapper.appendChild(title);
  wrapper.appendChild(canvas);
  chatLog.appendChild(wrapper);
  chatLog.scrollTop = chatLog.scrollHeight;

  const config = {
    type: graph.type,
    data: graph.data,
    options: graph.options || {}
  };

  new Chart(canvas.getContext("2d"), config);
}

function calculateMonthlyPayment(principal, annualRate, yearsToRepay) {
  if (principal <= 0 || yearsToRepay <= 0) return 0;

  const monthlyRate = annualRate / 100 / 12;
  const numPayments = yearsToRepay * 12;

  if (monthlyRate === 0) {
    return principal / numPayments;
  }

  const numerator = monthlyRate * Math.pow(1 + monthlyRate, numPayments);
  const denominator = Math.pow(1 + monthlyRate, numPayments) - 1;
  return principal * (numerator / denominator);
}

function projectEarnings({
  startSalary,
  growthRate,
  yearsToProject = 30,
  totalDebt = 0,
  annualRate = 5,
  repaymentYears = 10,
  taxRate = 0,
  costIndex = 1
}) {
  const projection = [];
  let currentSalary = startSalary;
  let cumulativeEarnings = 0;

  const monthlyPayment = calculateMonthlyPayment(totalDebt, annualRate, repaymentYears);
  const annualPayment = monthlyPayment * 12;

  for (let year = 0; year <= yearsToProject; year += 1) {
    if (year > 0) {
      currentSalary *= 1 + growthRate / 100;
    }

    const isRepayingDebt = year > 0 && year <= repaymentYears;
    const paymentThisYear = isRepayingDebt ? annualPayment : 0;

    const taxAmount = currentSalary * (taxRate / 100);
    const afterTaxIncome = currentSalary - taxAmount;
    const costAdjustedIncome = costIndex > 0 ? afterTaxIncome / costIndex : afterTaxIncome;
    const netEarningsThisYear = costAdjustedIncome - paymentThisYear;

    cumulativeEarnings += netEarningsThisYear;

    projection.push({
      year,
      netEarningsThisYear: Math.round(netEarningsThisYear),
      cumulativeNet: Math.round(cumulativeEarnings)
    });
  }

  return projection;
}

function computeBreakEvenYear(bachelorProjection, masterProjection) {
  const years = Math.min(bachelorProjection.length, masterProjection.length);
  for (let i = 0; i < years; i += 1) {
    if (masterProjection[i].cumulativeNet >= bachelorProjection[i].cumulativeNet) {
      return i;
    }
  }
  return null;
}

function buildFinancialSummary(scenario = BASELINE_SCENARIO) {
  const bachelorProjection = projectEarnings({
    startSalary: scenario.bachelorSalary,
    growthRate: scenario.growthRate,
    totalDebt: scenario.bachelorDebt,
    annualRate: scenario.interestRate,
    repaymentYears: scenario.repaymentYears,
    taxRate: scenario.taxRate,
    costIndex: scenario.costIndex
  });

  const masterProjection = projectEarnings({
    startSalary: scenario.masterSalary,
    growthRate: scenario.growthRate,
    totalDebt: scenario.masterDebt,
    annualRate: scenario.interestRate,
    repaymentYears: scenario.repaymentYears,
    taxRate: scenario.taxRate,
    costIndex: scenario.costIndex
  });

  const breakEvenYear = computeBreakEvenYear(bachelorProjection, masterProjection);
  const bachelorTotal30 = bachelorProjection[30].cumulativeNet;
  const masterTotal30 = masterProjection[30].cumulativeNet;
  const advantage30 = masterTotal30 - bachelorTotal30;
  const advantage15 = masterProjection[15].cumulativeNet - bachelorProjection[15].cumulativeNet;

  return {
    scenario,
    breakEvenYear,
    bachelorMonthly: Math.round(
      calculateMonthlyPayment(scenario.bachelorDebt, scenario.interestRate, scenario.repaymentYears)
    ),
    masterMonthly: Math.round(
      calculateMonthlyPayment(scenario.masterDebt, scenario.interestRate, scenario.repaymentYears)
    ),
    bachelorTotal30,
    masterTotal30,
    advantage30,
    advantage15
  };
}

function formatMoney(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  }).format(value);
}

function addKeyNote(text) {
  const normalized = text.trim();
  if (!normalized) return;

  const key = normalized.toLowerCase();
  if (noteKeySet.has(key)) return;
  noteKeySet.add(key);

  const item = document.createElement("li");

  const noteText = document.createElement("span");
  noteText.className = "note-text";
  noteText.contentEditable = "true";
  noteText.spellcheck = true;
  noteText.textContent = normalized;
  noteText.dataset.noteKey = key;

  noteText.addEventListener("blur", () => {
    const oldKey = noteText.dataset.noteKey;
    const updated = noteText.textContent.trim();

    if (!updated) {
      noteKeySet.delete(oldKey);
      item.remove();
      return;
    }

    const newKey = updated.toLowerCase();
    if (newKey !== oldKey) {
      noteKeySet.delete(oldKey);
      if (noteKeySet.has(newKey)) {
        item.remove();
        return;
      }
      noteKeySet.add(newKey);
      noteText.dataset.noteKey = newKey;
    }
  });

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "note-remove";
  removeBtn.textContent = "Remove";

  removeBtn.addEventListener("click", () => {
    noteKeySet.delete(noteText.dataset.noteKey);
    item.remove();
  });

  item.appendChild(noteText);
  item.appendChild(removeBtn);
  keyNotesList.appendChild(item);
}

function extractKeyNotesFromAnswer(answer) {
  const cleaned = String(answer || "").replace(/\s+/g, " ").trim();
  if (!cleaned) return [];

  const sentences = cleaned
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean);

  if (sentences.length <= 2) {
    return sentences.length === 1 ? [sentences[0], sentences[0]] : sentences;
  }

  const parts = [[], []];
  let lenA = 0;
  let lenB = 0;

  for (const sentence of sentences) {
    if (lenA <= lenB) {
      parts[0].push(sentence);
      lenA += sentence.length;
    } else {
      parts[1].push(sentence);
      lenB += sentence.length;
    }
  }

  const note1 = parts[0].join(" ").trim();
  const note2 = parts[1].join(" ").trim();

  if (!note2) {
    return [note1, note1];
  }

  return [note1, note2];
}

function populateTopGeneralInfo(summary) {
  infoBachelor.textContent = `Bachelor baseline: ${formatMoney(summary.scenario.bachelorSalary)} salary, ${formatMoney(summary.scenario.bachelorDebt)} debt`;
  infoMaster.textContent = `Master baseline: ${formatMoney(summary.scenario.masterSalary)} salary, ${formatMoney(summary.scenario.masterDebt)} debt`;
  lensBreakEven.textContent = `Break-even year: ${summary.breakEvenYear === null ? "No break-even within 30 years" : `Year ${summary.breakEvenYear}`}`;
}

async function askAdvisor(userPrompt) {
  validateApiUrl(API_BASE_URL);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        prompt: userPrompt
      })
    });
  } catch (error) {
    if (String(error?.message || "").toLowerCase().includes("failed to fetch")) {
      throw new Error(
        `Cannot reach backend at ${API_BASE_URL}. Start it with: python -m backend.app`
      );
    }
    throw error;
  }

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Backend error ${response.status}: ${errText}`);
  }

  const payload = await response.json();
  if (!payload?.answer) {
    throw new Error("Backend returned no answer text.");
  }

  return payload;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const prompt = input.value.trim();
  if (!prompt) return;

  addMessage("user", prompt);
  input.value = "";
  autoResizePromptField();

  sendBtn.disabled = true;
  addMessage("system", "Analyzing with cached data and ROI engine...");

  try {
    const result = await askAdvisor(prompt);
    addMessage("assistant", result.answer);

    if (result?.graph) {
      addChartMessage(result.graph);
    }

    if (result?.metadata?.university_names?.length) {
      addMessage(
        "system",
        `Resolved universities: ${result.metadata.university_names.join(", ")}.`
      );
    }

    const extractedNotes = extractKeyNotesFromAnswer(result.answer);
    extractedNotes.forEach((note) => addKeyNote(note));
  } catch (error) {
    addMessage("assistant", `Error: ${error.message}`);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
});

noteForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const customNote = noteInput.value.trim();
  if (!customNote) return;
  addKeyNote(customNote);
  noteInput.value = "";
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

input.addEventListener("input", autoResizePromptField);

const initialSummary = buildFinancialSummary();
autoResizePromptField();
populateTopGeneralInfo(initialSummary);
addKeyNote(`Baseline break-even: ${initialSummary.breakEvenYear === null ? "No break-even in 30 years" : `Year ${initialSummary.breakEvenYear}`}`);
addKeyNote(`30-year model advantage: ${formatMoney(initialSummary.advantage30)} (Master - Bachelor)`);
addKeyNote(`Debt assumptions: Bachelor ${formatMoney(initialSummary.scenario.bachelorDebt)}, Master ${formatMoney(initialSummary.scenario.masterDebt)}`);

addMessage(
  "assistant",
  "Ask a question about whether a CS Master's is worth it. I will use cached university data and ROI modeling to respond."
);

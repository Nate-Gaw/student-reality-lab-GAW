const ADVISOR_API_URL = import.meta.env.VITE_ADVISOR_API_URL || "http://127.0.0.1:5055";

function validateAdvisorUrl(url) {
  // Prevent accidental placement of API keys in the advisor URL config.
  if (!url || !/^https?:\/\//i.test(url)) {
    throw new Error(
      `Invalid VITE_ADVISOR_API_URL: "${url}". Set it to a bridge URL like http://127.0.0.1:5055`
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

function addGraphMessage(graph) {
  if (!graph?.html) return;

  const wrapper = document.createElement("article");
  wrapper.className = "message assistant message-graph";

  const title = document.createElement("p");
  title.className = "graph-title";
  title.textContent = graph.title || "Graph MCP Visualization";

  const frame = document.createElement("iframe");
  frame.className = "graph-frame";
  frame.setAttribute("title", graph.title || "Graph output");
  frame.setAttribute("loading", "lazy");
  frame.srcdoc = graph.html;

  wrapper.appendChild(title);
  wrapper.appendChild(frame);
  chatLog.appendChild(wrapper);
  chatLog.scrollTop = chatLog.scrollHeight;
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

function buildSystemPrompt(summary) {
  return [
    "You are a decision advisor focused on whether a Master's in CS is financially worth it.",
    "Reason using the provided model outputs and explain in plain language.",
    "Keep answers concise and structured.",
    "Always include:",
    "1) Direct recommendation",
    "2) Why (break-even + 30-year advantage)",
    "3) Risk caveats (debt, taxes, growth assumptions)",
    "4) One actionable next step",
    "Financial model context:",
    `- Baseline Bachelor debt: ${summary.scenario.bachelorDebt}`,
    `- Baseline Master debt: ${summary.scenario.masterDebt}`,
    `- Baseline Bachelor salary: ${summary.scenario.bachelorSalary}`,
    `- Baseline Master salary: ${summary.scenario.masterSalary}`,
    `- Interest rate: ${summary.scenario.interestRate}%`,
    `- Salary growth: ${summary.scenario.growthRate}%`,
    `- Tax rate: ${summary.scenario.taxRate}%`,
    `- Break-even year: ${summary.breakEvenYear ?? "No break-even in 30 years"}`,
    `- Bachelor monthly loan: ${summary.bachelorMonthly}`,
    `- Master monthly loan: ${summary.masterMonthly}`,
    `- Bachelor 30-year net: ${summary.bachelorTotal30}`,
    `- Master 30-year net: ${summary.masterTotal30}`,
    `- 15-year advantage (Master-Bachelor): ${summary.advantage15}`,
    `- 30-year advantage (Master-Bachelor): ${summary.advantage30}`
  ].join("\n");
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
  // Extract all key information components
  const info = {
    recommendation: null,
    breakEven: null,
    advantage: null,
    debt: null,
    university: null,
    cost: null,
    risks: [],
    actions: []
  };

  // Extract recommendation
  const recommendMatch = answer.match(/(?:recommend|suggestion|verdict):\s*([^.!?]+[.!?])/i);
  if (recommendMatch) {
    info.recommendation = recommendMatch[1].trim();
  }

  // Extract break-even
  const breakEvenMatch = answer.match(/break-?even[^.!?]*?(year\s*\d+|\d+\s*years?|never|not\s+achieve)/i);
  if (breakEvenMatch) {
    info.breakEven = breakEvenMatch[0].trim();
  }

  // Extract 30-year advantage
  const advantageMatch = answer.match(/(30-year|lifetime)\s+advantage[^.!?]*(\$[\d,]+)/i);
  if (advantageMatch) {
    info.advantage = advantageMatch[2].trim();
  }

  // Extract debt information
  const debtMatch = answer.match(/debt[^.!?]*(\$[\d,]+)/i);
  if (debtMatch) {
    info.debt = debtMatch[0].trim();
  }

  // Extract university-specific information
  const universityMatch = answer.match(/(Stanford|MIT|Rutgers|Harvard|[A-Z][a-z]+\s+University)[^.!?]*(?:tuition|cost|annual)[^.!?]*(\$[\d,]+)/i);
  if (universityMatch) {
    info.university = universityMatch[0].trim();
  }

  // Extract total cost information
  const costMatch = answer.match(/total\s+(?:annual\s+)?cost[^.!?]*(\$[\d,]+)/i);
  if (costMatch) {
    info.cost = costMatch[0].trim();
  }

  // Extract all risk/caveat mentions
  const riskMatches = answer.matchAll(/(?:risk|caution|concern|caveat|however|but)[^.!?]*?([^.!?]{15,100}[.!?])/gi);
  for (const match of riskMatches) {
    info.risks.push(match[1].trim());
  }

  // Extract action items
  const actionMatches = answer.matchAll(/(?:next step|action|should|consider|explore|check)[^.!?]*?([^.!?]{15,100}[.!?])/gi);
  for (const match of actionMatches) {
    info.actions.push(match[1].trim());
  }

  // Compile comprehensive summary and split into 1-2 notes
  const notes = [];

  // Note 1: Primary decision and financial summary
  const note1Parts = [];
  if (info.recommendation) {
    note1Parts.push(info.recommendation);
  }
  if (info.university) {
    note1Parts.push(info.university);
  } else if (info.cost) {
    note1Parts.push(info.cost);
  }
  if (info.breakEven) {
    note1Parts.push(info.breakEven);
  }
  if (info.advantage) {
    note1Parts.push(`30-year advantage: ${info.advantage}`);
  } else if (info.debt && !info.university) {
    note1Parts.push(info.debt);
  }

  if (note1Parts.length > 0) {
    notes.push(note1Parts.join('. '));
  }

  // Note 2: Risks, considerations, and actions
  const note2Parts = [];
  if (info.risks.length > 0) {
    // Take the most relevant risk (usually first or longest)
    const mainRisk = info.risks.sort((a, b) => b.length - a.length)[0];
    note2Parts.push(`Risk: ${mainRisk}`);
  }
  if (info.actions.length > 0) {
    // Take the most actionable item
    const mainAction = info.actions[0];
    note2Parts.push(`Action: ${mainAction}`);
  }

  if (note2Parts.length > 0) {
    notes.push(note2Parts.join(' '));
  }

  // Return max 2 comprehensive notes
  return notes.slice(0, 2);
}

function populateTopGeneralInfo(summary) {
  infoBachelor.textContent = `Bachelor baseline: ${formatMoney(summary.scenario.bachelorSalary)} salary, ${formatMoney(summary.scenario.bachelorDebt)} debt`;
  infoMaster.textContent = `Master baseline: ${formatMoney(summary.scenario.masterSalary)} salary, ${formatMoney(summary.scenario.masterDebt)} debt`;
  lensBreakEven.textContent = `Break-even year: ${summary.breakEvenYear === null ? "No break-even within 30 years" : `Year ${summary.breakEvenYear}`}`;
}

function extractResponseText(payload) {
  if (!payload || typeof payload !== "object") return "";

  if (typeof payload.output_text === "string" && payload.output_text.trim()) {
    return payload.output_text.trim();
  }

  if (Array.isArray(payload.output)) {
    const collected = [];

    for (const item of payload.output) {
      if (!item || !Array.isArray(item.content)) continue;

      for (const block of item.content) {
        const maybeText = typeof block?.text === "string" ? block.text : block?.text?.value;
        if (typeof maybeText === "string" && maybeText.trim()) {
          collected.push(maybeText.trim());
        }
      }
    }

    if (collected.length) {
      return collected.join("\n\n");
    }
  }

  if (Array.isArray(payload.choices)) {
    const choice0 = payload.choices[0];
    const content = choice0?.message?.content;

    if (typeof content === "string" && content.trim()) {
      return content.trim();
    }

    if (Array.isArray(content)) {
      const fromParts = content
        .map((part) => (typeof part?.text === "string" ? part.text : ""))
        .filter(Boolean)
        .join("\n\n")
        .trim();

      if (fromParts) return fromParts;
    }
  }

  return "";
}

async function askAdvisor(userPrompt) {
  validateAdvisorUrl(ADVISOR_API_URL);

  let response;
  try {
    response = await fetch(`${ADVISOR_API_URL}/api/advisor`, {
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
        `Cannot reach MCP advisor bridge at ${ADVISOR_API_URL}. Start it with: python mcp_bridge.py`
      );
    }
    throw error;
  }

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Advisor bridge error ${response.status}: ${errText}`);
  }

  const payload = await response.json();
  if (!payload?.answer) {
    throw new Error("Advisor bridge returned no answer text.");
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
  addMessage("system", "Analyzing with University Cost MCP + Graph MCP...");

  try {
    const result = await askAdvisor(prompt);
    addMessage("assistant", result.answer);

    if (result?.mcp?.graph?.used && result?.graph?.html) {
      addGraphMessage(result.graph);
    }

    if (result?.mcp?.universityCost?.used) {
      const mode = result.mcp.universityCost.mode;
      
      if (mode === "university_detected_unavailable") {
        // Handle both single and multiple detected universities
        const detected = result?.universityData?.detected_university;
        const detectedList = result?.universityData?.detected_universities;
        
        if (detectedList && detectedList.length > 0) {
          const universityList = detectedList.join(", ");
          addMessage(
            "system",
            `Recognized your question about ${universityList}, but detailed cost data for these universities is not currently available in our database. The advisor is using baseline projections for comparison.`
          );
        } else if (detected) {
          addMessage(
            "system",
            `Recognized your question about ${detected}, but detailed cost data for this university is not currently available in our database. The advisor can only provide general guidance.`
          );
        }
      } else if (mode === "compare_university_costs") {
        addMessage(
          "system",
          `University Cost MCP retrieved data for multiple universities${result?.graph?.html ? `; Graph MCP generated a ${result?.graph?.type || "chart"}` : ""}.`
        );
      } else {
        addMessage(
          "system",
          `University Cost MCP used via ${mode || "query"}${result?.graph?.html ? `; Graph MCP generated a ${result?.graph?.type || "chart"}` : ""}.`
        );
      }
    } else {
      addMessage(
        "system",
        "Using baseline financial model and Graph MCP for projections."
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
  "Ask a question about whether a CS Master's is worth it. I now use University Cost MCP for cost data when relevant and Graph MCP for projections/comparisons."
);

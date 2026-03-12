# Website Rebuild Sprints

## Sprint 1 - Foundation and Environment
Status: Completed

- Created fresh project scaffold in `Website/`.
- Added `.env` with `VITE_OPENAI_API_KEY` placeholder.
- Added `package.json` scripts for Vite.
- Added `.gitignore` to protect `.env`.

## Sprint 2 - Chat Interface
Status: Completed

- Built a ChatGPT-style layout with:
  - title,
  - conversation area,
  - single prompt input line and send button.
- Added responsive styling for desktop and mobile.

## Sprint 3 - Financial Reasoning Engine
Status: Completed

- Implemented the same modeling logic pattern as prior site:
  - loan payment calculation,
  - annual projection for Bachelor and Master paths,
  - break-even detection,
  - 15-year and 30-year advantage summaries.
- Connected model output as context for LLM answers.

## Sprint 4 - LLM Integration and UX
Status: Completed

- Added OpenAI Responses API call using env key.
- Added system prompt enforcing recommendation + reasoning structure.
- Added loading/system state and runtime error feedback in chat.

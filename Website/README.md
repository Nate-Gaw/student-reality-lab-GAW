# CS Master's Worth It? Chat Advisor

A rebuilt website with a ChatGPT-style interface focused on one question:
`Is a Master's in CS worth it financially?`

This Website now integrates both new MCP systems:
- `university-cost-mcp` for university tuition/cost data when relevant
- `graph-generation-mcp` for projections and cost visualizations

## Setup

```bash
cd "D:/College Classes/IS219/student-reality-lab-GAW/Website"
npm install
pip install -r requirements.txt
python mcp_bridge.py
```

Create and maintain one shared env file at `student-reality-lab-GAW/.env`:

```env
OPENAI_API_KEY=your_key_here
VITE_ADVISOR_API_URL=http://127.0.0.1:5055
DATABASE_URL=sqlite:///universities.db
```

In a second terminal:

```bash
cd "D:/College Classes/IS219/student-reality-lab-GAW/Website"
npm run dev
```

The frontend reads `VITE_ADVISOR_API_URL` from the shared root `.env`.

## How It Works

- Uses the same core financial process as the old site:
  - amortized loan payment,
  - year-by-year net earnings projection,
  - break-even year detection,
  - 15-year and 30-year net advantage.
- Calls `mcp_bridge.py` backend route (`/api/advisor`) instead of OpenAI directly from browser.
- Bridge enriches prompts with:
  - University data context from `university-cost-mcp` when user asks cost/university questions.
  - Graph metadata from `graph-generation-mcp` for projection/cost reasoning.
- Bridge returns text + graph HTML; Website renders graph inline in chat.

## Notes

- API key is kept server-side in bridge process (`OPENAI_API_KEY`).
- Graph MCP is always used for projection/cost visual support.
- University MCP is used when query intent matches university/cost/tuition context.

## Sprint Tracking

- Sprint files now live in `sprints/`.
- Current sprint log: `sprints/sprint-01-2026-03-09-website-rebuild.md`.
- Future sprint files must follow: `sprint-XX-YYYY-MM-DD-short-topic.md`.
- Naming convention reference: `sprints/README.md`.

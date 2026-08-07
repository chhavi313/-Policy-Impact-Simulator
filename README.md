# Policy Impact Simulator (MVP)

An exploratory, local tool: describe a policy, and see a rough sense of how
a synthetic population might react — support %, sentiment, and group
breakdowns — visualized in-app. Not a real-world prediction tool.

## Features
- AI-generated policy response simulation using Gemini API
- Representative synthetic population generation
- Overall support percentage calculation
- Sentiment analysis
- Population group breakdown
- Interactive Streamlit dashboard

## How it works

1. **Population** (`population.py`) — instead of simulating millions of
   individuals one by one, it builds a set of *weighted representative
   segments* (combinations of ethnicity × employment status × income tier),
   using illustrative, editable distribution/correlation assumptions.
2. **Reactions** (`reactions.py`) — for each segment, one Gemini API call
   generates a plausible reaction (support %, sentiment, rationale, key
   benefits/concerns), grounded in economic/social reasoning tied to
   employment and income — not ethnic stereotyping.
3. **Aggregation** (`aggregate.py`) — rolls segment reactions up into
   overall and group-level stats, weighted by population share.
4. **Visualization** (`app.py`) — Streamlit dashboard: KPIs, gauge, sentiment
   distribution, breakdown bar charts, and expandable per-segment detail
   cards. You can run multiple policies in one session and have detailed expandable response cards.

## Setup

```bash
git clone <repository-url>
cd policy-impact-simulator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste your real Gemini API key
```

## Run

```bash
streamlit run app.py
```

This opens the app in your browser (usually http://localhost:8501).

## Technologies Used
- Python
- Streamlit
- Google Gemini API
- Pandas
- Plotly

## Notes / things you may want to tune

- **Population weighting assumptions**: see the `ETHNICITY_DIST`,
  `EMPLOYMENT_DIST`, `INCOME_DIST`, and `EMPLOYMENT_INCOME_CORRELATION`
  tables at the top of `population.py`. These are illustrative, not real
  demographic data — edit freely for your context (e.g. a specific
  country's income/employment distribution).
- **Model**: defaults to `gemini-3.1-flash-lite` for speed/cost.
- **Reliability**: if a segment's API call fails after retries, it falls
  back to a neutral placeholder (50% support, 0 sentiment) rather than
  crashing the whole run — you'll see `"error": true` on that segment.

## What's intentionally out of scope 

- Exporting a shareable report file (results are for on-screen viewing)
- Very large populations 
- Multiple simulation modes, side-by-side comparison, individual narrative
  detail (diary-style entries per person)

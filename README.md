# GTM Signal Intelligence

Signal-driven GTM intelligence for AI-infrastructure providers (GPU cloud, colocation, build-to-suit). 396 prospect profiles across 17 segments, 24 competitors across 6 market segments, 19 free-source data collectors (including Northern Virginia land-use and incentive pipelines), AI-generated briefs and a daily digest, and a scoring engine that surfaces timing.

> Built in early 2026 as a demo for an AI-infrastructure provider. The seller's identity is a configurable provider profile (`PROVIDER_PROFILE` in `config.py`, overridable from `private/provider_config.py`). The repo ships with a neutral sample profile and no proprietary data.

## The Problem

An AI-infrastructure provider sells $10M+ deals (GPU cloud, colocation, build-to-suit data centers) to AI labs, enterprise companies, and hyperscalers. The commercial team tracks hundreds of prospects across segments from foundation model labs to quant trading firms to defense contractors. Manual signal tracking doesn't scale. By the time a rep reads about a funding round in the news, the prospect has already fielded five vendor calls. The companies that win these deals detect need before budget, and detect budget before evaluation.

This platform automates that. Public signals are collected continuously, scored for urgency, and translated into prioritized outreach with timing windows and recommended next actions.

## The Approach

Signal intelligence mapped to the buyer journey. Every prospect signal maps to one of three stages:

**Need Detected.** Company is scaling AI compute. Hiring infra engineers, publishing ML papers, pushing to GPU-related GitHub repos, announcing AI initiatives. They'll need capacity in 3 to 9 months.

**Budget Available.** Company just raised capital or has CAPEX allocated. SEC filings, funding news, earnings calls showing infrastructure spend. Procurement conversations start within a quarter.

**Actively Evaluating.** Company is outgrowing its current provider. Capacity complaints, migration signals, vendor switching discussions. This is the highest-urgency window: they're in-market now.

19 data collectors pull from free public sources. A weighted scoring engine with exponential recency decay ranks prospects across 6 signal categories (max 100 points). AI-generated briefs surface what happened, why it matters, what to do, and by when. A four-tier LLM cost model runs the entire collection pipeline for ~$0.15/run, with a premium Opus 4.6 tier for the daily digest.

A competitive intelligence layer tracks 24 competitors across 6 market segments (Neocloud, Hyperscaler, DC REIT, Power-First, International, Miner-to-HPC), each profiled with key customers, pricing intel, strengths and weaknesses, and a threat level relative to the provider. Prospect-level competitive context maps which competitors a rep is likely bidding against for any given deal, based on the prospect's product fit.

A regional data layer monitors VEDP press releases, county-level ArcGIS land-use datasets (Loudoun and Prince William), and state incentive reports to detect data center builds and grant recipients in Northern Virginia, the densest data center market in the US. It is the pattern for covering a provider's home market; the sample profile lists Northern Virginia as its home market.

## Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│  DATA SOURCES (all free)                                        │
│  RSS Feeds · Google News · SEC EDGAR · ATS (Greenhouse/Lever)   │
│  Earnings Transcripts · GitHub · ArXiv · Hacker News · Blogs    │
│  DuckDuckGo Search · VEDP · Loudoun/PWC ArcGIS · VEDP PDFs     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ 19 Collectors   │
                    │ (Python)        │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  Signals DB     │ │  Competitor   │ │  Ollama          │
│  (SQLite)       │ │  Events DB    │ │  Embeddings      │
└────────┬────────┘ └──────┬───────┘ └──────────────────┘
         │                 │
         ▼                 ▼
┌─────────────────────────────────────┐
│  Scoring Engine + Competitive Intel │
│  recency decay × magnitude ×       │
│  confidence + threat assessment     │
└────────────────┬────────────────────┘
                 │
    ┌────────────▼────────────┐
    │  AI Layer               │
    │  briefs, emails,        │
    │  battle cards, digest   │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │  FastAPI (JSON API)     │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │  Next.js Frontend       │
    └─────────────────────────┘
```

**LLM tiers:**

| Tier | Model | Cost | Role |
|------|-------|------|------|
| Free | Ollama `nomic-embed-text` (local) | $0 | Embeddings, dedup, semantic search |
| Bulk | Gemini 2.5 Flash | $0.30/$2.50 per M tokens | Signal classification, article summaries |
| Analysis | Kimi K2 | $0.55/$2.20 per M tokens | Briefs, outreach emails, battle cards |
| Premium | Opus 4.6 | $5.00/$25.00 per M tokens | Daily digest (2x/day, cached) |

Every AI call has a keyword-based fallback. Premium falls back to Analysis, Analysis falls back to Bulk, Bulk falls back to keyword extraction. The platform scores and surfaces prospects with zero API keys configured.

## Provider Profile

`PROVIDER_PROFILE` in `config.py` describes the seller: name, capacity (MW), GPU count and models, products (AI Cloud, Colocation, Build-to-Suit), locations, cooling, pricing, key customers, strengths, weaknesses, expansion plans, and home markets. `SEGMENT_PROFILES` holds the provider's positioning against each competitor segment.

The repo ships a sample profile, "Sample AI Cloud Provider". It is not a real company. Its numbers are round and illustrative (1,000 MW, 20,000 GPUs), chosen to sit mid-pack against the seeded competitors so threat levels and positioning read sensibly.

To run it for a real provider, add `private/provider_config.py` (gitignored) exporting `PROVIDER_PROFILE`, `COMPETITOR_SEGMENTS`, `SEGMENT_PROFILES` and `PRODUCT_FIT_TO_SEGMENTS`. On Railway, pass the same file through `PRIVATE_CONFIG_B64` (see `.env.example`); the key must be `provider_config.py`.

What reads the profile:

- `_build_provider_context()` in `ai/brief_generator.py` formats it into the context block at the top of every brief, outreach email, battle card, and the daily digest.
- `/api/compete/landscape` and `/api/competitors` return it as `provider`, which the Compete page pins at the top of the directory.
- `/api/prospects/{id}/competitive-context` returns the matching segment's `positioning` as `provider_edge`.
- Battle cards add the provider's own strengths and weaknesses as a self-assessment.

Competitor threat levels live in `database/seed.py` and are rated against the sample profile. Re-rate them for your own deployment.

## Signal Framework

| Signal | Buyer Stage | Detects | Engagement Window | Product Fit | Primary Collectors |
|--------|-------------|---------|-------------------|-------------|--------------------|
| Infrastructure Hiring | Need Detected | GPU/ML/infra job postings | 3-6 months | AI Cloud, Colo | ATS, HN, News |
| AI Initiatives | Need Detected | Model training, AI product launches | 3-9 months | AI Cloud | ArXiv, GitHub, News, Cloud Blogs |
| Cloud Spend | Need Detected | High cloud bills, cost optimization signals | 6-12 months | Colo | Earnings, Cloud Blogs |
| Active Fundraising | Budget Available | Currently raising; procurement starts soon | 60-90 days | AI Cloud, BTS | Funding, SEC, HN |
| Completed Funding | Budget Available | Round closed; infra purchasing within 1 quarter | 30-120 days | AI Cloud, BTS | Funding, SEC, HN |
| Outgrowing Provider | Actively Evaluating | Capacity complaints, provider switching | 1-3 months | All | HN, Earnings, News |

Each signal carries an urgency level (URGENT / HIGH / MEDIUM) and an action template: the full chain from "what happened" to "so what" to "do this" to "by when."

## Data Collectors

| Collector | Source | Signal Types | Cost |
|-----------|--------|-------------|------|
| `news` | RSS feeds (Data Center Dynamics, DCK, TechCrunch, Reuters) + Google News | All | Free |
| `funding` | Google News funding regex | fundraising, funding_completed | Free |
| `sec` | SEC EDGAR filings API | fundraising, funding_completed | Free |
| `jobs` | Google News job keyword detection | hiring | Free |
| `ats` | Greenhouse & Lever ATS APIs | hiring | Free |
| `earnings` | Earnings call transcripts | cloud_spend, ai_initiative, outgrowing | Free |
| `github` | GitHub API (repos, activity) | ai_initiative | Free |
| `arxiv` | ArXiv RSS (cs.AI, cs.LG, cs.CL) | ai_initiative | Free |
| `hn` | Hacker News API | hiring, fundraising, outgrowing | Free |
| `cloud_blogs` | AWS/GCP/Azure blog RSS | ai_initiative, cloud_spend | Free |
| `competitive_intel` | DuckDuckGo web search | CompetitorEvents (deal, expansion, pricing, talent) | Free |
| `press_releases` | Company press release pages | All | Free |
| `edgar_rss` | SEC EDGAR RSS (real-time filings) | fundraising, funding_completed | Free |
| `peeringdb` | PeeringDB API (network facility data) | cloud_spend | Free |
| `trends` | Google Trends (search interest) | ai_initiative | Free |
| `vedp` | VEDP press releases + sitemap | cloud_spend, ai_initiative | Free |
| `loudoun_dc` | Loudoun County ArcGIS BuildOut API | cloud_spend | Free |
| `pwc_dc` | Prince William County ArcGIS FeatureServer | cloud_spend | Free |
| `cof` | VEDP COF/VJIP incentive PDF reports | funding_completed | Free |

All collectors inherit from `BaseCollector`, which handles session management, semantic dedup via Ollama embeddings, and per-item error isolation (one failed article doesn't skip the rest). The `competitive_intel` collector searches for each competitor's recent deals, expansions, pricing changes, and talent moves, creating `CompetitorEvent` rows (separate from prospect signals). After collection, a signal reclassification pass runs to normalize signal types using keyword matching.

The four Virginia collectors form a regional market intelligence layer: VEDP tracks state economic development press releases for data center investments, the Loudoun and Prince William County collectors monitor ArcGIS land-use datasets for new builds and status changes, and the COF collector parses VEDP's semi-annual incentive PDF reports (COF and VJIP programs) to detect which companies received state grants.

## Prospect Coverage

396 prospect profiles across 17 segments, each tagged with a product fit (AI Cloud, Colocation, or Build-to-Suit):

| Segment | Count | Product Fit |
|---------|-------|-------------|
| Enterprise Software | 52 | Colocation |
| Biotech / Pharma / Healthcare | 48 | AI Cloud |
| AI Infrastructure & Developer Tools | 45 | AI Cloud |
| AI-Native Applications | 43 | AI Cloud |
| Fintech / Quantitative Trading | 39 | Colocation |
| AI Research / Foundation Models | 33 | AI Cloud |
| Government / Defense | 22 | Colocation |
| Gaming / Media / Entertainment | 21 | Colocation |
| Data Infrastructure | 20 | Colocation |
| Technology / Hyperscalers | 16 | Build-to-Suit |
| Crypto / Web3 | 13 | AI Cloud |
| Specialized AI Applications | 13 | AI Cloud |
| Autonomous Vehicles / Robotics | 10 | AI Cloud |
| Cybersecurity | 8 | AI Cloud |
| Bitcoin Mining / AI Infrastructure | 8 | Build-to-Suit |
| Infrastructure / Energy | 4 | Build-to-Suit |
| Enterprise AI / Data Analytics | 1 | Colocation |

**Product fit distribution:** 193 AI Cloud, 168 Colocation, 35 Build-to-Suit.

9 companies appear as both prospect and competitor (neoclouds and miners that buy and sell capacity). The seed stores each once, as a competitor, so a fresh database holds 387 prospects and 24 competitors.

## Competitive Intelligence

24 competitors tracked across 6 market segments. Each competitor is profiled with key customers, pricing intel, strengths, weaknesses, and a threat level (high/medium/low). This is the data a GTM strategy team would compile, structured for reps rather than analysts.

| Segment | Competitors | Key Battleground | Provider Positioning |
|---------|------------|------------------|----------------------|
| Neocloud | CoreWeave, Crusoe, Lambda, Nebius, Voltage Park | GPU availability, NVIDIA allocation, pricing/GPU-hr | The provider supplies the infrastructure neoclouds run on; they are both customers and competitors |
| Hyperscaler | AWS, Google Cloud | Scale (GW-level), speed to deploy, grid proximity | The provider builds overflow capacity when hyperscaler demand exceeds their own data center pipeline |
| DC REIT | Equinix, Digital Realty, QTS, CyrusOne, Vantage | Power density (kW/rack), campus scale, PUE | The provider differentiates on AI-ready high-density design and delivered power cost |
| Power-First | Lancium, Applied Digital | Power cost ($/kWh), MW pipeline, construction speed | Direct competitors running the same energy-first playbook |
| International | Adani Group | Geography, regulatory approval, talent access | The provider competes on proximity to US demand centers and operating track record |
| Miner-to-HPC | Hut 8, Core Scientific, Cipher Mining, HIVE Digital, TeraWulf, Bit Digital | Pivot execution speed, HPC customer contracts, power cost | Peers with a similar power-first cost structure; the provider differentiates on execution track record and customer quality |

**Threat assessment:** Each competitor is assigned a threat level based on overlap in product fit, customer type, and recent activity. Levels are relative to the configured provider; edit them per deployment.

**Prospect-level competitive context:** Every prospect's product fit (AI Cloud, Colocation, Build-to-Suit) maps to relevant competitor segments. When a rep opens a prospect, they see which competitors they're likely bidding against, recent competitive moves from those competitors, and the provider's positioning edge. The mapping:

- `ai_cloud` → Neocloud + Hyperscaler + Miner-to-HPC competitors
- `colocation` → DC REIT + Power-First competitors
- `build_to_suit` → Power-First + DC REIT + Miner-to-HPC competitors

**Data enrichment:** The `competitive_intel` collector runs web searches per competitor to discover recent deals, facility expansions, pricing changes, and executive hires. Results are classified and stored as `CompetitorEvent` rows, feeding the activity feed and competitive pulse.

## Scoring Model

Each prospect is scored 0–100 across 6 categories. Formula per signal:

```text
points = base_points × recency_decay × magnitude_multiplier × source_confidence
```

- **Recency decay**: exponential half-life per signal type. A hiring signal from last week scores higher than one from three months ago.
- **Magnitude multiplier**: tiered thresholds for funding amounts: smaller rounds score below baseline, large rounds score above, with fundraising multipliers slightly more aggressive than completed-funding because an active raise is a timing signal.
- **Source confidence**: SEC filing → major news → industry news → blog → social media → rumor, each discounted accordingly.
- **Category cap**: each signal type has a max_points ceiling. All caps sum to 100.

| Signal Type | Buyer Stage | Why It Matters |
|-------------|-------------|----------------|
| Infrastructure Hiring | Need Detected | Strongest leading indicator: each infra role posted accumulates pressure |
| Active Fundraising | Budget Available | Time-sensitive timing signal; fast decay reflects the narrow window |
| AI Initiatives | Need Detected | Training runs, model launches, GitHub infra scaling |
| Completed Funding | Budget Available | Capital deployed: infrastructure purchasing follows |
| Cloud Spend | Need Detected | Repatriation opportunity; slower decay reflects longer decision cycle |
| Outgrowing Provider | Actively Evaluating | In-market now; highest urgency |

Exact weights, half-lives, and magnitude thresholds are configurable per deployment.

## Frontend

Next.js 16 + React 19 + Tailwind CSS 4 + shadcn/ui. Four pages:

- **Today.** Dashboard with a prioritized call list, live funding tracker, competitive pulse card, and the daily digest. The call list ranks prospects by score x urgency and shows the engagement window for each. Competitive Pulse shows 7-day event and signal counts, the high-threat count, and the most active competitor.
- **Prospects.** Filterable table (by segment, product fit, score range) with expandable detail sheets. Each prospect has an AI brief, engagement window, persona contacts with recommended approaches, an outreach email draft, and a **Competitive Context** section showing the provider's edge, likely competitors, their threat levels, and recent moves.
- **Compete.** KPIs for events this week, the hottest competitor, and prospects with competing activity, then three tabs:
  - **Activity Feed.** Chronological feed of competitor events and signals, filterable by type (deal, expansion, pricing, talent). Links to source articles.
  - **Deal Threats.** High-scoring prospects where competitor activity overlaps with the prospect's product fit.
  - **Directory.** Sortable competitor table with segment filters, threat level badges, capacity bars, and activity counts. The provider's own row is pinned at the top with a YOU badge. Clicking a competitor opens a sheet with a vs-provider comparison (MW, GPUs, activity), key customers, strengths and weaknesses, and an AI battle card.
- **Admin.** Company management, scoring config, collector status, system health.

Signal cards display the full reasoning chain: **What happened** → **So what** → **Do this** → **By when**. Reps don't need to interpret signals: the platform tells them what the signal means for the provider and what the next action is.

## Quick Start

```bash
# Backend
pip install -r requirements.txt
cp .env.example .env  # add OPENROUTER_API_KEY for AI features

# Seed prospects + competitors (the API also does this on first start)
python -c "from database.seed import seed_database; seed_database()"

# If upgrading an existing database, run migration for new competitor fields
python3 scripts/add_company_columns.py

# Run all collectors (includes competitive intel web search)
python -m collectors.runner

# Or run just the competitive intel collector
python -m collectors.runner competitive_intel

# Score all prospects
python -c "from scoring.engine import score_all_prospects; score_all_prospects()"

# API
cd api && pip install -r requirements.txt
uvicorn main:app --reload --port 8000 &
cd ..

# Frontend
cd frontend && npm install && npm run dev
```

- Frontend: <http://localhost:3000>
- API docs: <http://localhost:8000/docs>
- Ollama (optional): `ollama pull nomic-embed-text` then `python -m ai.embed_backfill` for semantic dedup

The database lives at `data/gtm_signal_intel.db`. A fresh file is created and seeded on first run. If you have a database under an older filename, move it to that path or point `DATABASE_URL` at it.

## Deployment (Railway)

The app runs on Railway with two services in one project.

**API**: Root = repo root. Env: `DATABASE_URL=sqlite:////data/gtm_signal_intel.db`, `CORS_ORIGINS=*`. Add a **Volume** (mount `/data`) in the dashboard so SQLite persists. To use a real provider profile, set `PRIVATE_CONFIG_B64` with a `provider_config.py` key (see `.env.example`); without it the sample profile is used. Deploy: `./scripts/deploy_railway.sh api` (or `railway service api` → `railway up` from repo root).

**Frontend**: In the Railway dashboard, add a second service (Empty Service) named `frontend`. Set **Root Directory** to `frontend`. Set env `NEXT_PUBLIC_API_URL` to your API URL (e.g. `https://api-production-xxx.up.railway.app`). Generate a domain for the frontend service. Step-by-step: see **docs/RAILWAY_FRONTEND_SETUP.md**. Deploy: `./scripts/deploy_railway.sh frontend` (or `railway service frontend` → `railway up` from repo root).

See `api/README.md` for API-only deploy steps and volume setup. **CLI:** `railway add --service frontend --variables "NEXT_PUBLIC_API_URL=https://api-production-xxx.up.railway.app"` then `railway domain -s frontend`; set Root Directory to `frontend` in the dashboard once.

## Tech Stack

Python 3.14, FastAPI, SQLAlchemy 2.x, SQLite, OpenRouter (Kimi K2 + Gemini 2.5 Flash), Ollama (`nomic-embed-text`), pdfplumber, Next.js 16, React 19, Tailwind CSS 4, shadcn/ui, Recharts, TanStack Table.

## Cost Model

Four tiers: **Free** (Ollama local, $0 for all embeddings), **Bulk** (Gemini 2.5 Flash at ~$0.15/collection run for classification and summaries), **Analysis** (Kimi K2 at ~$0.05/request for briefs and emails), **Premium** (Opus 4.6 at ~$0.10/digest for the daily digest, 2x/day with caching). Full collection run + 10 AI briefs = ~$0.65. $15 total budget covers 30+ collection runs, 50+ analysis requests, and 60 daily digests.

## Tests

```bash
python -m pytest tests/ -v  # no API keys or Ollama needed
```

All tests use in-memory SQLite and mocked embeddings. No external services required.

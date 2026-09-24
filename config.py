# Why: Central env vars, constants, enums
# Deps: os, pathlib, dotenv
# How: Reads .env then exports typed defaults

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'gtm_signal_intel.db'}")

# CORS — wildcard in dev; set CORS_ORIGINS=https://app.example.com in production
CORS_ORIGINS: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()] or ["*"]

# Logging — INFO default; set LOG_LEVEL=DEBUG or VERBOSE=1 for verbose
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if os.getenv("VERBOSE", "").strip().lower() in ("1", "true", "yes"):
    LOG_LEVEL = "DEBUG"

# OpenRouter (OpenAI-compatible API) — used for all AI features
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "google/gemini-2.0-flash-001")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Legacy OpenAI support (falls back to OpenRouter if not set)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") or OPENROUTER_API_KEY
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "") or AI_MODEL

# Ollama (local) — used for embeddings only
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# HuggingFace Inference API — cloud fallback for embeddings when Ollama isn't running
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_EMBED_MODEL = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Four-tier LLM models (via OpenRouter)
AI_MODEL_BULK = os.getenv("AI_MODEL_BULK", "google/gemini-2.5-flash")
AI_MODEL_ANALYSIS = os.getenv("AI_MODEL_ANALYSIS", "") or AI_MODEL
AI_MODEL_PREMIUM = os.getenv("AI_MODEL_PREMIUM", "anthropic/claude-4.6-opus-20260205")

# Scheduler — UTC hour to run daily collection (default 7am UTC)
COLLECT_SCHEDULE_HOUR = int(os.getenv("COLLECT_SCHEDULE_HOUR", "7"))

SEC_EDGAR_USER_AGENT = os.getenv(
    "SEC_EDGAR_USER_AGENT",
    "GTMSignalIntel research@example.com",
)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

NEWS_RSS_FEEDS = [
    "https://www.datacenterdynamics.com/en/rss/",
    "https://www.datacenterknowledge.com/rss.xml",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
]

GOOGLE_NEWS_BASE = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

SIGNAL_TYPES = [
    "fundraising",
    "funding_completed",
    "hiring",
    "ai_initiative",
    "cloud_spend",
    "outgrowing",
    "other",
]

# Human-readable labels and descriptions for README scoring table (used by scripts/update_readme.py)
SIGNAL_LABELS = {
    "fundraising": "Active Fundraising",
    "funding_completed": "Completed Funding",
    "hiring": "Infrastructure Hiring",
    "ai_initiative": "AI Initiatives",
    "cloud_spend": "Cloud Spend",
    "outgrowing": "Outgrowing Provider",
}
SIGNAL_DESCRIPTIONS = {
    "fundraising": "Currently raising — timing signal for outreach",
    "funding_completed": "Recently closed a round — capacity signal",
    "hiring": "GPU/ML/infra job postings — strongest demand signal",
    "ai_initiative": "Model training, AI product launches",
    "cloud_spend": "High cloud bills, cost optimization signals",
    "outgrowing": "Capacity complaints, provider switching",
}

COMPETITOR_EVENT_TYPES = [
    "deal",
    "expansion",
    "pricing",
    "talent",
]

COMPANY_TYPES = ["prospect", "competitor"]

SOURCE_CONFIDENCE = {
    "sec_filing": 1.0,
    "major_news": 0.85,
    "industry_news": 0.7,
    "blog": 0.5,
    "social_media": 0.35,
    "rumor": 0.2,
}

try:
    from private.provider_config import (
        PROVIDER_PROFILE,
        COMPETITOR_SEGMENTS,
        SEGMENT_PROFILES,
        PRODUCT_FIT_TO_SEGMENTS,
    )
except ImportError:
    # Sample profile. Not a real company. All numbers are round, illustrative
    # values chosen to sit mid-pack against the seeded competitors so threat
    # levels and positioning stay meaningful. Replace by adding
    # private/provider_config.py (gitignored) with the same four names.
    PROVIDER_PROFILE = {
        "name": "Sample AI Cloud Provider",
        "short_name": "Sample Provider",
        "industry": "AI Infrastructure / Data Center",
        "capacity_mw": 1000,
        "gpu_count": 20000,
        "is_public": False,
        "ticker": "",
        "exchange": "",
        "hq_location": "Ashburn, VA",
        "website": "",
        "home_markets": ["Northern Virginia"],
        "key_customers": [],
        "known_pricing": (
            "GPU cloud from $2.00/GPU-hr (H100), "
            "colocation from $140/kW/month, build-to-suit negotiated per campus."
        ),
        "products": {
            "ai_cloud": "GPU-as-a-service for AI training and inference (InfiniBand fabric, NVIDIA H100 through B200)",
            "colocation": "High-density colocation with air and direct-to-chip liquid cooling (up to 150 kW/rack)",
            "build_to_suit": "Dedicated campus builds on owned land with secured grid power",
        },
        "gpu_models": ["H100", "H200", "B200"],
        "locations": [
            "Northern Virginia (400 MW)",
            "West Texas (600 MW, under construction)",
        ],
        "cooling": ["air", "liquid (direct-to-chip)"],
        "strengths": [
            "1 GW of secured grid-connected power",
            "Low delivered power cost from renewable-matched supply",
            "Vertically integrated: land, power, facilities, and GPUs",
            "Speed to deploy: campus energization in under 18 months",
        ],
        "weaknesses": [
            "Smaller operating footprint than the largest data center REITs",
            "Revenue concentrated in a small number of anchor customers",
            "Execution risk on a multi-site construction pipeline",
        ],
        "expansion_plans": (
            "Second campus energizing next year; "
            "targeting 60K GPUs deployed within 24 months."
        ),
    }
    COMPETITOR_SEGMENTS: dict[str, str] = {
        "GPU Cloud": "Neocloud",
        "Neocloud": "Neocloud",
        "AI Cloud": "Neocloud",
        "Hyperscaler": "Hyperscaler",
        "REIT": "DC REIT",
        "Energy": "Power-First",
        "Power": "Power-First",
        "Conglomerate": "International",
        "Mining": "Miner-to-HPC",
        "HPC": "Miner-to-HPC",
    }
    SEGMENT_PROFILES: dict[str, dict[str, str]] = {
        "Neocloud": {
            "description": "GPU cloud providers selling compute-as-a-service to AI labs and enterprises",
            "positioning": "The provider supplies the infrastructure neoclouds run on; they are both customers and competitors",
            "key_battleground": "GPU availability, NVIDIA allocation, pricing per GPU-hour, speed to deploy",
        },
        "Hyperscaler": {
            "description": "Mega-scale cloud platforms (AWS, GCP, Azure) with their own silicon and massive capex",
            "positioning": "The provider builds overflow capacity when hyperscaler demand exceeds their own data center pipeline",
            "key_battleground": "Scale (GW-level power), speed to deployment, location near grid capacity",
        },
        "DC REIT": {
            "description": "Data center REITs with large portfolios of colocation and wholesale facilities",
            "positioning": "The provider differentiates on AI-ready high-density design and delivered power cost",
            "key_battleground": "Power density (kW/rack), campus scale, PUE, contract flexibility",
        },
        "Power-First": {
            "description": "Energy-native data center developers building on cheap or renewable power",
            "positioning": "Direct competitors running the same energy-first playbook",
            "key_battleground": "Power cost ($/kWh), MW pipeline, construction speed, energy source",
        },
        "International": {
            "description": "Global conglomerates and international players entering the AI data center market",
            "positioning": "The provider competes on proximity to US demand centers and operating track record",
            "key_battleground": "Geography, regulatory approval, subsea connectivity, talent access",
        },
        "Miner-to-HPC": {
            "description": "Bitcoin miners pivoting to AI/HPC data centers on their existing power assets",
            "positioning": "Peers with a similar power-first cost structure; the provider differentiates on execution track record and customer quality",
            "key_battleground": "Pivot execution speed, HPC customer contracts, power cost, GPU deployment timeline",
        },
    }
    PRODUCT_FIT_TO_SEGMENTS: dict[str, list[str]] = {
        "ai_cloud": ["Neocloud", "Hyperscaler", "Miner-to-HPC"],
        "colocation": ["DC REIT", "Power-First"],
        "build_to_suit": ["Power-First", "DC REIT", "Miner-to-HPC"],
    }

COMPETITOR_SEGMENT_DEFAULT = "Data Center"

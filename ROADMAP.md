# Product Roadmap - Investment Portfolio Analyzer

> **Last Updated:** March 29, 2026
>
> This document tracks feature ideas, planned enhancements, and the product vision.

---

## How This Roadmap Works

| Status | Meaning |
|--------|---------|
| **Backlog** | Ideas we want to build someday |
| **Planned** | Committed for upcoming development |
| **In Progress** | Currently being worked on |
| **Completed** | Done and shipped |

---

## Current Sprint

### In Progress
*None currently*

### Just Completed
- [x] Simplified Asset Allocation Display (Stocks, Bonds, REITs, Alternatives, Commodities, Other)
- [x] Modern UI Redesign (CSS design system, dashboard cards, insight cards)
- [x] Fixed JPMC Empower PDF multi-line fund name parsing

### Completed Previously
- [x] Multi-file upload (accumulate files instead of replacing)
- [x] Account selection/exclusion page
- [x] Fixed diversification score decimals
- [x] Fixed tax efficiency score decimals
- [x] Improved text wrapping/overflow handling
- [x] Titan PDF Statement Parser
- [x] Acorns PDF Statement Parser
- [x] Arta Finance PDF Statement Parser
- [x] Duplicate ticker consolidation in Top 10 Holdings
- [x] Empower 401k PDF Statement Parser (auto-detection + parsing)
- [x] Per-Source Breakdown in Analysis (pie chart + source badges on accounts)
- [x] Sector Allocation Details (pie chart showing holdings by sector with legend)
- [x] Ticker Descriptions & Links (full names, descriptions, Yahoo Finance links)
- [x] Target Date Fund Year Extraction (uses full fund name from PDF to show year, e.g., "Target Date 2045 Fund")
- [x] AI-Powered Insights (GPT-4o chat widget with portfolio context, persistent history)

---

## Backlog

### High Priority

#### AI Advisor Semantic Layer
**Why:** Transform raw portfolio data into meaningful, contextualized knowledge for better AI recommendations
**Effort:** High
**Status:** Planned

**The Problem:**
Currently, the AI advisor receives raw portfolio data as a text dump in the system prompt. This approach:
- Lacks relationship context (e.g., VTI and VOO have 100% overlap)
- Missing fund knowledge (what is VTI? what sectors does it cover?)
- No benchmark comparisons (am I underweight international?)
- No pre-computed insights (just raw numbers)

**What is a Semantic Layer?**
A semantic layer is a **translation/enrichment layer** that transforms raw data into meaningful context:

```
Raw Data → Semantic Layer → Enriched Context → AI Advisor → Better Recommendations
```

**It is NOT:**
- Investment philosophy (that's separate configuration)
- The AI itself (it feeds the AI)
- Just a database (it's active intelligence)

**Semantic Layer Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      SEMANTIC LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ 1. FUND         │    │ 2. RELATIONSHIP │                     │
│  │    KNOWLEDGE    │    │    ENGINE       │                     │
│  │    BASE         │    │                 │                     │
│  │                 │    │ - Overlap       │                     │
│  │ - Descriptions  │    │   detection     │                     │
│  │ - Asset classes │    │ - Correlations  │                     │
│  │ - Sectors       │    │ - Substitutes   │                     │
│  │ - Expense ratios│    │                 │                     │
│  └────────┬────────┘    └────────┬────────┘                     │
│           │                      │                               │
│           ▼                      ▼                               │
│  ┌─────────────────────────────────────────┐                    │
│  │         3. BENCHMARK COMPARISONS         │                    │
│  │                                          │                    │
│  │  - Target allocations (60/40, age-based) │                    │
│  │  - "You're 15% underweight international"│                    │
│  │  - Missing asset classes/sectors         │                    │
│  └────────────────────┬────────────────────┘                    │
│                       │                                          │
│                       ▼                                          │
│  ┌─────────────────────────────────────────┐                    │
│  │       4. PRE-COMPUTED INSIGHTS           │                    │
│  │                                          │                    │
│  │  - Concentration warnings WITH context   │                    │
│  │  - Rebalancing suggestions WITH reasons  │                    │
│  │  - Tax optimization opportunities        │                    │
│  │  - Overlap warnings                      │                    │
│  └────────────────────┬────────────────────┘                    │
│                       │                                          │
│                       ▼                                          │
│  ┌─────────────────────────────────────────┐                    │
│  │       5. TEMPORAL CONTEXT (History)      │                    │
│  │                                          │                    │
│  │  - "NVDA grew from 3% to 8% in 6 months"│                    │
│  │  - Previous recommendations & outcomes   │                    │
│  │  - Trend analysis                        │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AI ADVISOR    │
                    │   (Claude)      │
                    │                 │
                    │ Receives rich,  │
                    │ contextualized  │
                    │ knowledge       │
                    └─────────────────┘
```

**Component Details:**

**1. Fund Knowledge Base**
| Data | Source | Example |
|------|--------|---------|
| Fund Description | Static DB + APIs | "VTI: Vanguard Total Stock Market ETF, holds 4000+ US stocks" |
| Asset Class | Mapping table | "VTI → US Equity, BND → Fixed Income" |
| Sector Breakdown | Fund data | "VTI: 28% Tech, 13% Healthcare, 12% Financials" |
| Expense Ratio | Fund data | "VTI: 0.03%, ARKK: 0.75%" |
| Dividend Yield | API/static | "VTI: 1.5%, SCHD: 3.4%" |
| Fund Family | Static | "VTI → Vanguard, SPY → State Street" |

**2. Relationship Engine**
| Relationship | Detection Method | Example Output |
|--------------|------------------|----------------|
| Overlap | Compare underlying holdings | "VTI contains all VOO holdings (100% overlap)" |
| Correlation | Historical price data | "NVDA and AMD are highly correlated (0.85)" |
| Substitutes | Same category + low cost | "Consider VTI (0.03%) instead of SWTSX (0.03%)" |
| Tax Lot Pairs | Same security, different lots | "Harvest ARKK loss, keep ARKG for exposure" |

**3. Benchmark Comparisons**
| Benchmark Type | Implementation | Example Output |
|----------------|----------------|----------------|
| Age-Based Target | `100 - age` stocks | "At 35, target ~65% stocks. You have 80%." |
| 60/40 Portfolio | Fixed comparison | "Typical 60/40: 60% stocks, 40% bonds. You: 85/5" |
| Sector Weights | S&P 500 sector weights | "Tech is 28% of S&P. You have 45% (overweight)" |
| Missing Classes | Check presence | "You have no REIT exposure (typical: 5-10%)" |

**4. Pre-Computed Insights**
| Insight Type | Current | With Semantic Layer |
|--------------|---------|---------------------|
| Concentration | "NVDA is 35%" | "NVDA is 35% (HIGH). Single stock >10% is risky. Consider trimming $8K to reach 25%." |
| Diversification | "Score: 72" | "Score: 72. Strong US equity coverage via VTI. Gap: No international (target: 20-30%)." |
| Tax Efficiency | "Score: 85" | "Score: 85. Opportunity: Harvest $2K ARKK loss to offset AAPL gains. Net tax savings: ~$500." |

**5. Temporal Context**
| Context Type | Data Source | Example Output |
|--------------|-------------|----------------|
| Position Drift | Historical snapshots | "NVDA grew from 8% to 35% over 12 months" |
| Recommendation Tracking | Chat history + outcomes | "Last month suggested trimming TSLA. Still relevant." |
| Performance Trends | Snapshot comparisons | "Portfolio +12% YTD vs S&P +8%" |

**Implementation Plan:**

**Phase 1: Fund Knowledge Base (Week 1-2)**
- Create `src/services/semantic/fund_knowledge.py`
- Build static database of 500+ common tickers
- Include: description, asset class, sector, expense ratio
- API integration for unknown tickers (Yahoo Finance)

**Phase 2: Relationship Engine (Week 3)**
- Create `src/services/semantic/relationships.py`
- Implement overlap detection using ETF holdings data
- Build fund similarity/substitute recommendations
- Identify correlated positions

**Phase 3: Benchmark Comparisons (Week 4)**
- Create `src/services/semantic/benchmarks.py`
- Implement target allocation models (age-based, 60/40, etc.)
- Calculate deviation from targets
- Identify missing asset classes

**Phase 4: Pre-Computed Insights (Week 5)**
- Create `src/services/semantic/insights.py`
- Enhance existing concentration/diversification analysis
- Add contextual explanations
- Generate actionable recommendations

**Phase 5: Integration & Temporal Context (Week 6)**
- Create `src/services/semantic/context_builder.py`
- Integrate with historical snapshots
- Update AI advisor to use semantic context
- Add recommendation tracking

**Files to Create:**
```
src/services/semantic/
├── __init__.py
├── fund_knowledge.py      # Fund descriptions, asset classes, sectors
├── relationships.py       # Overlap detection, correlations
├── benchmarks.py          # Target allocations, comparisons
├── insights.py            # Pre-computed contextual insights
├── context_builder.py     # Assembles full semantic context
└── data/
    ├── fund_database.json # Static fund data (500+ tickers)
    ├── sector_weights.json # S&P 500 sector weights
    └── overlap_matrix.json # Common ETF overlaps
```

**Files to Modify:**
- `src/services/ai_advisor.py` - Use SemanticContextBuilder instead of raw data
- `src/web/app.py` - Pass semantic context to advisor

**Example Output (Before vs After):**

**Before (Raw Data):**
```
TOP 10 HOLDINGS:
- VTI: $50,000 (25%)
- VOO: $30,000 (15%)
- NVDA: $70,000 (35%)
```

**After (Semantic Context):**
```
PORTFOLIO INTELLIGENCE:

OVERLAP WARNING:
VTI (Total US Market) and VOO (S&P 500) have 85% overlap.
Combined exposure: $80,000 (40%) in essentially the same stocks.
Consider: Keep VTI only, redeploy $30K from VOO to VXUS (international).

CONCENTRATION ALERT:
NVDA at 35% is HIGH RISK (single stock >10% threshold).
- Has grown from 8% to 35% over past year (drift)
- Sector: Technology (you're already 45% tech overall)
- Action: Consider trimming $20K to reach 25% allocation

MISSING ASSET CLASSES:
- International Equities: 0% (target: 20-30%)
- REITs: 0% (target: 5-10%)
- Bonds: 5% (target for age 35: ~35%)

BENCHMARK COMPARISON:
Your allocation: 95% stocks, 5% bonds
Age-based target: 65% stocks, 35% bonds
Action: Consider adding BND or BNDX for bond exposure
```

**Success Metrics:**
- AI recommendations reference specific fund characteristics
- Overlap warnings catch redundant holdings
- Recommendations include dollar amounts based on analysis
- User feedback: "Recommendations feel more personalized"

**Resources & Learning:**
- [Building Semantic Layers for Analytics](https://www.getdbt.com/blog/semantic-layer)
- [ETF Overlap Tools](https://www.etfrc.com/funds/overlap.php) - for overlap logic
- [Morningstar Categories](https://www.morningstar.com/investing-definitions/morningstar-category) - for classification

---

#### Investment Philosophy Configuration (Separate from Semantic Layer)
**Why:** Allow users to customize AI recommendations based on their investment style
**Effort:** Medium
**Status:** Future (after Semantic Layer)

**Note:** This is DIFFERENT from the semantic layer. The semantic layer provides knowledge/context. Investment philosophy provides preferences/constraints.

**Example Philosophies:**
```python
PHILOSOPHIES = {
    "passive_index": {
        "prefer": ["VTI", "VXUS", "BND"],
        "avoid": ["individual stocks", "active funds"],
        "max_expense_ratio": 0.10,
        "rebalance_threshold": 5  # % drift before rebalancing
    },
    "dividend_growth": {
        "prefer": ["SCHD", "VIG", "dividend aristocrats"],
        "min_yield": 2.0,
        "focus": "growing dividend income"
    },
    "aggressive_growth": {
        "prefer": ["QQQ", "VGT", "growth stocks"],
        "risk_tolerance": "high",
        "time_horizon": "10+ years"
    }
}
```

---

#### Target Date Fund / Investment Fund Profile Ingestion
**Why:** 401k statements show target date funds as single holdings, but they contain multiple underlying investments (stocks, bonds, international). Without fund profiles, diversification and sector analysis is inaccurate.
**Effort:** Medium-High
**Details:**

**The Problem:**
- Target Date 2045 Fund shows as 1 holding worth $92,000
- But internally it's: 54% US Stocks, 36% International, 10% Bonds
- Current analyzer can't "look through" to see true allocation
- Diversification score is misleading (shows concentrated in 1 fund)

**Solution - Fund Profile Ingestion with Persistent Storage:**

1. **One-Time Upload** - User uploads "Investment Fund Profiles" PDF once
2. **Parse & Store** - Extract fund composition and save to local database
3. **Auto-Match** - When statements are uploaded, automatically match holdings to stored fund profiles
4. **Look-Through Analysis** - Calculate true portfolio allocation using stored profiles

**Key Design: Upload Once, Reuse Forever**
```
First Upload:
  User uploads Fund Profile PDF → Parse → Store in SQLite DB

Subsequent Uploads:
  User uploads 401k Statement → Match "Target Date 2045 Fund" →
  Lookup stored profile → Apply look-through analysis
```

**Data Model - Fund Profile Storage:**
| Field | Example |
|-------|---------|
| fund_name | Target Date 2045 Fund |
| source | JPMC Empower |
| asset_allocation | {"us_stocks": 54, "intl_stocks": 36, "bonds": 10} |
| sector_breakdown | {"tech": 25, "healthcare": 15, ...} |
| top_holdings | [{"ticker": "AAPL", "percent": 3}, ...] |
| expense_ratio | 0.12 |
| last_updated | 2025-03-15 |

**Matching Logic:**
- Match by exact fund name
- Match by fund name + source (JPMC, Wells Fargo, etc.)
- Fuzzy match for slight name variations
- Prompt user to confirm if uncertain

**Implementation Steps:**
1. Create `fund_profiles` SQLite table
2. Build fund profile PDF parser
3. Add "Manage Fund Profiles" UI section
4. Modify analyzer for look-through calculations
5. Add profile matching logic when processing statements
6. Update results UI with "Simple" vs "Look-Through" toggle

**Files to Create/Modify:**
- `src/models/fund_profile.py` (new - SQLAlchemy model)
- `src/utils/fund_profile_parser.py` (new - PDF parser)
- `src/services/fund_matcher.py` (new - matching logic)
- `src/portfolio_analyzer/analyzer.py` (modify for look-through)
- `src/web/app.py` (add fund profile management routes)
- `src/web/templates/fund_profiles.html` (new - management UI)
- `src/web/templates/results.html` (add view toggle)

---

#### YTD Performance Tracking
**Why:** Statements don't show year-to-date performance - users want to see how their investments performed this year
**Effort:** Medium
**Details:**
- Fetch YTD performance data from external source (Yahoo Finance API, Alpha Vantage, etc.)
- Show YTD % gain/loss for each holding
- Show overall portfolio YTD performance
- Color code: green for gains, red for losses
- Option to compare against benchmarks (S&P 500 YTD, etc.)

**Input Options:**
- Automatic: Pull from Yahoo Finance API using ticker symbols
- Manual: Allow user to input YTD % if they have it from another source
- Hybrid: Auto-fetch with manual override capability

---

#### Migrate AI Advisor from OpenAI to Anthropic API
**Why:** Switch from GPT-4o to Claude for the AI Investment Advisor
**Effort:** Low (2-3 hours)
**Details:**

**Current Implementation:**
- `src/services/ai_advisor.py` - AIAdvisor class using OpenAI SDK
- `src/web/app.py` - Chat endpoints calling AIAdvisor
- Environment variable: `OPENAI_API_KEY`

**Changes Required:**
1. Install Anthropic SDK: `pip install anthropic`
2. Update `ai_advisor.py`:
   - Replace `from openai import OpenAI` with `from anthropic import Anthropic`
   - Change client initialization: `Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))`
   - Update API call from `client.chat.completions.create()` to `client.messages.create()`
   - Adjust message format (Anthropic uses `system` parameter separately)
   - Update model from `gpt-4o` to `claude-sonnet-4-20250514` or `claude-3-5-sonnet`
3. Update `.env` file: Replace `OPENAI_API_KEY` with `ANTHROPIC_API_KEY`
4. Update `requirements.txt`: Add `anthropic>=0.18.0`
5. Update error messages referencing "OpenAI"

**API Differences:**
| OpenAI | Anthropic |
|--------|-----------|
| `client.chat.completions.create()` | `client.messages.create()` |
| `messages=[{role, content}]` | `system="...", messages=[{role, content}]` |
| `response.choices[0].message.content` | `response.content[0].text` |
| `max_tokens=1000` | `max_tokens=1024` |
| `gpt-4o` | `claude-sonnet-4-20250514` |

**Files to Modify:**
- `src/services/ai_advisor.py` (main changes)
- `src/models/chat.py` (update docstring only)
- `requirements.txt`
- `.env.example`

---

**Why:** Tax analyzer for investment accounts  
**Effort:** Medium
**Details:**
- Need to understand the income, interest and dividends from investment account statement
- Once the user uploads the year end statement document i need to extract the required details
- The primary persona is a Retail investor

**Why:** Make the UI more intuitive and user friendly 
**Effort:** Medium
**Details:**
- Levearge V0 designs for the approach
- Leverage Claude to implement the design patterns
- The primary persona is a Retail investor

**Why:** Alerting about fees on accounts
**Effort:** Medium
**Details:**
- Scan through statements
- Identify periodic fees and then summarize to the user
- Understand if the fee is monthly or annually

**Why:** Tax loss harvesting alerts
**Effort:** Medium
**Details:**
- Identify tax loss harvesting items in statements
- Let the users know about potential opportunities
- Provide them a clear explanation  of the opportunity

**Why:** Investment ideas recommendor
**Effort:** Medium
**Details:**
- Let the user use the AI chatbot for specific ideas and thematic recommendation
- We should provide a specific thematic recommendations in the chat bot
- Once the user selects an option we should give them the opportunity to review and save the idea

---

#### AI-Generated Market & Portfolio Recap
**Why:** Users want periodic context on how market conditions affect their specific portfolio
**Effort:** Medium-High
**Details:**

**The Problem:**
- Users see their portfolio numbers but lack context
- They don't know how macro events (Fed rates, inflation, earnings) impact their specific holdings
- No personalized market intelligence based on what they actually own

**Solution - Personalized AI Market Recap:**

Generate a weekly/monthly AI-powered recap that connects market events to the user's specific portfolio.

**Recap Sections:**
1. **Portfolio Performance Summary**
   - "Your portfolio moved +2.3% this week ($4,500)"
   - Compare to benchmarks (S&P 500, sector indices)

2. **Sector Impact Analysis**
   - "Your 45% Technology allocation was affected by..."
   - "Healthcare (12% of portfolio) outperformed due to..."

3. **Macro & Monetary Context**
   - Fed rate decisions and impact on bonds/growth stocks
   - Inflation trends and portfolio positioning
   - Economic indicators (jobs, GDP, etc.)

4. **Holdings Spotlight**
   - Notable moves in top holdings
   - Earnings reports from companies you own
   - News affecting your specific positions

5. **Forward Outlook**
   - Upcoming events to watch (Fed meetings, earnings, etc.)
   - Sector rotation trends
   - Risk factors for your allocation

**Data Sources:**
- User's latest snapshot (holdings, allocation, values)
- Web search for current market data (via AI web search capability)
- Financial news APIs (optional enhancement)

**Implementation Approach:**
1. **Trigger Options:**
   - Manual: "Generate Market Recap" button on dashboard
   - Scheduled: Weekly email digest (requires email setup)
   - On-demand: Chat command "Give me a market recap"

2. **AI Prompt Engineering:**
   - Pass portfolio holdings and allocation to LLM
   - Include web search results for recent market news
   - Generate personalized narrative connecting macro to micro

**Example Output:**
```
📊 WEEKLY PORTFOLIO RECAP - March 10-17, 2025

YOUR PORTFOLIO: +$3,245 (+1.8%)
vs S&P 500: +1.2% | vs NASDAQ: +2.1%

🏭 SECTOR IMPACT:
• Technology (47% of portfolio): +2.4%
  - Your NVDA position (+4.2%) benefited from AI chip demand
  - VGT tracking sector momentum

• Fixed Income (0%): N/A
  - Consider: 10Y Treasury at 4.2%, attractive entry point

📈 MACRO CONTEXT:
• Fed held rates steady, signaling patience on cuts
• Your growth-heavy allocation benefits from this stance
• Inflation at 2.8% - watch for Q2 data

⚠️ WATCH THIS WEEK:
• NVDA earnings Thursday - you have $23K exposure
• Fed minutes Wednesday - bond market volatility expected

💡 POSITIONING THOUGHTS:
Your 47% tech concentration performed well but remains
a risk factor. Consider trimming if NVDA approaches $950.
```

**Files to Create/Modify:**
- `src/services/market_recap.py` (new - recap generation logic)
- `src/web/app.py` (add recap API endpoint)
- `src/web/templates/results.html` (add "Generate Recap" button)
- `src/web/templates/recap.html` (new - formatted recap display)

**Future Enhancements:**
- Email digest subscription
- Historical recap archive
- Custom frequency (daily/weekly/monthly)
- Sector-specific deep dives


#### Proactive Tax Intelligence Engine
**Why:** Every app files or tracks taxes backward. None tells you in August "sell this loser to offset your gains before Dec 31" or "move this to your Roth now." TurboTax is backward-looking; brokers don't do tax planning. This gap costs investors thousands per year.
**Effort:** High
**Status:** Backlog

**The Problem:**
- Tax software (TurboTax, H&R Block) only works AFTER the year ends
- Brokers show gains/losses but don't advise on timing or strategy
- Investors miss tax-loss harvesting windows, Roth conversion opportunities, and optimal timing
- Result: Overpaying taxes by $1K-$10K+ annually

**Solution - Year-Round Proactive Tax Intelligence:**

A monitoring system that analyzes your portfolio throughout the year and sends actionable, time-sensitive tax alerts.

**Key Features:**

**1. Tax-Loss Harvesting Alerts (Year-Round)**
| Scenario | Alert Example |
|----------|---------------|
| Significant unrealized loss | "ARKK is down $3,200. Harvest this loss to offset your $4,500 AAPL gain. Net tax savings: ~$800" |
| Market dip opportunity | "Market dropped 5% today. Your VTI position has a $2,100 harvestable loss. Act within 30 days to avoid wash sale." |
| Year-end deadline | "⚠️ 15 days until Dec 31. You have $5,400 in unrealized losses to harvest." |

**2. Gain Deferral Strategies**
| Scenario | Alert Example |
|----------|---------------|
| Short-term → Long-term | "NVDA position turns long-term in 45 days. Waiting saves ~$1,200 in taxes (23% → 15% rate)." |
| Bunching gains | "You've realized $8K in gains this year. Consider deferring the GOOGL sale to next year to stay in 0% LTCG bracket." |

**3. Roth Conversion Opportunities**
| Scenario | Alert Example |
|----------|---------------|
| Low income year | "Your projected income is $45K this year. Consider converting $15K from Traditional to Roth (12% bracket) before Dec 31." |
| Market dip | "Market is down 15%. Converting $20K now means paying taxes on depressed values - same shares, less tax." |
| Bracket space | "You have $8,500 of room in the 22% bracket. Fill it with a Roth conversion before year-end?" |

**4. Asset Location Optimization**
| Scenario | Alert Example |
|----------|---------------|
| Tax-inefficient in taxable | "Your SCHD (3.4% yield) is in your taxable account. Move to IRA to save ~$400/year in dividend taxes." |
| Growth in Roth | "Consider holding QQQ in your Roth IRA - maximum growth, zero taxes ever." |

**5. Estimated Tax Payment Reminders**
| Scenario | Alert Example |
|----------|---------------|
| Q4 payment due | "You've realized $12K in gains. Estimated Q4 payment of ~$1,800 due Jan 15 to avoid penalties." |
| Withholding check | "Year-end projection: You may owe $3,200. Increase W-4 withholding or make estimated payment." |

**Implementation Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                   TAX INTELLIGENCE ENGINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ 1. PORTFOLIO    │    │ 2. TAX PROFILE  │                     │
│  │    MONITOR      │    │                 │                     │
│  │                 │    │ - Filing status │                     │
│  │ - Track lots    │    │ - Tax bracket   │                     │
│  │ - Monitor G/L   │    │ - State taxes   │                     │
│  │ - Watch dates   │    │ - Deductions    │                     │
│  └────────┬────────┘    └────────┬────────┘                     │
│           │                      │                               │
│           ▼                      ▼                               │
│  ┌─────────────────────────────────────────┐                    │
│  │         3. OPPORTUNITY DETECTOR          │                    │
│  │                                          │                    │
│  │  - Loss harvesting candidates            │                    │
│  │  - Short→Long term transitions           │                    │
│  │  - Roth conversion windows               │                    │
│  │  - Asset location mismatches             │                    │
│  └────────────────────┬────────────────────┘                    │
│                       │                                          │
│                       ▼                                          │
│  ┌─────────────────────────────────────────┐                    │
│  │       4. ALERT GENERATOR                 │                    │
│  │                                          │                    │
│  │  - Calculate dollar impact               │                    │
│  │  - Prioritize by savings potential       │                    │
│  │  - Generate actionable recommendations   │                    │
│  │  - Track deadlines                       │                    │
│  └────────────────────┬────────────────────┘                    │
│                       │                                          │
│                       ▼                                          │
│  ┌─────────────────────────────────────────┐                    │
│  │       5. NOTIFICATION SYSTEM             │                    │
│  │                                          │                    │
│  │  - Dashboard alerts                      │                    │
│  │  - Email notifications (optional)        │                    │
│  │  - Year-end tax summary                  │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Tax Calendar Integration:**

| Date | Event | System Action |
|------|-------|---------------|
| Jan 1 | New tax year | Reset YTD tracking, review prior year missed opportunities |
| Jan 15 | Q4 estimated payment | Reminder if gains realized |
| Apr 15 | Q1 estimated payment | Reminder + tax filing deadline |
| Jun 15 | Q2 estimated payment | Reminder |
| Sep 15 | Q3 estimated payment | Reminder |
| Oct 15 | Extended filing deadline | Alert |
| Nov 1 | 60-day countdown | "Critical window for year-end tax moves" |
| Dec 1 | 30-day countdown | Urgent harvesting + conversion alerts |
| Dec 15 | Final harvesting window | Last call for trades to settle by Dec 31 |

**User Tax Profile (Input Required):**

```python
TAX_PROFILE = {
    "filing_status": "married_filing_jointly",  # or single, head_of_household
    "tax_bracket": 24,  # Federal marginal rate %
    "state": "CA",  # For state tax calculations
    "state_rate": 9.3,  # State marginal rate %
    "ltcg_rate": 15,  # Long-term capital gains rate
    "has_carryover_losses": True,
    "carryover_amount": 5000,  # From prior years
    "estimated_income": 180000,  # For bracket calculations
    "roth_eligible": True,
    "ira_contribution_room": 7000,
}
```

**Dashboard Display - Tax Intelligence Panel:**

```
┌─────────────────────────────────────────────────────────────┐
│ 🎯 TAX INTELLIGENCE                           2025 YTD     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ REALIZED THIS YEAR:                                         │
│   Short-term gains:    +$4,200   (taxed as income)         │
│   Long-term gains:     +$8,500   (15% rate)                │
│   Harvested losses:    -$2,100                             │
│   ─────────────────────────────                            │
│   Net taxable gains:   +$10,600                            │
│   Estimated tax:       ~$2,350                             │
│                                                             │
│ ⚡ OPPORTUNITIES (3 alerts)                                 │
│                                                             │
│ 🔴 HIGH PRIORITY - Act by Dec 15                           │
│    Harvest $3,200 ARKK loss → Save ~$770 in taxes          │
│    [View Details] [Dismiss]                                │
│                                                             │
│ 🟡 MEDIUM - 45 days remaining                              │
│    NVDA turns long-term on Feb 23 → Save ~$1,200 if wait   │
│    [View Details] [Dismiss]                                │
│                                                             │
│ 🟢 OPTIMIZATION                                             │
│    Move SCHD to IRA → Save ~$400/year in dividend taxes    │
│    [View Details] [Dismiss]                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Implementation Phases:**

**Phase 1: Tax Profile & Lot Tracking (Foundation)**
- Add tax profile input UI
- Parse purchase dates from statements (for holding period)
- Track realized gains/losses YTD
- Calculate short-term vs long-term status

**Phase 2: Loss Harvesting Engine**
- Identify unrealized losses
- Calculate tax savings potential
- Wash sale rule checker (31-day window)
- Generate harvesting alerts

**Phase 3: Holding Period Optimization**
- Track days until long-term status
- Alert when approaching 1-year mark
- Calculate deferral savings

**Phase 4: Roth Conversion Intelligence**
- Income projection integration
- Bracket space calculator
- Conversion opportunity detector

**Phase 5: Notification System**
- Dashboard alert panel
- Email digest (optional)
- Year-end tax summary report

**Files to Create:**
```
src/services/tax/
├── __init__.py
├── tax_profile.py        # User tax settings
├── lot_tracker.py        # Purchase lots & holding periods
├── loss_harvester.py     # Loss harvesting opportunities
├── gain_optimizer.py     # Holding period & deferral
├── roth_advisor.py       # Roth conversion analysis
├── alert_generator.py    # Create actionable alerts
└── tax_calendar.py       # Deadline tracking
```

**Competitive Advantage:**
- TurboTax: Only looks backward at filed returns
- Brokers: Show data, don't advise on timing
- Robo-advisors: Auto-harvest but don't explain or optimize
- **This tool: Proactive, personalized, actionable tax intelligence year-round**

**Potential Tax Savings:**
| Strategy | Typical Annual Savings |
|----------|----------------------|
| Loss harvesting | $500 - $3,000 |
| Holding period optimization | $200 - $2,000 |
| Asset location | $300 - $1,500 |
| Roth conversion timing | $500 - $5,000 |
| **Total potential** | **$1,500 - $11,500/year** |

---

### Medium Priority

#### 4. Rebalancing Recommendations
**Why:** Tell users exactly what to buy/sell to reach target allocation
**Effort:** Medium
**Details:**
- User sets target allocation (e.g., 60% stocks, 40% bonds)
- System calculates current vs target
- Outputs specific trades: "Sell $5K of VTI, Buy $5K of BND"

#### 6. Export to PDF Report
**Why:** Users want to save/share their analysis
**Effort:** Medium
**Details:**
- Generate downloadable PDF
- Include all charts and tables
- Professional formatting

#### 7. Schwab CSV Support
**Why:** Charles Schwab is a major brokerage
**Effort:** Low
**Details:**
- Analyze Schwab export format
- Add parser
- Test with sample data

#### 8. Vanguard CSV/PDF Support
**Why:** Vanguard is popular for index fund investors
**Effort:** Low-Medium
**Details:**
- Support Vanguard brokerage exports
- Handle their unique format

---

### Low Priority / Future Ideas

#### 9. User Accounts & Cloud Storage
**Why:** Access portfolio from any device
**Effort:** High
**Details:**
- User registration/login
- Store portfolios in cloud database
- Privacy considerations important

#### 10. Mobile App
**Why:** Check portfolio on the go
**Effort:** Very High
**Details:**
- React Native or Flutter app
- Sync with web version
- Push notifications for alerts

#### 11. Benchmark Comparison
**Why:** Compare portfolio performance to S&P 500, etc.
**Effort:** Medium
**Details:**
- Fetch benchmark data (API needed)
- Calculate relative performance
- Show "You beat the market by X%"

#### 12. Dividend Tracking
**Why:** Income investors want to see dividend yield and history
**Effort:** Medium
**Details:**
- Calculate portfolio dividend yield
- Show dividend calendar
- Project annual dividend income

#### 13. Risk Analysis (Beta, Volatility)
**Why:** Advanced users want risk metrics
**Effort:** Medium-High
**Details:**
- Calculate portfolio beta
- Show volatility metrics
- Value at Risk (VaR) calculation

---

## Completed Features

### v1.0 - Initial Release
- [x] CSV upload (Fidelity format)
- [x] PDF upload (Betterment format)
- [x] Portfolio summary (value, cost basis, returns)
- [x] Asset allocation breakdown
- [x] Top 10 holdings display
- [x] Diversification score
- [x] Concentration risk analysis
- [x] Tax-loss harvesting opportunities
- [x] Web-based UI

### v1.1 - Multi-Portfolio Support (Current)
- [x] Upload multiple files at once
- [x] Account selection/exclusion
- [x] Combined portfolio analysis
- [x] Improved text wrapping/overflow handling
- [x] Titan PDF Statement Parser (auto-detection + parsing)
- [x] Acorns PDF Statement Parser (auto-detection + parsing)
- [x] Arta Finance PDF Statement Parser (auto-detection + parsing)
- [x] Empower 401k PDF Statement Parser (auto-detection + parsing, tax_deferred)
- [x] Duplicate ticker consolidation in Top 10 Holdings
- [x] Per-Source Breakdown in Analysis (pie chart showing allocation by brokerage)
- [x] Source badges on accounts (Fidelity, Betterment, Titan, Empower, etc.)
- [x] Sector Allocation Details (pie chart showing holdings by sector with legend)
- [x] Ticker Descriptions & Links (full names, descriptions, Yahoo Finance links for 100+ tickers)
- [x] Historical Tracking (SQLite database, save/view/compare snapshots, Chart.js value chart)
- [x] AI-Powered Insights (GPT-4o floating chat widget, portfolio context, persistent chat history)
- [x] Specific Investment Recommendations (actionable buy/sell with dollar amounts, rebalancing calculator)

### v1.2 - UI Redesign (March 2025)
- [x] Modern CSS Design System (CSS variables, Inter font, design tokens)
- [x] Upload Page Redesign (hero section, drag & drop zone, brokerage cards)
- [x] Results Page Dashboard (portfolio value card, analysis scores card)
- [x] Key Insights Section (colored insight cards: positive/warning/attention)
- [x] Improved Charts (doughnut charts for brokerage & sector allocation)
- [x] Fixed JPMC Empower multi-line fund name parsing
- [x] Added DEFECTS.md for bug tracking

---

## Technical Debt

Items that need cleanup but aren't features:

- [ ] Add unit tests for parsers
- [ ] Add integration tests for web routes
- [ ] Improve error handling for malformed files
- [ ] Add logging for debugging
- [ ] Clean up background shell processes
- [ ] Add proper session management (currently using query params)

---

## How to Add a Feature Request

1. Add it to the **Backlog** section above
2. Include: **Why** (user benefit), **Effort** estimate, **Details**
3. When ready to build, move to **Planned** or **In Progress**
4. When done, move to **Completed Features**

---

## Notes & Ideas Parking Lot

*Random ideas that need more thought:*

- Integration with Plaid for automatic account sync?
- Support for crypto portfolios (Coinbase, etc.)?
- ESG scoring for socially responsible investing?
- What-if scenarios ("What if I sold X and bought Y?")
- Alerts for concentration limits exceeded?
- Family/household portfolio aggregation?

---

*This roadmap is a living document. Update it as priorities change!*

# Product Roadmap - Investment Portfolio Analyzer

> **Last Updated:** March 17, 2025
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
*No items currently in progress*

### Just Completed
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

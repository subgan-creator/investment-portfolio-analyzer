# Product Roadmap - Investment Portfolio Analyzer

> **Last Updated:** March 1, 2025
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
- [x] Specific Investment Recommendations (actionable buy/sell with dollar amounts)
- [x] Customize AI Advisor system prompt and add OpenAI API key to .env

### Completed This Session
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

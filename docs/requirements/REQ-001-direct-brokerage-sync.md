# REQ-001: Direct Brokerage Account Sync (Betterment and others)

| | |
|---|---|
| **Status** | Backlog (not scheduled) |
| **Priority** | Medium |
| **Effort** | Medium–High |
| **Created** | 2026-09-27 |
| **Depends on** | Persistent user identity and profile storage (see "Dependencies") |

---

## 1. Problem

Today every account has to be refreshed by downloading a statement (PDF/CSV) from each
platform and uploading it (`/upload` → `data_loader.py` / `pdf_parser.py`). This is manual, slow,
error-prone (per-institution parsers break when statement formats change) and means the analysis
is only as fresh as the last upload.

## 2. Goal

Let the user link an investment account once and pull current holdings automatically, starting
with Betterment, and ideally covering the other accounts already in use (Fidelity, Empower / JPMC 401k,
Titan, Acorns, Arta).

### Non-goals (for the first version)
- Placing trades or moving money (read-only only).
- Replacing statement upload. Upload stays as the fallback and as the source for tax-lot detail.
- Multi-user / household aggregation.

## 3. Research findings (Sept 2026)

- **Betterment has no public API for individual users.** Its integrations exist only for advisors on
  Betterment Advisor Solutions. Unofficial GitHub wrappers scrape the site with the user's password.
  Those are fragile and likely against Betterment's terms, so they're **rejected**.
- **Plaid Investments** supports Betterment. It's read-only and returns holdings, security metadata
  (ticker, name, type), each holding's aggregate cost basis when the institution provides it, and
  investment transactions. It also covers most other brokerages in use. **Recommended.**
- **SnapTrade:** strong for Robinhood, E*TRADE, Empower, etc., and supports trading. Betterment was
  **not** on its published integration list at the time of research.
- **Mastercard Open Finance (formerly Finicity):** connects to Betterment but is enterprise-oriented.
- **Plaid cost:** free sandbox (test data) and limited production (200 free API calls per product
  with live data), then Pay-as-you-go. Investments pricing isn't published; check it in the Plaid dashboard.

## 4. Proposed design

Plaid becomes a new **source** that produces the same `Portfolio → Account → Holding` objects the
upload parsers produce, so the analyzers, snapshots and AI advisor need no changes.

### 4.1 Configuration
- `requirements.txt`: add `plaid-python`.
- `.env` / `.env.example`: `PLAID_CLIENT_ID`, `PLAID_SECRET`, `PLAID_ENV` (`sandbox` | `production`),
  `TOKEN_ENCRYPTION_KEY`.

### 4.2 New module `src/integrations/plaid_client.py`
- `create_link_token(user_id)` calls `link/token/create` with `products=["investments"]`.
- `exchange_public_token(public_token)` calls `item/public_token/exchange` and returns `access_token`, `item_id`.
- `fetch_portfolio(access_token)` calls `investments/holdings/get` and maps the result to models (see 4.4).
- `remove_item(access_token)` calls `item/remove` (on unlink).

### 4.3 Data model: new table `linked_accounts`
| column | notes |
|---|---|
| id | PK |
| user_id | FK to the user (requires the identity work) |
| provider | `plaid` |
| institution_name | e.g. "Betterment" |
| item_id | Plaid item id |
| access_token_encrypted | **never stored or logged in plain text** |
| last_synced_at, status, error | for re-auth / error display |

### 4.4 Mapping Plaid → `Holding`
```python
resp = client.investments_holdings_get(InvestmentsHoldingsGetRequest(access_token=token))
securities = {s.security_id: s for s in resp.securities}
for h in resp.holdings:
    sec = securities[h.security_id]
    qty = h.quantity or 0
    Holding(
        ticker=sec.ticker_symbol or sec.name,
        shares=qty,
        cost_basis_per_share=(h.cost_basis / qty) if h.cost_basis and qty else h.institution_price,
        cost_basis_estimated=h.cost_basis is None,
        purchase_date=None,            # Plaid provides no tax lots / purchase dates
        current_price=h.institution_price,
        description=sec.name,
        asset_class=map_plaid_type(sec.type),   # equity / etf / mutual fund / cash / fixed income
    )
```
Accounts come from `resp.accounts` (name, subtype such as `ira`, `roth`, `401k`, `brokerage`), which
feed `determine_tax_status()`.

### 4.5 Routes (`src/web/app.py`)
- `POST /api/plaid/link_token` returns a link token to the browser.
- `POST /api/plaid/exchange` stores the encrypted access token and triggers the first sync.
- `POST /api/plaid/sync` refreshes all linked accounts and feeds the same pipeline as `/analyze`.
- `POST /api/plaid/unlink/<id>` calls `item/remove` and deletes the row.

### 4.6 UI
- "Connect an account" button next to the upload box on `index.html` (Plaid Link JS). The user signs in
  to Betterment inside Plaid's widget, so the app never sees the password.
- A "Linked accounts" list showing institution, last synced time, Refresh, Unlink and Re-authenticate.
- Source badge "Synced via Plaid" alongside the existing Fidelity/Betterment/Titan badges.

## 5. Known gaps and required code changes
1. **No tax lots:** Plaid gives one cost basis per holding, with no lots and no purchase dates.
   `Holding.purchase_date` is currently required and `is_long_term` depends on it. Make it
   `Optional[datetime]`, and have `tax_optimizer.py` and the long/short-term logic handle `None`
   (show "unknown holding period" rather than guessing).
2. **Betterment's many small positions:** Betterment splits money across many ETFs and fractional
   shares, often for tax-loss harvesting. Cost-basis completeness must be tested with a real account.
3. **Hybrid source:** allow Plaid holdings plus an uploaded statement for the same account (statement
   provides lots), with de-duplication by account and ticker.

## 6. Security and privacy
- Access tokens are long-lived credentials. Encrypt them at rest (e.g. Fernet with
  `TOKEN_ENCRYPTION_KEY`), never log them, and never send them to the browser or the AI advisor.
- Replace the hard-coded `app.secret_key` with an environment variable before going live.
- Unlink must call `item/remove` so Plaid revokes access.
- Holdings pulled from Plaid are personal financial data. Same `.gitignore` / storage rules as statements.

## 7. Dependencies
- **Persistent user identity** (see the profile-persistence work): linked accounts must belong to a
  user that survives browser restarts and redeploys. Today identity is a browser-session cookie.
- **Persistent database on Render**: SQLite on Render's default disk is wiped on redeploy. Use a Render
  persistent disk or a hosted Postgres before storing tokens there.

## 8. Acceptance criteria
- [ ] In Plaid sandbox, a user can link a test institution and see its holdings analyzed with no file upload.
- [ ] In production, a real Betterment account links and its holdings match the latest Betterment statement
      (shares and market value within rounding).
- [ ] Holdings with no cost basis are flagged `cost_basis_estimated` and shown as such in results.
- [ ] Tax features don't crash or mislabel long/short term when `purchase_date` is missing.
- [ ] Refresh pulls current holdings. Unlink revokes the token and removes stored data.
- [ ] Access tokens are encrypted in the database and absent from logs.
- [ ] Statement upload continues to work unchanged.

## 9. Open questions
- Which institutions to support in v1 beyond Betterment (Fidelity, Empower/JPMC 401k, Titan)?
- Automatic scheduled sync (daily) or manual Refresh only?
- Also pull `investments/transactions/get` for YTD performance tracking (ties into the roadmap item)?
- Monthly Plaid cost for the number of linked accounts. Is it acceptable for a personal tool?

## 10. Sources
- Betterment Plaid support: https://www.openbankingtracker.com/plaid/betterment
- Plaid Investments: https://plaid.com/products/investments/
- Plaid pricing: https://plaid.com/pricing/
- SnapTrade vs Plaid: https://dev.to/pickuma/snaptrade-vs-plaid-investments-brokerage-aggregation-apis-for-fintech-builders-27mh
- SnapTrade integrations: https://snaptrade.com/brokerage-integrations
- Betterment advisor integrations: https://www.betterment.com/advisors/integrations

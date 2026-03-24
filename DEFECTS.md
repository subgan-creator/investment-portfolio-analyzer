# Defects Log - Investment Portfolio Analyzer

> **Purpose:** Track bugs found, root causes, and fixes applied.

---

## Resolved Defects

### DEF-001: JPMC Empower PDF Multi-Line Fund Names Parsed Incorrectly

**Date Found:** March 14, 2025
**Severity:** High
**Status:** Resolved

**Symptoms:**
- Fund names in JPMC Empower 401k statements were being parsed incorrectly
- Some fund names had duplicate "Fund" suffix (e.g., "Large Cap Growth Fund Fund")
- Some fund names were incomplete (e.g., "Government" instead of "Government Inflation-Protected Bond Fund")
- Some fund names picked up text from adjacent funds (e.g., "Target Date 2045 Fund Inflation-Protected Bond")

**Root Cause:**
The JPMC Empower PDF format has fund names that span multiple lines in the extracted text. For example:
```
Line 15: Government 13,058.78 1,071.83 1,002.82 15,133.43 633.978
Line 16: Inflation-Protected Bond
Line 17: Fund
```

The parser had two issues:
1. It was checking `endswith('Index')` as a complete name condition, but JPMC has funds like "Large Cap Value Index Fund" where the full name ends with "Fund"
2. The Wells Fargo format fix was looking for continuation lines even when the name was already complete

**Fix Applied:**
1. Changed the completion check from `endswith('Fund') or endswith('Index')` to just `endswith('Fund')`
2. Only look for continuation lines when the name does NOT already end with "Fund"
3. Look FORWARD (not backward) for continuation lines to reconstruct multi-line names

**Files Changed:**
- `src/utils/pdf_parser.py` (lines ~1355-1430)

**Verification:**
```bash
python3 -c "
from src.utils.pdf_parser import load_portfolio_from_empower_pdf

# Test JPMC format
portfolio = load_portfolio_from_empower_pdf('data/Empower JPMC 401k.pdf')
total = sum(h.current_price * h.shares for a in portfolio.accounts for h in a.holdings)
print(f'JPMC Total: \${total:,.2f}')  # Should be $308,887.19

# Test Wells Fargo format
portfolio = load_portfolio_from_empower_pdf('data/Empower Wells Dec 2025 .pdf')
total = sum(h.current_price * h.shares for a in portfolio.accounts for h in a.holdings)
print(f'Wells Fargo Total: \${total:,.2f}')  # Should be $32,525.70
"
```

**Expected Results:**
| Format | Expected Total | Holdings Count |
|--------|---------------|----------------|
| JPMC Empower | $308,887.19 | 10 |
| Wells Fargo Empower | $32,525.70 | 6 |

---

## How to Test PDF Parsers

### Manual Testing

1. **Start the web app:**
   ```bash
   cd /Users/ganapathisseetharaman/investment-portfolio-analyzer
   source venv/bin/activate
   python -m src.web.app
   ```
   Then open http://localhost:5001

2. **Upload test PDFs:**
   - `data/Empower JPMC 401k.pdf` - JPMC format
   - `data/Empower Wells Dec 2025 .pdf` - Wells Fargo format
   - `data/Betterment statement.pdf` - Betterment format
   - `data/Titan statements.pdf` - Titan format
   - `data/Acorns Dec 2025 statements.pdf` - Acorns format
   - `data/Arta Jan 2026 statements.pdf` - Arta Finance format

3. **Verify:**
   - All holdings are parsed correctly
   - No duplicate "Fund" suffixes
   - No missing fund name parts
   - Total values match statement totals

### Automated Testing (TODO)

Unit tests should be added to `tests/` directory:
- `tests/test_pdf_parser.py` - Test each PDF format parser
- `tests/test_empower_parser.py` - Specific tests for Empower format variations

---

### DEF-002: Titan/Apex PDF Detection Fails When Privacy Notices Precede Statement

**Date Found:** March 17, 2025
**Severity:** High
**Status:** Resolved

**Symptoms:**
- Titan Feb 2026 PDF statement fails to parse
- Error: "Unknown PDF format"
- Detection logic returns false, causing the file to be rejected

**Root Cause:**
Starting Feb 2026, Titan/Apex Clearing statements include privacy notice pages (3+ pages) at the beginning of the PDF before the actual account statement. The detection logic only checked the first page for markers like "TITAN" and "Apex Clearing", which are no longer on page 1.

PDF structure changed from:
```
Page 1: Account statement header with TITAN and Apex Clearing
Page 2+: Holdings, transactions, etc.
```

To:
```
Page 1-3: Privacy notices ("NOTICE OF CHANGES", "APEX CONSUMER PRIVACY NOTICES")
Page 4+: Account statement with TITAN and Apex Clearing markers
Page 7+: Holdings data
```

**Fix Applied:**
1. Updated `detect_titan_pdf()` to scan first 10 pages for markers instead of just page 1
2. Added early exit optimization when markers are found
3. Added multiple marker patterns: "Apex Clearing", "Apex Fintech", "APEX"
4. Updated `load_portfolio_from_titan_pdf()` to scan first 10 pages for account number
5. Added more robust account number regex pattern for format like "3TQ-XXXXX-XX"

**Files Changed:**
- `src/utils/pdf_parser.py` - `detect_titan_pdf()` and `load_portfolio_from_titan_pdf()` functions

**Verification:**
```bash
python3 -c "
from src.utils.pdf_parser import load_portfolio_from_pdf

pdf_path = 'data/Feb 2026 statements/Titan Feb 2026.pdf'
portfolio = load_portfolio_from_pdf(pdf_path, 'Test')
if portfolio:
    print(f'Success! Holdings: {len(portfolio.accounts[0].holdings)}')
    print(f'Account: {portfolio.accounts[0].account_id}')
    print(f'Total: \${portfolio.total_value:,.2f}')
else:
    print('FAILED')
"
```

**Expected Results:**
| Field | Expected Value |
|-------|---------------|
| Detection | "Detected Titan/Apex Clearing PDF format" |
| Account Number | 3TQ-61333-12 |
| Holdings Count | 57 |
| Total Value | ~$75,336.79 |

**Prevention:**
- PDF parsers should check multiple pages for format detection markers
- Account info extraction should not assume fixed page positions
- Consider adding format version detection for future statement changes

---

### DEF-003: False Concentration Warnings for Target Date Funds and Cash

**Date Found:** March 21, 2026
**Severity:** Medium
**Status:** Resolved

**Symptoms:**
- Target date funds (e.g., "TARGETDAT 22.2%") flagged as concentration risk
- Cash/money market positions (e.g., "CASH 18.1%") flagged as concentration risk
- S&P 500 index funds (e.g., VFIAX) flagged as concentration risk
- Sector ETFs (e.g., VGT) flagged at even moderate percentages

**Root Cause:**
The concentration analyzer treated all positions equally, regardless of their inherent diversification. It only checked if a position exceeded 10% of the portfolio, without considering:
- Target date funds contain hundreds of underlying securities (stocks, bonds, international)
- Total market/S&P 500 funds hold 500-3000+ securities
- Cash is inherently low-risk and not a concentration concern
- Sector ETFs hold 100+ stocks within their sector

**Fix Applied:**
1. Added `is_diversified_position()` function to detect inherently diversified holdings
2. Created `DIVERSIFIED_TICKERS` set with 60+ known diversified funds:
   - Total market ETFs (VTI, ITOT, VTSAX)
   - S&P 500 funds (VOO, SPY, VFIAX, FXAIX)
   - Bond funds (BND, AGG, VBTLX)
   - International funds (VXUS, IEFA, VWO)
   - Sector ETFs (VGT, VHT, VNQ)
   - Money market (VMFXX, SPAXX, FZFXX)
3. Added `DIVERSIFIED_KEYWORDS` list to match by description:
   - "target date", "target retirement"
   - "total market", "s&p 500"
   - "money market", "cash"
   - Target date years (2025, 2030, 2035, etc.)
4. Modified `identify_concentrated_positions()` to skip diversified positions
5. Updated Portfolio model to include `description` in consolidated positions

**Files Changed:**
- `src/portfolio_analyzer/concentration.py` - Major refactor with diversification detection
- `src/models/portfolio.py` - Added `description` field to positions

**Verification:**
```bash
python3 -c "
from src.utils.data_loader import load_portfolio_from_csv
from src.portfolio_analyzer.concentration import ConcentrationRiskAnalyzer, is_diversified_position

# Test detection function
print('=== Testing is_diversified_position() ===')
test_cases = [
    ('VFIAX', 'Fund', 'US Large Cap', '500 Index Fund'),  # Should SKIP
    ('CASH', 'Cash', 'Money Market', 'Cash'),             # Should SKIP
    ('NH2030', 'Target Date Fund', 'Education', 'NH PORTFOLIO 2030'),  # Should SKIP
    ('NVDA', 'Stock', 'Technology', 'NVIDIA Corporation'),  # Should CHECK
]
for ticker, ac, sector, desc in test_cases:
    result = is_diversified_position(ticker, ac, sector, desc)
    print(f'  {ticker}: {\"SKIP\" if result else \"CHECK\"}')
"
```

**Expected Results:**
| Position Type | Before Fix | After Fix |
|--------------|------------|-----------|
| Target Date Fund 22% | HIGH WARNING | Not flagged (diversified) |
| Cash 18% | HIGH WARNING | Not flagged (low risk) |
| VFIAX 29% | HIGH WARNING | Not flagged (500+ stocks) |
| NVDA 35% | HIGH WARNING | HIGH WARNING (single stock) |
| JPM 12% | MODERATE WARNING | MODERATE WARNING (single stock) |

**Prevention:**
- Concentration analysis should consider the nature of holdings
- Index funds and target date funds are designed for diversification
- Single stock positions are the real concentration risk

---

### DEF-004: Fund Profile PDF Upload Causes 502 Error on Render (Out of Memory)

**Date Found:** March 24, 2026
**Severity:** High
**Status:** Resolved

**Symptoms:**
- Uploading a fund profile PDF on Render returns 502 Bad Gateway
- Render logs show: "Instance failed: Ran out of memory (used over 512MB)"
- Works fine locally, fails only on Render's free tier (512MB memory limit)

**Root Cause:**
The `pdfplumber` library loads PDF content into memory. The original `parse_jpmc_fund_profile_pdf()` function opened the PDF once and iterated through all pages while keeping the PDF object open. This caused memory to accumulate because:
1. PDF parsing buffers weren't released until the `with` block completed
2. Each page's extracted text added to memory usage
3. Large PDFs (50+ pages) could easily exceed 512MB

**Fix Applied:**
1. **Memory-optimized parsing** - Process pages one at a time by reopening the PDF for each page, allowing garbage collection between pages
2. **Focused page range** - Only scan pages 10-30 where Target Date Funds typically appear (instead of all pages)
3. **Explicit garbage collection** - Call `gc.collect()` after processing each page to free memory immediately
4. **Better logging** - Added detailed logging to help diagnose future issues

**Key Code Change:**
```python
# BEFORE (memory-hungry):
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:  # All pages held in memory
        text = page.extract_text()
        # ... process

# AFTER (memory-efficient):
for page_num in range(start_page, end_page):
    with pdfplumber.open(pdf_path) as pdf:  # Reopen for each page
        page = pdf.pages[page_num]
        text = page.extract_text()
        # ... process
    gc.collect()  # Force memory release
```

**Files Changed:**
- `src/utils/fund_profile_parser.py` - Rewrote `parse_jpmc_fund_profile_pdf()` function
- `src/web/app.py` - Added logging for file size and parse progress
- `gunicorn.conf.py` - Added `preload_app=True` and `capture_output=False`

**Verification:**
1. Deploy to Render
2. Navigate to `/fund-profiles`
3. Upload a JPMC fund profile PDF
4. Check Render logs for:
   ```
   [Fund Profile Upload] Saved file: ...
   [Fund Profile Upload] File size: ... bytes
   [Fund Profile Upload] Starting PDF parse...
   [Fund Profile Upload] Parse complete. Found X profiles
   ```
5. No 502 error, profiles saved successfully

**Prevention - Render Memory Guidelines:**
- **512MB is tight** - Render's free tier has minimal memory
- **Avoid loading entire PDFs at once** - Process page-by-page
- **Use `gc.collect()`** - Force Python to release memory between operations
- **Set `max_requests` in gunicorn** - Restart workers periodically to prevent memory leaks
- **Log memory-intensive operations** - Add timing/size logging to identify bottlenecks
- **Consider async processing** - For large files, use background jobs instead of synchronous requests

**Related Configuration (gunicorn.conf.py):**
```python
workers = 1           # Single worker to minimize memory
preload_app = True    # Load app before forking for faster startup
max_requests = 100    # Restart worker every 100 requests to free memory
```

---

## Open Defects

*None currently tracked*

---

## Defect Template

```markdown
### DEF-XXX: Brief Description

**Date Found:** YYYY-MM-DD
**Severity:** High/Medium/Low
**Status:** Open/In Progress/Resolved

**Symptoms:**
- What the user sees

**Root Cause:**
- Technical explanation

**Fix Applied:**
- What was changed

**Files Changed:**
- List of files

**Verification:**
- How to test the fix
```

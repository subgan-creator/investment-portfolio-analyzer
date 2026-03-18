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

"""
PDF Parser for investment statements.
Supports Betterment statement format.
"""
import re
import gc
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from ..models import Portfolio, Account, Holding

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: pdfplumber not installed. PDF parsing disabled.")


# Additional ETF classifications for Betterment's typical holdings
BETTERMENT_TICKER_CLASSIFICATIONS = {
    # Bond ETFs
    'AGG': ('Bond', 'Fixed Income'),
    'BND': ('Bond', 'Fixed Income'),
    'BNDX': ('Bond', 'International Bonds'),
    'EMB': ('Bond', 'Emerging Markets Bonds'),
    'IAGG': ('Bond', 'International Bonds'),
    'MUB': ('Bond', 'Municipal Bonds'),
    'TFI': ('Bond', 'Municipal Bonds'),
    'STIP': ('Bond', 'TIPS'),
    'VTIP': ('Bond', 'TIPS'),
    'VWOB': ('Bond', 'Emerging Markets Bonds'),

    # US Stock ETFs
    'VTI': ('ETF', 'US Total Market'),
    'ITOT': ('ETF', 'US Total Market'),
    'SCHB': ('ETF', 'US Total Market'),
    'VOO': ('ETF', 'US Large Cap'),
    'SPYM': ('ETF', 'US Large Cap'),
    'VTV': ('ETF', 'US Large Cap Value'),
    'SCHV': ('ETF', 'US Large Cap Value'),
    'SPYV': ('ETF', 'US Large Cap Value'),
    'VBR': ('ETF', 'US Small Cap Value'),
    'IWN': ('ETF', 'US Small Cap Value'),
    'VOE': ('ETF', 'US Mid Cap Value'),
    'IWS': ('ETF', 'US Mid Cap Value'),

    # International Stock ETFs
    'VEA': ('ETF', 'International Developed'),
    'IEFA': ('ETF', 'International Developed'),
    'SCHF': ('ETF', 'International Developed'),
    'VWO': ('ETF', 'Emerging Markets'),
    'IEMG': ('ETF', 'Emerging Markets'),

    # Real Estate ETFs
    'VNQ': ('ETF', 'US Real Estate'),
    'SCHH': ('ETF', 'US Real Estate'),
    'VNQI': ('ETF', 'International Real Estate'),
}


def classify_betterment_ticker(ticker: str, description: str = "") -> Tuple[str, str]:
    """Classify a Betterment ticker into asset_class and sector."""
    if ticker in BETTERMENT_TICKER_CLASSIFICATIONS:
        return BETTERMENT_TICKER_CLASSIFICATIONS[ticker]

    desc_lower = description.lower() if description else ""

    # Infer from description
    if 'bond' in desc_lower:
        return ('Bond', 'Fixed Income')
    if 'real estate' in desc_lower or 'reit' in desc_lower:
        return ('ETF', 'Real Estate')
    if 'emerging' in desc_lower:
        return ('ETF', 'Emerging Markets')
    if 'international' in desc_lower or 'developed' in desc_lower:
        return ('ETF', 'International')
    if 'value' in desc_lower:
        return ('ETF', 'Value')

    return ('ETF', 'Diversified')


def detect_betterment_pdf(pdf_path: str) -> bool:
    """Check if a PDF is a Betterment statement."""
    if not PDF_SUPPORT:
        return False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0].extract_text()
                if first_page:
                    return 'Betterment' in first_page and 'Monthly Statement' in first_page
    except Exception:
        pass
    return False


def parse_betterment_holdings_from_text(text: str, account_name: str) -> List[Dict]:
    """
    Parse holdings from Betterment PDF text.

    The format is:
    Line 1: ETFs Description TICKER start_shares $start_val change_shares $change_val end_shares $end_val
    Line 2+: Description TICKER start_shares $start_val change_shares $change_val end_shares $end_val

    Returns list of holding dicts with ticker, shares, value.
    """
    holdings = []

    # Only parse if this is an ETF holdings section (has the ETF header line)
    if 'ETFs' not in text:
        return holdings

    # Pattern to match holding lines
    # The ticker is 2-5 uppercase letters, followed by numerical data
    # First line starts with "ETFs ", subsequent lines start with description directly
    holding_pattern = re.compile(
        r'^(?:ETFs\s+)?'                       # Optional "ETFs " prefix
        r'(.+?)\s+'                            # Description (non-greedy)
        r'([A-Z]{2,5})\s+'                     # Ticker (2-5 uppercase letters)
        r'([\d.]+)\s+'                         # Starting shares
        r'-?\$?([\d,.]+)\s+'                   # Starting value
        r'-?([\d.]+)\s+'                       # Change shares
        r'-?\$?([\d,.]+)\s+'                   # Change value
        r'([\d.]+)\s+'                         # Ending shares (capture)
        r'\$?([\d,.]+)$'                       # Ending value (capture)
    )

    in_holdings = False
    for line in text.split('\n'):
        line = line.strip()

        # Start parsing after HOLDINGS header
        if 'HOLDINGS' in line:
            in_holdings = True
            continue

        if not in_holdings:
            continue

        # Skip header and footer lines
        if not line or 'Page' in line or 'Type' in line or 'Starting' in line:
            continue

        # Stop at end of holdings section (but not for fund names containing "Total")
        if line.startswith('Total') or 'Footnotes' in line:
            break

        match = holding_pattern.match(line)
        if match:
            description = match.group(1).strip()
            ticker = match.group(2)
            shares_str = match.group(7)  # Ending shares
            value_str = match.group(8)   # Ending value

            # Validate ticker is a known ETF pattern (not a bank name)
            if ticker not in BETTERMENT_TICKER_CLASSIFICATIONS:
                # Check if it looks like a valid ETF ticker
                if not re.match(r'^[A-Z]{2,5}$', ticker):
                    continue
                # Skip if description looks like a bank
                if 'Bank' in description or 'FDIC' in description:
                    continue

            try:
                shares = float(shares_str.replace(',', ''))
                value = float(value_str.replace(',', ''))

                if shares > 0 and value > 0:
                    holdings.append({
                        'ticker': ticker,
                        'description': description,
                        'shares': shares,
                        'value': value,
                        'account_name': account_name,
                    })
            except ValueError:
                continue

    return holdings


def parse_betterment_continuation_page(text: str, account_name: str) -> List[Dict]:
    """
    Parse holdings from a continuation page (page without HOLDINGS header).
    These pages continue listings from a previous page.
    """
    holdings = []

    # Pattern for holding lines - same as main parser but without requiring ETFs marker
    holding_pattern = re.compile(
        r'^(.+?)\s+'                            # Description (non-greedy)
        r'([A-Z]{2,5})\s+'                     # Ticker (2-5 uppercase letters)
        r'([\d.]+)\s+'                         # Starting shares
        r'-?\$?([\d,.]+)\s+'                   # Starting value
        r'-?([\d.]+)\s+'                       # Change shares
        r'-?\$?([\d,.]+)\s+'                   # Change value
        r'([\d.]+)\s+'                         # Ending shares (capture)
        r'\$?([\d,.]+)$'                       # Ending value (capture)
    )

    for line in text.split('\n'):
        line = line.strip()

        # Skip header and footer lines
        if not line or 'Page' in line or 'Type' in line or 'Starting' in line:
            continue

        # Skip non-holding sections
        if 'DIVIDEND' in line or 'ACTIVITY' in line or 'Footnotes' in line:
            break

        match = holding_pattern.match(line)
        if match:
            description = match.group(1).strip()
            ticker = match.group(2)
            shares_str = match.group(7)  # Ending shares
            value_str = match.group(8)   # Ending value

            # Validate ticker is a known ETF or looks valid
            if ticker not in BETTERMENT_TICKER_CLASSIFICATIONS:
                if 'Bank' in description or 'FDIC' in description:
                    continue

            try:
                shares = float(shares_str.replace(',', ''))
                value = float(value_str.replace(',', ''))

                if shares > 0 and value > 0:
                    holdings.append({
                        'ticker': ticker,
                        'description': description,
                        'shares': shares,
                        'value': value,
                        'account_name': account_name,
                    })
            except ValueError:
                continue

    return holdings


def parse_betterment_holdings_table(table_data: List[List], account_name: str) -> List[Dict]:
    """
    Parse a holdings table from Betterment PDF.
    Returns list of holding dicts with ticker, shares, value.
    """
    holdings = []

    if not table_data or len(table_data) < 2:
        return holdings

    # Find header row
    header_row = None
    header_idx = 0
    for idx, row in enumerate(table_data):
        if row and any('Ticker' in str(cell) for cell in row if cell):
            header_row = row
            header_idx = idx
            break

    if not header_row:
        return holdings

    # Map column indices
    col_map = {}
    for idx, cell in enumerate(header_row):
        if cell:
            cell_str = str(cell).strip()
            if 'Description' in cell_str:
                col_map['description'] = idx
            elif 'Ticker' in cell_str:
                col_map['ticker'] = idx
            elif 'Ending' in cell_str and 'Shares' in cell_str:
                col_map['shares'] = idx
            elif 'Ending' in cell_str and 'Value' in cell_str:
                col_map['value'] = idx
            elif cell_str == 'Shares' and 'shares' not in col_map:
                col_map['shares'] = idx
            elif cell_str == 'Value' and 'value' not in col_map:
                col_map['value'] = idx

    # Parse data rows
    for row in table_data[header_idx + 1:]:
        if not row or len(row) < 3:
            continue

        # Skip non-data rows
        row_str = ' '.join(str(c) for c in row if c)
        if 'Total' in row_str or 'Cash' in row_str or not any(c for c in row if c):
            continue

        try:
            ticker = str(row[col_map.get('ticker', 1)]).strip() if col_map.get('ticker') is not None and row[col_map['ticker']] else None
            if not ticker or ticker == 'None' or ticker == '–':
                continue

            description = str(row[col_map.get('description', 0)]).strip() if col_map.get('description') is not None and row[col_map['description']] else ''

            # Get shares - try Ending column first, then last Shares column
            shares_str = '0'
            if 'shares' in col_map and row[col_map['shares']]:
                shares_str = str(row[col_map['shares']])

            # Get value - try Ending column first
            value_str = '0'
            if 'value' in col_map and row[col_map['value']]:
                value_str = str(row[col_map['value']])

            # Clean and parse numbers
            shares = float(shares_str.replace(',', '').replace('$', '').strip() or '0')
            value = float(value_str.replace(',', '').replace('$', '').strip() or '0')

            if shares > 0 and value > 0:
                holdings.append({
                    'ticker': ticker,
                    'description': description,
                    'shares': shares,
                    'value': value,
                    'account_name': account_name,
                })
        except (ValueError, IndexError, TypeError):
            continue

    return holdings


def load_portfolio_from_betterment_pdf(pdf_path: str, portfolio_name: str = "Betterment Portfolio") -> Optional[Portfolio]:
    """
    Load portfolio from a Betterment monthly statement PDF.

    Args:
        pdf_path: Path to the Betterment PDF statement
        portfolio_name: Name for the portfolio

    Returns:
        Portfolio object with accounts and holdings, or None if parsing fails
    """
    if not PDF_SUPPORT:
        print("PDF support not available. Install pdfplumber: pip install pdfplumber")
        return None

    portfolio = Portfolio(portfolio_name=portfolio_name)
    accounts_dict: Dict[str, Account] = {}
    all_holdings: List[Dict] = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            current_account = None

            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ''

                # Detect account sections by looking for account headers
                # Betterment has distinct account sections like "Taxable Investing Account", "Cash Reserve", etc.

                # Check for account headers in the text
                account_patterns = [
                    (r'Taxable Investing Account.*Account #(\d+)', 'Taxable Investing', 'taxable'),
                    (r'Cash Reserve.*Account #(\d+)', 'Cash Reserve', 'taxable'),
                    (r'(\w+ Education) - Automated Investing.*Account #(\d+)', None, 'taxable'),  # Dynamic name
                    (r'Automated Investing.*Account #(\d+)', 'Automated Investing', 'taxable'),
                    (r'Traditional IRA.*Account #(\d+)', 'Traditional IRA', 'tax_deferred'),
                    (r'Roth IRA.*Account #(\d+)', 'Roth IRA', 'tax_free'),
                ]

                for pattern, default_name, tax_status in account_patterns:
                    match = re.search(pattern, text)
                    if match:
                        if default_name is None:
                            # Dynamic name from capture group
                            account_name = match.group(1) + ' - Automated Investing'
                            account_id = match.group(2)
                        else:
                            account_name = default_name
                            account_id = match.group(1)

                        # Use account_name + account_id as key (some accounts share IDs)
                        account_key = f"{account_name}_{account_id}"
                        if account_key not in accounts_dict:
                            current_account = Account(
                                account_id=account_id,
                                account_name=account_name,
                                account_type='Betterment ' + account_name,
                                tax_status=tax_status,
                            )
                            accounts_dict[account_key] = current_account
                        else:
                            current_account = accounts_dict[account_key]
                        break  # Stop after first matching pattern

                # Parse holdings from text (more reliable than table extraction)
                # Check for HOLDINGS section or continuation pages (pages that have holdings data without header)
                if current_account:
                    if 'HOLDINGS' in text or 'ETFs' in text:
                        holdings = parse_betterment_holdings_from_text(text, current_account.account_name)
                        all_holdings.extend(holdings)
                    else:
                        # Try parsing as continuation page - look for holding-like lines
                        holdings = parse_betterment_continuation_page(text, current_account.account_name)
                        all_holdings.extend(holdings)

                # NOTE: Removed table extraction fallback - it's very slow and memory-intensive
                # for large PDFs (37+ pages), causing timeouts on limited-memory servers.
                # Text extraction above handles holdings parsing effectively.

                # Free memory periodically (every 10 pages) for large PDFs
                if page_num > 0 and page_num % 10 == 0:
                    gc.collect()

        # Now create holdings from parsed data
        # Group by account and add to portfolio
        holdings_by_account: Dict[str, List[Dict]] = {}
        for h in all_holdings:
            acc_name = h.get('account_name', 'Unknown')
            if acc_name not in holdings_by_account:
                holdings_by_account[acc_name] = []
            holdings_by_account[acc_name].append(h)

        # Create accounts with holdings
        for acc_name, holdings_list in holdings_by_account.items():
            # Find or create account
            account = None
            for acc in accounts_dict.values():
                if acc.account_name == acc_name:
                    account = acc
                    break

            if not account:
                # Create a new account
                account = Account(
                    account_id=f"betterment_{acc_name.replace(' ', '_').lower()}",
                    account_name=acc_name,
                    account_type=f'Betterment {acc_name}',
                    tax_status='taxable',
                )
                accounts_dict[account.account_id] = account

            # Add holdings to account
            for h in holdings_list:
                ticker = h['ticker']
                shares = h['shares']
                value = h['value']
                description = h.get('description', '')

                # Calculate current price
                current_price = value / shares if shares > 0 else 0

                # Classify the ticker
                asset_class, sector = classify_betterment_ticker(ticker, description)

                holding = Holding(
                    ticker=ticker,
                    shares=shares,
                    cost_basis_per_share=current_price,  # Betterment doesn't show cost basis in monthly statement
                    purchase_date=datetime(2024, 1, 1),  # Placeholder
                    current_price=current_price,
                    asset_class=asset_class,
                    sector=sector,
                    cost_basis_estimated=True,  # No cost basis in Betterment monthly statements
                )
                account.add_holding(holding)

        # Add accounts to portfolio
        for account in accounts_dict.values():
            if account.holdings:
                portfolio.add_account(account)

        # Also try to add Cash Reserve as a cash holding
        # Parse cash balance from text
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ''
                # Look for Cash Reserve ending balance (use non-greedy match to get first occurrence)
                cash_match = re.search(r'Cash Reserve Account.*?Ending Balance \([^)]+\) \$([0-9,]+\.\d{2})', text, re.DOTALL)
                if cash_match:
                    cash_value = float(cash_match.group(1).replace(',', ''))
                    if cash_value > 0:
                        # Create Cash Reserve account
                        cash_account = Account(
                            account_id='betterment_cash_reserve',
                            account_name='Cash Reserve',
                            account_type='Betterment Cash Reserve',
                            tax_status='taxable',
                        )
                        cash_holding = Holding(
                            ticker='CASH',
                            shares=cash_value,
                            cost_basis_per_share=1.0,
                            purchase_date=datetime.now(),
                            current_price=1.0,
                            asset_class='Cash',
                            sector='Money Market',
                        )
                        cash_account.add_holding(cash_holding)
                        portfolio.add_account(cash_account)
                    break

        if portfolio.accounts:
            return portfolio
        else:
            print(f"No holdings found in Betterment PDF: {pdf_path}")
            return None

    except Exception as e:
        print(f"Error parsing Betterment PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# TITAN PDF PARSER
# =============================================================================
# LEARNING: Titan statements are from Apex Clearing Corporation
# Format: Account statement with holdings table showing TICKER C QUANTITY PRICE VALUE
# =============================================================================

# Titan-specific ticker classifications (adds to Betterment ones)
TITAN_TICKER_CLASSIFICATIONS = {
    # Crypto ETFs
    'IBIT': ('ETF', 'Crypto'),
    'ETHA': ('ETF', 'Crypto'),

    # Gold/Mining
    'GLD': ('ETF', 'Commodities'),
    'GDX': ('ETF', 'Gold Miners'),
    'GDXJ': ('ETF', 'Gold Miners'),

    # Uranium
    'UEC': ('Stock', 'Uranium'),
    'CCJ': ('Stock', 'Uranium'),
    'DNN': ('Stock', 'Uranium'),
    'NXE': ('Stock', 'Uranium'),
    'URNM': ('ETF', 'Uranium'),

    # Tech
    'NVDA': ('Stock', 'Technology'),
    'MSFT': ('Stock', 'Technology'),
    'GOOG': ('Stock', 'Technology'),
    'META': ('Stock', 'Technology'),
    'AMZN': ('Stock', 'Technology'),
    'ORCL': ('Stock', 'Technology'),
    'NOW': ('Stock', 'Technology'),
    'OKTA': ('Stock', 'Technology'),
    'ESTC': ('Stock', 'Technology'),
    'CIEN': ('Stock', 'Technology'),
    'ASML': ('Stock', 'Technology'),
    'MU': ('Stock', 'Technology'),
    'ADI': ('Stock', 'Technology'),
    'AVGO': ('Stock', 'Technology'),
    'AEVA': ('Stock', 'Technology'),

    # Financials
    'SPGI': ('Stock', 'Financials'),
    'MA': ('Stock', 'Financials'),
    'V': ('Stock', 'Financials'),
    'SCHW': ('Stock', 'Financials'),
    'MCO': ('Stock', 'Financials'),
    'FICO': ('Stock', 'Financials'),
    'FNMA': ('Stock', 'Financials'),
    'FMCC': ('Stock', 'Financials'),
    'FCNCA': ('Stock', 'Financials'),
    'NU': ('Stock', 'Financials'),
    'SSNC': ('Stock', 'Financials'),

    # Consumer/Transport
    'UBER': ('Stock', 'Technology'),
    'MELI': ('Stock', 'Consumer'),

    # Industrial
    'TDG': ('Stock', 'Industrial'),
    'TMO': ('Stock', 'Healthcare'),
    'GE': ('Stock', 'Industrial'),
    'RTX': ('Stock', 'Industrial'),
    'CP': ('Stock', 'Industrial'),
    'CRS': ('Stock', 'Industrial'),

    # International/Emerging
    'BMA': ('Stock', 'International'),
    'PAM': ('Stock', 'International'),
    'SUPV': ('Stock', 'International'),
    'YPF': ('Stock', 'International'),
    'VIST': ('Stock', 'International'),
    'KWEB': ('ETF', 'International'),
    'EWJ': ('ETF', 'International'),
    'SAFRY': ('Stock', 'International'),
    'LVMUY': ('Stock', 'International'),
}


def classify_titan_ticker(ticker: str, description: str = "") -> Tuple[str, str]:
    """Classify a Titan ticker into asset_class and sector."""
    # Check Titan-specific first
    if ticker in TITAN_TICKER_CLASSIFICATIONS:
        return TITAN_TICKER_CLASSIFICATIONS[ticker]

    # Then check Betterment classifications
    if ticker in BETTERMENT_TICKER_CLASSIFICATIONS:
        return BETTERMENT_TICKER_CLASSIFICATIONS[ticker]

    # Infer from description
    desc_lower = description.lower() if description else ""

    if 'etf' in desc_lower or 'fund' in desc_lower:
        return ('ETF', 'Diversified')
    if 'inc' in desc_lower or 'corp' in desc_lower or 'ltd' in desc_lower:
        return ('Stock', 'Other')

    return ('Stock', 'Other')


def detect_titan_pdf(pdf_path: str) -> bool:
    """
    Check if a PDF is a Titan/Apex Clearing statement.

    LEARNING: Titan statements may have privacy notices on first pages (as of Feb 2026).
    We check the first 10 pages for identifying markers to handle this.

    Detection markers:
    - "TITAN" (the broker name)
    - "Apex Clearing" or "Apex Fintech" (the clearing firm)
    - Account format like "ACCOUNT NUMBER" with pattern like "3TQ-XXXXX-XX"
    """
    if not PDF_SUPPORT:
        return False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Check first 10 pages for markers (handles privacy notice pages)
            pages_to_check = min(10, len(pdf.pages))
            combined_text = ""

            for i in range(pages_to_check):
                page_text = pdf.pages[i].extract_text() or ""
                combined_text += page_text + "\n"

                # Early exit if we find markers
                has_titan = 'TITAN' in page_text.upper()
                has_apex = 'Apex Clearing' in page_text or 'Apex Fintech' in page_text or 'APEX' in page_text.upper()

                if has_titan and has_apex:
                    return True

            # Final check on combined text
            has_titan = 'TITAN' in combined_text.upper()
            has_apex = 'Apex Clearing' in combined_text or 'Apex Fintech' in combined_text
            return has_titan and has_apex

    except Exception:
        pass
    return False


def load_portfolio_from_titan_pdf(pdf_path: str, portfolio_name: str = "Titan Portfolio") -> Optional[Portfolio]:
    """
    Load portfolio from a Titan/Apex Clearing statement PDF.

    LEARNING: How this parser works:
    1. Scans all pages for holdings data
    2. Uses regex to match lines with format: DESCRIPTION TICKER C QUANTITY PRICE VALUE
    3. Creates a single account with all holdings

    Args:
        pdf_path: Path to the Titan PDF statement
        portfolio_name: Name for the portfolio

    Returns:
        Portfolio object with holdings, or None if parsing fails
    """
    if not PDF_SUPPORT:
        print("PDF support not available. Install pdfplumber: pip install pdfplumber")
        return None

    portfolio = Portfolio(portfolio_name=portfolio_name)

    # LEARNING: Regex pattern explanation:
    # ^(.+?)\s+     - Description (non-greedy, stops at first match)
    # ([A-Z]{1,5})  - Ticker symbol (1-5 uppercase letters)
    # \s+C\s+       - Account type "C" (Cash)
    # ([\d,.]+)     - Quantity (numbers with commas/decimals)
    # \s+\$?([\d,.]+) - Price (optional $ sign)
    # \s+\$?([\d,.]+) - Market Value
    holding_pattern = re.compile(
        r'^(.+?)\s+([A-Z]{1,5})\s+C\s+([\d,.]+)\s+\$?([\d,.]+)\s+\$?([\d,.]+)'
    )

    all_holdings = []
    account_number = "titan_account"
    account_name = "Titan Individual Account"

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # LEARNING: Titan statements may have privacy notices on first pages (Feb 2026+)
            # Scan first 10 pages for account info
            for i in range(min(10, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text() or ''

                # Try to get account number (format: 3TQ-XXXXX-XX)
                acc_match = re.search(r'ACCOUNT NUMBER\s+([A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+)', page_text)
                if acc_match:
                    account_number = acc_match.group(1)
                    break

                # Alternative pattern
                acc_match2 = re.search(r'ACCOUNT NUMBER\s+(\S+)', page_text)
                if acc_match2 and acc_match2.group(1) not in ['RR', 'TTA']:
                    account_number = acc_match2.group(1)
                    break

            # Scan all pages for holdings
            for page in pdf.pages:
                text = page.extract_text() or ''

                for line in text.split('\n'):
                    line = line.strip()

                    # Skip header and non-holding lines
                    if any(skip in line for skip in ['SYMBOL/', 'DESCRIPTION', 'Total', 'FDIC', 'EQUITIES']):
                        continue

                    match = holding_pattern.match(line)
                    if match:
                        desc, ticker, qty_str, price_str, value_str = match.groups()

                        # Skip FDIC deposit program (it's cash, not securities)
                        if ticker == 'ISPAZ':
                            continue

                        try:
                            quantity = float(qty_str.replace(',', ''))
                            price = float(price_str.replace(',', ''))
                            value = float(value_str.replace(',', ''))

                            if quantity > 0 and value > 0:
                                all_holdings.append({
                                    'ticker': ticker,
                                    'description': desc.strip(),
                                    'quantity': quantity,
                                    'price': price,
                                    'value': value,
                                })
                        except ValueError:
                            continue

            # Also capture FDIC cash balance
            for page in pdf.pages:
                text = page.extract_text() or ''
                fdic_match = re.search(r'FDIC Insured Deposits\s+([\d,.]+)', text)
                if fdic_match:
                    cash_value = float(fdic_match.group(1).replace(',', ''))
                    if cash_value > 0:
                        all_holdings.append({
                            'ticker': 'CASH',
                            'description': 'FDIC Insured Deposits',
                            'quantity': cash_value,
                            'price': 1.0,
                            'value': cash_value,
                        })
                    break

        if not all_holdings:
            print(f"No holdings found in Titan PDF: {pdf_path}")
            return None

        # Create the account
        account = Account(
            account_id=account_number,
            account_name=account_name,
            account_type='Titan Brokerage',
            tax_status='taxable',  # Individual accounts are taxable
        )

        # Add holdings to account
        for h in all_holdings:
            asset_class, sector = classify_titan_ticker(h['ticker'], h['description'])

            holding = Holding(
                ticker=h['ticker'],
                shares=h['quantity'],
                cost_basis_per_share=h['price'],  # Using current price as cost basis (not provided)
                purchase_date=datetime(2024, 1, 1),  # Placeholder
                current_price=h['price'],
                asset_class=asset_class,
                sector=sector,
                cost_basis_estimated=True,  # No cost basis in Titan statements
            )
            account.add_holding(holding)

        portfolio.add_account(account)
        return portfolio

    except Exception as e:
        print(f"Error parsing Titan PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# ACORNS PDF PARSER
# =============================================================================
# LEARNING: Acorns statements are from Acorns Securities, LLC
# Format: Simple ETF portfolio with holdings in "Asset Allocation" table
# Pattern: Description (TICKER) QUANTITY $PRICE $VALUE ALLOCATION% TYPE
# =============================================================================

# Acorns typically uses a small set of ETFs
ACORNS_TICKER_CLASSIFICATIONS = {
    'VOO': ('ETF', 'US Large Cap'),      # Vanguard S&P 500
    'IJH': ('ETF', 'US Mid Cap'),        # iShares S&P Mid-Cap
    'IJR': ('ETF', 'US Small Cap'),      # iShares S&P Small-Cap
    'IXUS': ('ETF', 'International'),    # iShares Total International
    'VEA': ('ETF', 'International Developed'),
    'VWO': ('ETF', 'Emerging Markets'),
    'AGG': ('Bond', 'Fixed Income'),     # iShares Core US Aggregate Bond
    'TIP': ('Bond', 'TIPS'),             # iShares TIPS Bond
    'LQD': ('Bond', 'Corporate Bonds'),  # iShares Investment Grade Corporate
    'GLD': ('ETF', 'Commodities'),       # SPDR Gold
    'IAU': ('ETF', 'Commodities'),       # iShares Gold
}


def classify_acorns_ticker(ticker: str, description: str = "") -> Tuple[str, str]:
    """Classify an Acorns ticker into asset_class and sector."""
    if ticker in ACORNS_TICKER_CLASSIFICATIONS:
        return ACORNS_TICKER_CLASSIFICATIONS[ticker]

    # Check Betterment classifications as fallback (they overlap)
    if ticker in BETTERMENT_TICKER_CLASSIFICATIONS:
        return BETTERMENT_TICKER_CLASSIFICATIONS[ticker]

    desc_lower = description.lower() if description else ""

    if 'bond' in desc_lower:
        return ('Bond', 'Fixed Income')
    if 'international' in desc_lower:
        return ('ETF', 'International')
    if 's&p 500' in desc_lower or 'large' in desc_lower:
        return ('ETF', 'US Large Cap')
    if 'mid' in desc_lower:
        return ('ETF', 'US Mid Cap')
    if 'small' in desc_lower:
        return ('ETF', 'US Small Cap')

    return ('ETF', 'Diversified')


def detect_acorns_pdf(pdf_path: str) -> bool:
    """
    Check if a PDF is an Acorns statement.
    LEARNING: Acorns statements have "Acorns Securities, LLC" marker.
    """
    if not PDF_SUPPORT:
        return False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0].extract_text()
                if first_page:
                    has_acorns = 'Acorns Securities' in first_page or 'Acorns Advisers' in first_page
                    has_finra = 'FINRA/SIPC' in first_page
                    return has_acorns and has_finra
    except Exception:
        pass
    return False


def load_portfolio_from_acorns_pdf(pdf_path: str, portfolio_name: str = "Acorns Portfolio") -> Optional[Portfolio]:
    """
    Load portfolio from an Acorns statement PDF.

    LEARNING: How this parser works:
    1. Looks for "Asset Allocation" section
    2. Uses regex to match lines with format: Description (TICKER) QUANTITY $PRICE $VALUE ALLOCATION% TYPE
    3. Creates a single account with all holdings

    Args:
        pdf_path: Path to the Acorns PDF statement
        portfolio_name: Name for the portfolio

    Returns:
        Portfolio object with holdings, or None if parsing fails
    """
    if not PDF_SUPPORT:
        print("PDF support not available. Install pdfplumber: pip install pdfplumber")
        return None

    portfolio = Portfolio(portfolio_name=portfolio_name)

    # LEARNING: Regex pattern for Acorns holdings
    # Format: iShares Core S&P Mid-Cap ETF (IJH) 72.76865 $66.00 $4,802.73 9% Base
    # Pattern: Description (TICKER) QUANTITY $PRICE $VALUE ALLOCATION% TYPE
    holding_pattern = re.compile(
        r'^(.+?)\s+\(([A-Z]{2,5})\)\s+'   # Description (TICKER)
        r'([\d,.]+)\s+'                    # Quantity
        r'\$([\d,.]+)\s+'                  # Price
        r'\$([\d,.]+)\s+'                  # Value
        r'(\d+)%\s+'                       # Allocation %
        r'(\w+)'                           # Portfolio Type
    )

    all_holdings = []
    account_number = "acorns_account"
    account_name = "Acorns Investment Account"

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract account info from first page
            first_page = pdf.pages[0].extract_text() or ''

            # Try to get account number
            acc_match = re.search(r'Account Number\s+(\d+)', first_page)
            if acc_match:
                account_number = acc_match.group(1)

            # Also try to get the account ID
            id_match = re.search(r'Account ID\s+([a-f0-9-]+)', first_page)
            if id_match:
                account_name = f"Acorns Account ({id_match.group(1)[:8]}...)"

            # Scan all pages for Asset Allocation section
            in_asset_allocation = False
            for page in pdf.pages:
                text = page.extract_text() or ''

                for line in text.split('\n'):
                    line = line.strip()

                    # Detect Asset Allocation section
                    if 'Asset Allocation' in line:
                        in_asset_allocation = True
                        continue

                    # Skip header line
                    if 'Quantity Price Value' in line or 'Portfolio Type' in line:
                        continue

                    # Stop at next section (like "Realized" or "Summary")
                    if in_asset_allocation and ('Realized' in line or 'Summary' in line or 'Page' in line):
                        in_asset_allocation = False
                        continue

                    if not in_asset_allocation:
                        continue

                    # Try to match holding line
                    match = holding_pattern.match(line)
                    if match:
                        description = match.group(1).strip()
                        ticker = match.group(2)
                        quantity_str = match.group(3)
                        price_str = match.group(4)
                        value_str = match.group(5)

                        try:
                            quantity = float(quantity_str.replace(',', ''))
                            price = float(price_str.replace(',', ''))
                            value = float(value_str.replace(',', ''))

                            if quantity > 0 and value > 0:
                                all_holdings.append({
                                    'ticker': ticker,
                                    'description': description,
                                    'quantity': quantity,
                                    'price': price,
                                    'value': value,
                                })
                        except ValueError:
                            continue

        if not all_holdings:
            print(f"No holdings found in Acorns PDF: {pdf_path}")
            return None

        # Create the account
        account = Account(
            account_id=account_number,
            account_name=account_name,
            account_type='Acorns Brokerage',
            tax_status='taxable',
        )

        # Add holdings to account
        for h in all_holdings:
            asset_class, sector = classify_acorns_ticker(h['ticker'], h['description'])

            holding = Holding(
                ticker=h['ticker'],
                shares=h['quantity'],
                cost_basis_per_share=h['price'],  # Using current price as cost basis
                purchase_date=datetime(2024, 1, 1),  # Placeholder
                current_price=h['price'],
                asset_class=asset_class,
                sector=sector,
                cost_basis_estimated=True,  # No cost basis in Acorns statements
            )
            account.add_holding(holding)

        portfolio.add_account(account)
        return portfolio

    except Exception as e:
        print(f"Error parsing Acorns PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# ARTA FINANCE PDF PARSER
# =============================================================================
# LEARNING: Arta Finance uses Pershing as custodian
# Format: Money Market funds + Alternative Investments (Private Equity, etc.)
# =============================================================================

def classify_arta_ticker(ticker: str, description: str = "") -> Tuple[str, str]:
    """Classify an Arta Finance holding into asset_class and sector."""
    desc_lower = description.lower() if description else ""

    if 'money' in desc_lower or 'cash' in desc_lower or 'dreyfus' in desc_lower:
        return ('Cash', 'Money Market')
    if 'private equity' in desc_lower or 'kkr' in desc_lower:
        return ('Alternative', 'Private Equity')
    if 'hedge' in desc_lower:
        return ('Alternative', 'Hedge Fund')
    if 'real estate' in desc_lower or 'reit' in desc_lower:
        return ('Alternative', 'Real Estate')
    if 'venture' in desc_lower:
        return ('Alternative', 'Venture Capital')

    return ('Alternative', 'Other')


def detect_arta_pdf(pdf_path: str) -> bool:
    """
    Check if a PDF is an Arta Finance statement.
    LEARNING: Arta Finance statements have "ARTA FINANCE" and use Pershing.
    """
    if not PDF_SUPPORT:
        return False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0].extract_text()
                if first_page:
                    has_arta = 'ARTA FINANCE' in first_page or 'Arta Finance' in first_page
                    has_pershing = 'Pershing' in first_page or 'ASD-' in first_page
                    return has_arta or (has_pershing and 'Portfolio at a Glance' in first_page)
    except Exception:
        pass
    return False


def load_portfolio_from_arta_pdf(pdf_path: str, portfolio_name: str = "Arta Finance Portfolio") -> Optional[Portfolio]:
    """
    Load portfolio from an Arta Finance/Pershing statement PDF.

    LEARNING: How this parser works:
    1. Looks for Money Market Fund Detail section for cash holdings
    2. Looks for Portfolio Holdings section for alternative investments
    3. Parses each holding type with specific patterns

    Args:
        pdf_path: Path to the Arta Finance PDF statement
        portfolio_name: Name for the portfolio

    Returns:
        Portfolio object with holdings, or None if parsing fails
    """
    if not PDF_SUPPORT:
        print("PDF support not available. Install pdfplumber: pip install pdfplumber")
        return None

    portfolio = Portfolio(portfolio_name=portfolio_name)
    all_holdings = []
    account_number = "arta_account"
    account_name = "Arta Finance Account"

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract account info from first page
            first_page = pdf.pages[0].extract_text() or ''

            # Try to get account number (format: ASD-XXXXXX)
            acc_match = re.search(r'Account Number:\s*(ASD-\d+)', first_page)
            if acc_match:
                account_number = acc_match.group(1)
                account_name = f"Arta Finance ({account_number})"

            # Scan all pages for holdings
            full_text = ''
            for page in pdf.pages:
                full_text += (page.extract_text() or '') + '\n'

            # Pattern 1: Money Market Fund - look for closing balance
            # Format: "01/30/26 Closing Balance $97.31"
            money_market_pattern = re.compile(
                r'(DREYFUS[^\n]+)\n.*?Closing Balance\s+\$([\d,.]+)',
                re.DOTALL
            )
            for match in money_market_pattern.finditer(full_text):
                fund_name = match.group(1).strip()
                balance = float(match.group(2).replace(',', ''))
                if balance > 0:
                    all_holdings.append({
                        'ticker': 'DGSXX',  # Dreyfus Govt Cash Mgmt ticker
                        'description': fund_name,
                        'quantity': balance,
                        'price': 1.0,
                        'value': balance,
                        'cost_basis': balance,
                    })

            # Pattern 2: Alternative Investments (Limited Partnerships / LLC's)
            # Format in table: Date Acquired | Quantity | Unit Cost | Cost Basis | Market Price | Estimated Value | Gain/Loss
            # Example: 06/26/24*,3 703.5800 27.3070 19,213.00 33.7504 23,746.11 4,533.11

            # First find the security name
            alt_invest_pattern = re.compile(
                r'([A-Z][A-Z\s]+(?:LLC|LP|FUND|TRUST)[^\n]*)\s+Security Identifier:\s*(\w+)',
                re.IGNORECASE
            )

            # Then find the holdings data line
            holdings_data_pattern = re.compile(
                r'(\d{2}/\d{2}/\d{2})[*,\d]*\s+'  # Date acquired
                r'([\d,.]+)\s+'                    # Quantity
                r'([\d,.]+)\s+'                    # Unit Cost
                r'([\d,.]+)\s+'                    # Cost Basis
                r'([\d,.]+)\s+'                    # Market Price
                r'([\d,.]+)\s+'                    # Estimated Value
                r'-?([\d,.]+)'                     # Gain/Loss
            )

            # Find all alternative investment sections
            for page in pdf.pages:
                text = page.extract_text() or ''

                # Check if this page has alternative investments
                if 'Limited Partnerships' in text or 'ALTERNATIVE INVESTMENTS' in text:
                    # Find security names
                    sec_matches = list(alt_invest_pattern.finditer(text))

                    # Find holdings data
                    data_matches = list(holdings_data_pattern.finditer(text))

                    for i, data_match in enumerate(data_matches):
                        quantity = float(data_match.group(2).replace(',', ''))
                        unit_cost = float(data_match.group(3).replace(',', ''))
                        cost_basis = float(data_match.group(4).replace(',', ''))
                        market_price = float(data_match.group(5).replace(',', ''))
                        value = float(data_match.group(6).replace(',', ''))

                        # Try to match with security name
                        sec_name = "Alternative Investment"
                        sec_id = "ALT"
                        if i < len(sec_matches):
                            sec_name = sec_matches[i].group(1).strip()
                            sec_id = sec_matches[i].group(2)

                        if quantity > 0 and value > 0:
                            all_holdings.append({
                                'ticker': sec_id[:5] if len(sec_id) > 5 else sec_id,
                                'description': sec_name,
                                'quantity': quantity,
                                'price': market_price,
                                'value': value,
                                'cost_basis': cost_basis,
                            })

        if not all_holdings:
            print(f"No holdings found in Arta Finance PDF: {pdf_path}")
            return None

        # Create the account
        account = Account(
            account_id=account_number,
            account_name=account_name,
            account_type='Arta Finance Brokerage',
            tax_status='taxable',
        )

        # Add holdings to account
        for h in all_holdings:
            asset_class, sector = classify_arta_ticker(h['ticker'], h['description'])

            # Calculate cost basis per share
            cost_per_share = h['cost_basis'] / h['quantity'] if h['quantity'] > 0 else h['price']

            holding = Holding(
                ticker=h['ticker'],
                shares=h['quantity'],
                cost_basis_per_share=cost_per_share,
                purchase_date=datetime(2024, 1, 1),  # Placeholder
                current_price=h['price'],
                asset_class=asset_class,
                sector=sector,
            )
            account.add_holding(holding)

        portfolio.add_account(account)
        return portfolio

    except Exception as e:
        print(f"Error parsing Arta Finance PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# EMPOWER 401K PDF PARSER
# =============================================================================
# LEARNING: Empower 401k statements show holdings table with:
# Fund Name | Beginning Balance | Deposits | Withdrawals | Ending Balance | Shares
# Tax status is tax_deferred (401k)
# =============================================================================

# Empower 401k fund classifications
EMPOWER_FUND_CLASSIFICATIONS = {
    'Target Date': ('Fund', 'Target Date'),
    'Bond': ('Bond', 'Fixed Income'),
    'Inflation': ('Bond', 'TIPS'),
    'Large Cap Value': ('Fund', 'US Large Cap Value'),
    'Large Cap Growth': ('Fund', 'US Large Cap Growth'),
    'S&P 500': ('Fund', 'US Large Cap'),
    'S&P MidCap': ('Fund', 'US Mid Cap'),
    'Small Cap': ('Fund', 'US Small Cap'),
    'International': ('Fund', 'International'),
    'Emerging': ('Fund', 'Emerging Markets'),
    'Stock Fund': ('Stock', 'Company Stock'),
}


def classify_empower_fund(fund_name: str) -> Tuple[str, str]:
    """Classify an Empower 401k fund into asset_class and sector."""
    fund_lower = fund_name.lower()

    for keyword, (asset_class, sector) in EMPOWER_FUND_CLASSIFICATIONS.items():
        if keyword.lower() in fund_lower:
            return (asset_class, sector)

    return ('Fund', 'Diversified')


def detect_empower_pdf(pdf_path: str) -> bool:
    """
    Check if a PDF is an Empower 401k statement.
    LEARNING: Empower statements have "Empower" and "401(K)" markers.
    """
    if not PDF_SUPPORT:
        return False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0].extract_text()
                if first_page:
                    has_empower = 'Empower' in first_page
                    has_401k = '401(K)' in first_page or '401(k)' in first_page or '401K' in first_page
                    return has_empower and has_401k
    except Exception:
        pass
    return False


def load_portfolio_from_empower_pdf(pdf_path: str, portfolio_name: str = "Empower 401k Portfolio") -> Optional[Portfolio]:
    """
    Load portfolio from an Empower 401k statement PDF.

    LEARNING: How this parser works:
    1. Looks for "How is my account invested?" section
    2. Parses fund holdings with format: FundName Beginning Deposits Withdrawals Ending Shares
    3. Creates a single 401k account with all holdings (tax_deferred status)

    Args:
        pdf_path: Path to the Empower PDF statement
        portfolio_name: Name for the portfolio

    Returns:
        Portfolio object with holdings, or None if parsing fails
    """
    if not PDF_SUPPORT:
        print("PDF support not available. Install pdfplumber: pip install pdfplumber")
        return None

    portfolio = Portfolio(portfolio_name=portfolio_name)
    all_holdings = []
    account_number = "empower_401k"
    account_name = "Empower 401k"
    plan_name = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract account info from first page
            first_page = pdf.pages[0].extract_text() or ''

            # Try to get participant ID
            id_match = re.search(r'Participant ID:\s*(\d+)', first_page)
            if id_match:
                account_number = id_match.group(1)

            # Try to get plan name
            plan_match = re.search(r'([A-Z][A-Z\s]+401\(K\)[^\n]+)', first_page)
            if plan_match:
                plan_name = plan_match.group(1).strip()
                account_name = f"401k - {plan_name[:30]}"

            # Detect format: Wells Fargo uses 6 columns, others use 5 columns
            is_wells_fargo_format = 'WELLS FARGO' in first_page.upper()

            # LEARNING: Holdings are on page 2 with format:
            # FundName Beginning Deposits/Changes Withdrawals Ending Shares
            # Example: Target Date 2040 Fund 78,297.22 14,643.17 -187.68 92,752.71 2,611.318
            # Some fund names span multiple lines (e.g., "Government\nInflation-Protected Bond\nFund")
            # Wells Fargo format has 6 columns: Beginning Deposits ChangeInValue Transfers Ending Shares

            # Pattern for fund holdings - fund name followed by 5 numbers
            # Matches: FundName Beginning Deposits Withdrawals Ending Shares
            holding_pattern = re.compile(
                r'^([A-Za-z][A-Za-z0-9\s&\-/\']+(?:Fund|Index))\s+'  # Fund name ending in Fund or Index
                r'([\d,]+\.\d{2})\s+'                                # Beginning balance
                r'-?([\d,]+\.\d{2})\s+'                              # Deposits/Changes
                r'-?([\d,]+\.\d{2})\s+'                              # Withdrawals
                r'([\d,]+\.\d{2})\s+'                                # Ending balance
                r'([\d,]+\.\d+)'                                     # Shares
            )

            # Alternative pattern for multi-line fund names that start with numbers on a line
            # Format: "Government 13,058.78 1,071.83 1,002.82 15,133.43 633.978"
            # Format: "Target Date 2040 Fund 78,297.22 14,643.17 -187.68 92,752.71 2,611.318"
            # Format: "S&P MidCap 400 Index 5,222.08 489.67 480.76 6,192.51 235.125"
            # where "Government" continues from "Inflation-Protected Bond\nFund" on next lines
            multi_line_pattern = re.compile(
                r'^([A-Za-z][A-Za-z0-9\s&\-]+)\s+'                    # Partial fund name (includes digits like 2040, 400)
                r'([\d,]+\.\d{2})\s+'                                # Beginning balance
                r'-?([\d,]+\.\d{2})\s+'                              # Deposits/Changes
                r'-?([\d,]+\.\d{2})\s+'                              # Withdrawals
                r'([\d,]+\.\d{2})\s+'                                # Ending balance
                r'([\d,]+\.\d+)'                                     # Shares
            )

            # Wells Fargo format: 6 columns with possible negative Transfers
            # Example: "Emerging Markets Equity 2,412.15 522.69 151.32 -96.29 2,989.87 147.042"
            # Example: "State Street S&P 500 Index 12,909.66 2,845.73 376.81 -176.71 15,955.49 1,340.910"
            # Columns: Beginning Deposits ChangeInValue Transfers Ending Shares
            wells_fargo_pattern = re.compile(
                r'^([A-Za-z][A-Za-z0-9\s&\-\']+?)\s+'                  # Fund name (includes digits like 500)
                r'([\d,]+\.\d{2})\s+'                                 # Beginning balance
                r'-?([\d,]+\.\d{2})\s+'                               # Deposits
                r'-?([\d,]+\.\d{2})\s+'                               # Change in Value
                r'-?([\d,]+\.\d{2})\s+'                               # Transfers (often negative)
                r'([\d,]+\.\d{2})\s+'                                 # Ending balance
                r'([\d,]+\.\d+)$'                                     # Shares
            )

            # Scan all pages for holdings
            for page in pdf.pages:
                text = page.extract_text() or ''

                # Look for holdings section
                if 'How is my account invested?' in text or ('Ending' in text and 'Balance' in text):
                    lines = text.split('\n')
                    pending_fund_parts = []  # For multi-line fund names

                    for i, line in enumerate(lines):
                        line = line.strip()

                        # Skip totals and headers
                        if line.startswith('Totals') or 'Beginning' in line or 'Dividends' in line:
                            continue
                        if 'How is my account' in line or 'Units/' in line:
                            continue

                        # Use format-specific pattern matching
                        if is_wells_fargo_format:
                            # Wells Fargo: 6 columns (Beginning Deposits Change Transfers Ending Shares)
                            wf_match = wells_fargo_pattern.match(line)
                            if wf_match:
                                partial_name = wf_match.group(1).strip()
                                # Check if the fund name is already complete (ends with Fund)
                                full_name = partial_name
                                if not full_name.endswith('Fund'):
                                    # Check if next lines complete the fund name
                                    for j in range(i + 1, min(i + 3, len(lines))):
                                        next_line = lines[j].strip()
                                        # Skip empty lines
                                        if not next_line:
                                            continue
                                        # Skip category headers like "LargeCapFunds", "InternationalFunds", "Bond", "Other"
                                        if next_line in ['Bond', 'Other'] or 'Funds' in next_line.replace(' ', ''):
                                            break
                                        # Stop at lines that look like data (contain many numbers with decimals)
                                        if sum(1 for c in next_line if c.isdigit()) > 10:
                                            break
                                        # This looks like part of a fund name continuation
                                        full_name += ' ' + next_line
                                        # Stop once we have the complete name (ends with Fund)
                                        if full_name.endswith('Fund') or next_line.endswith('M'):
                                            # Note: Wells Fargo has some funds ending in "NL Cl M"
                                            break

                                ending_balance = float(wf_match.group(6).replace(',', ''))  # 6th group is ending balance
                                shares = float(wf_match.group(7).replace(',', ''))  # 7th group is shares

                                if ending_balance > 0 and shares > 0:
                                    price_per_share = ending_balance / shares
                                    all_holdings.append({
                                        'ticker': full_name[:10].upper().replace(' ', ''),
                                        'description': full_name,
                                        'quantity': shares,
                                        'price': price_per_share,
                                        'value': ending_balance,
                                    })
                        else:
                            # JPMC and other formats: 5 columns (Beginning Deposits Withdrawals Ending Shares)
                            multi_match = multi_line_pattern.match(line)
                            if multi_match:
                                partial_name = multi_match.group(1).strip()
                                # Check if the fund name is already complete (ends with Fund)
                                # Note: "Index" alone is NOT complete - JPMC has "Index Fund" names
                                full_name = partial_name
                                if not full_name.endswith('Fund'):
                                    # Need to look at FOLLOWING lines to complete the fund name
                                    # Multi-line fund names have the continuation AFTER the data line
                                    # e.g., Line: "Government 13,058.78 ..."
                                    #       Next: "Inflation-Protected Bond"
                                    #       Next: "Fund"
                                    # Or:   Line: "Large Cap Value Index 17,941.56 ..."
                                    #       Next: "Fund"
                                    for j in range(i + 1, min(i + 4, len(lines))):
                                        next_line = lines[j].strip()
                                        # Skip empty lines
                                        if not next_line:
                                            continue
                                        # Stop at section headers or data lines
                                        if 'Totals' in next_line or 'How is' in next_line:
                                            break
                                        # Stop at lines that look like data (contain many numbers with decimals)
                                        if sum(1 for c in next_line if c.isdigit()) > 10:
                                            break
                                        # This looks like part of a fund name continuation
                                        full_name += ' ' + next_line
                                        # Stop once we have the complete name (ends with Fund)
                                        if full_name.endswith('Fund'):
                                            break

                                ending_balance = float(multi_match.group(5).replace(',', ''))
                                shares = float(multi_match.group(6).replace(',', ''))

                                if ending_balance > 0 and shares > 0:
                                    price_per_share = ending_balance / shares
                                    all_holdings.append({
                                        'ticker': full_name[:10].upper().replace(' ', ''),
                                        'description': full_name,
                                        'quantity': shares,
                                        'price': price_per_share,
                                        'value': ending_balance,
                                    })

        if not all_holdings:
            print(f"No holdings found in Empower PDF: {pdf_path}")
            return None

        # Create the 401k account (tax_deferred)
        account = Account(
            account_id=account_number,
            account_name=account_name,
            account_type='Empower 401k',
            tax_status='tax_deferred',  # 401k is tax-deferred!
        )

        # Add holdings to account
        for h in all_holdings:
            asset_class, sector = classify_empower_fund(h['description'])

            holding = Holding(
                ticker=h['ticker'],
                shares=h['quantity'],
                cost_basis_per_share=h['price'],  # Using current price as cost basis
                purchase_date=datetime(2024, 1, 1),  # Placeholder
                current_price=h['price'],
                asset_class=asset_class,
                sector=sector,
                description=h.get('description', ''),  # Full fund name from PDF
                cost_basis_estimated=True,  # No cost basis in Empower 401k statements
            )
            account.add_holding(holding)

        portfolio.add_account(account)
        return portfolio

    except Exception as e:
        print(f"Error parsing Empower PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================
# FIDELITY PDF PARSER
# ============================================

def detect_fidelity_pdf(pdf_path: str) -> bool:
    """
    Check if a PDF is a Fidelity Investment Report.
    Fidelity PDFs contain "INVESTMENT REPORT" and "Fidelity" on the first page.
    """
    if not PDF_SUPPORT:
        return False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0].extract_text() or ''
                # Check for Fidelity markers
                has_investment_report = 'INVESTMENT REPORT' in first_page
                has_fidelity = 'Fidelity' in first_page or 'fidelity.com' in first_page.lower()
                return has_investment_report and has_fidelity
    except Exception:
        pass
    return False


def parse_fidelity_holding_line(line: str) -> Optional[Dict]:
    """
    Parse a Fidelity holdings line.
    Format: DESCRIPTION (TICKER) begin_value quantity price end_value cost_basis gain_loss income

    Examples:
    NVIDIA CORPORATION COM (NVDA) $45,871.20 240.000 $177.1900 $42,525.60 $2,554.21 $39,971.39 $9.60
    NH PORTFOLIO 2030 (FIDELITY FUNDS) 100% $14,814.79 483.715 $31.9300 $15,445.02
    """
    # Skip header lines, total lines, and non-holding lines
    skip_patterns = [
        'Beginning', 'Market Value', 'Description', 'Total', 'Account #',
        'INVESTMENT REPORT', 'Holdings', 'Page', 'Core Account', 'Mutual Funds',
        'Exchange Traded', 'Stocks', 'Common Stock', 'Equity ETPs', 'Stock Funds',
        'EAI', 'Estimated', 'All positions', 'Includes exchange', 'of account',
        '% of account', 'Please note', 'Unrealized', 'Per Unit', 'Gain/Loss',
        '(continued)', 'account holdings', 'Feb 1', 'Feb 28', 'Cost Basis',
        'Brokerage services', 'Member NYSE', 'day yield', 'not applicable'
    ]

    for pattern in skip_patterns:
        if pattern in line:
            return None

    # Try to find ticker in parentheses - must be 2-5 uppercase letters
    ticker_match = re.search(r'\(([A-Z]{2,5})\)', line)
    if not ticker_match:
        return None

    ticker = ticker_match.group(1)

    # Skip if ticker looks like a date or code
    if ticker in ['SIPC', 'NFS', 'FBS', 'NYSE', 'ETF', 'ETN', 'MKT', 'COM', 'INC', 'CORP', 'DEL', 'CL']:
        return None

    # Extract description (everything before the ticker)
    description = line[:ticker_match.start()].strip()
    if not description or len(description) < 3:
        return None

    # Extract the part after ticker - this contains the numbers
    after_ticker = line[ticker_match.end():]

    # Fidelity format: begin_value quantity price end_value cost_basis gain_loss [income]
    # Pattern to match: $45,871.20 240.000 $177.1900 $42,525.60 $2,554.21 $39,971.39 $9.60
    # We need: quantity (no $), price ($xxx.xxxx), end_value ($xx,xxx.xx)

    # Find all numeric values with their position
    # Dollar amounts: $123,456.78 or -$123.45
    # Plain numbers: 240.000 (quantity usually 3 decimal places)

    dollar_pattern = r'-?\$[\d,]+\.?\d*'
    quantity_pattern = r'(?<!\$)\b\d+\.\d{3}\b'  # Number with exactly 3 decimal places, not preceded by $

    # Find quantity (no $ sign, has .XXX format)
    qty_match = re.search(quantity_pattern, after_ticker)
    if not qty_match:
        # Try to find any reasonable number that could be quantity
        qty_match = re.search(r'(?<!\$)\b(\d+\.\d+)\b', after_ticker)
        if not qty_match:
            return None

    quantity = float(qty_match.group().replace(',', ''))

    # Find all dollar amounts
    dollar_amounts = re.findall(dollar_pattern, after_ticker)
    clean_dollars = []
    for d in dollar_amounts:
        val = d.replace('$', '').replace(',', '').strip()
        if val and val != '-':
            try:
                clean_dollars.append(float(val))
            except ValueError:
                pass

    # We need at least begin_value and price (which comes after quantity)
    # Format: begin_value [%] quantity price end_value cost_basis gain_loss
    if len(clean_dollars) < 2:
        return None

    # Price is the dollar amount that appears AFTER the quantity in the string
    qty_pos = qty_match.end()
    after_qty = after_ticker[qty_pos:]

    price_match = re.search(dollar_pattern, after_qty)
    if not price_match:
        return None

    price = float(price_match.group().replace('$', '').replace(',', ''))

    # End value is the next dollar amount after price
    after_price = after_qty[price_match.end():]
    end_value_match = re.search(dollar_pattern, after_price)
    if end_value_match:
        end_value = float(end_value_match.group().replace('$', '').replace(',', ''))
    else:
        end_value = quantity * price

    # Cost basis is the next dollar amount
    cost_basis = end_value
    if end_value_match:
        after_end = after_price[end_value_match.end():]
        cost_match = re.search(dollar_pattern, after_end)
        if cost_match:
            cost_basis = float(cost_match.group().replace('$', '').replace(',', ''))

    # Sanity check: calculated value should be close to end_value
    calc_value = quantity * price
    if end_value > 0 and abs(calc_value - end_value) / end_value > 0.1:
        # Values don't match - might be parsing error
        # Use calculated value
        end_value = calc_value

    return {
        'ticker': ticker,
        'description': description,
        'shares': quantity,
        'price': price,
        'value': end_value,
        'cost_basis': cost_basis
    }


def load_portfolio_from_fidelity_pdf(pdf_path: str, portfolio_name: str = "Fidelity Portfolio") -> Optional[Portfolio]:
    """
    Load portfolio from a Fidelity Investment Report PDF.

    Supports:
    - Brokerage accounts (stocks, ETFs, mutual funds)
    - 529 Education accounts
    - IRA accounts

    LEARNING: Fidelity holdings can span multiple lines:
    - Single line: APPLE INC (AAPL) $2,386.43 9.197 $264.1800 ...
    - Multi-line: J P MORGAN EXCHANGE TRADED FD 2,808.12 47.251 58.0400 ...
                  NASDAQ EQT 10.580
                  PREM (JEPQ)
    The ticker in parentheses may appear on a later line.

    For 529 accounts:
    - Holdings format: NH PORTFOLIO 2030 (FIDELITY FUNDS) 100% $14,814.79 483.715 $31.9300 $15,445.02
    - No ticker symbol, use fund name as ticker

    Args:
        pdf_path: Path to the Fidelity PDF statement
        portfolio_name: Name for the portfolio

    Returns:
        Portfolio object or None if parsing fails
    """
    if not PDF_SUPPORT:
        print("PDF support not available. Install pdfplumber: pip install pdfplumber")
        return None

    portfolio = Portfolio(portfolio_name=portfolio_name)
    accounts_dict: Dict[str, Account] = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            current_account_id = None
            current_account_name = None
            current_tax_status = 'taxable'
            is_529_account = False

            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ''
                lines = text.split('\n')

                # Detect account headers first
                for line in lines:
                    line_clean = line.strip()

                    # Format: "Account # X66-769380" or "Account # 618-731045"
                    # Must have # to be a valid account line (excludes "Account Value", "Account Type")
                    account_match = re.search(r'Account #\s*([A-Z0-9-]+)', line_clean)
                    if account_match:
                        new_account_id = account_match.group(1)
                        # Only update if different account and looks like valid ID
                        if new_account_id != current_account_id and len(new_account_id) > 3:
                            current_account_id = new_account_id
                            # Reset account name when new account detected
                            if is_529_account:
                                current_account_name = 'Fidelity 529'

                    # Detect account type from headers
                    if 'FIDELITY ACCOUNT' in line_clean or 'JOINT TIC' in line_clean:
                        current_account_name = 'Fidelity Brokerage'
                        current_tax_status = 'taxable'
                        is_529_account = False
                    elif 'BENEFICIARY (529)' in line_clean:
                        # 529 account with beneficiary name
                        current_tax_status = 'tax_deferred'
                        is_529_account = True
                        # Extract beneficiary name: "Namasya Subramanian - BENEFICIARY (529)"
                        ben_match = re.search(r'^([A-Za-z]+\s+[A-Za-z]+)\s*-\s*BENEFICIARY', line_clean)
                        if ben_match:
                            current_account_name = f"529 - {ben_match.group(1).title()}"
                        else:
                            current_account_name = 'Fidelity 529'
                    elif 'EDUCATION ACCOUNT' in line_clean:
                        current_account_name = 'Fidelity 529'
                        current_tax_status = 'tax_deferred'
                        is_529_account = True
                    elif 'NH UNIQUE' in line_clean:
                        is_529_account = True
                    elif 'TRADITIONAL IRA' in line_clean:
                        current_account_name = 'Fidelity Traditional IRA'
                        current_tax_status = 'tax_deferred'
                        is_529_account = False
                    elif 'ROTH IRA' in line_clean:
                        current_account_name = 'Fidelity Roth IRA'
                        current_tax_status = 'tax_free'
                        is_529_account = False
                    elif 'ROLLOVER IRA' in line_clean:
                        current_account_name = 'Fidelity Rollover IRA'
                        current_tax_status = 'tax_deferred'
                        is_529_account = False

                # Parse holdings - use different parser for 529 accounts
                if is_529_account:
                    holdings = parse_fidelity_529_holdings(text)
                else:
                    holdings = parse_fidelity_holdings_from_page(text)

                for holding in holdings:
                    if not current_account_id:
                        continue

                    # Create account if doesn't exist
                    if current_account_id not in accounts_dict:
                        account = Account(
                            account_id=current_account_id,
                            account_name=current_account_name or 'Fidelity Account',
                            account_type=current_account_name or 'Brokerage',
                            tax_status=current_tax_status,
                        )
                        accounts_dict[current_account_id] = account

                    account = accounts_dict[current_account_id]

                    # Classify ticker
                    ticker = holding['ticker']
                    asset_class, sector = classify_fidelity_ticker(ticker, holding['description'])

                    # Create holding
                    new_holding = Holding(
                        ticker=ticker,
                        shares=holding['shares'],
                        cost_basis_per_share=holding['cost_basis'] / holding['shares'] if holding['shares'] > 0 else holding['price'],
                        purchase_date=datetime(2024, 1, 1),
                        current_price=holding['price'],
                        asset_class=asset_class,
                        sector=sector,
                        description=holding['description'],
                    )

                    # Avoid duplicates
                    existing_tickers = [h.ticker for h in account.holdings]
                    if ticker not in existing_tickers:
                        account.add_holding(new_holding)

                # GC every 5 pages
                if page_num > 0 and page_num % 5 == 0:
                    gc.collect()

        # Add accounts to portfolio
        for account in accounts_dict.values():
            if account.holdings:
                portfolio.add_account(account)

        return portfolio

    except Exception as e:
        print(f"Error parsing Fidelity PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def parse_fidelity_529_holdings(page_text: str) -> List[Dict]:
    """
    Parse holdings from a Fidelity 529 account page.

    Formats:
    - NH PORTFOLIO 2030 (FIDELITY FUNDS) 100% $14,814.79 483.715 $31.9300 $15,445.02
    - NH PORTFOLIO 2036 (FIDELITY BLEND) 100% $15,734.41 844.332 $19.3800 $16,363.15
    Pattern: Description (FIDELITY FUNDS/BLEND) Percent BeginValue Quantity Price EndValue

    Returns:
        List of holding dicts
    """
    holdings = []
    lines = page_text.split('\n')

    for line in lines:
        line = line.strip()

        # Look for NH PORTFOLIO lines - these are 529 target date funds
        # Support both FIDELITY FUNDS and FIDELITY BLEND variants
        if 'NH PORTFOLIO' in line and ('FIDELITY FUNDS' in line or 'FIDELITY BLEND' in line):
            # Extract fund name (e.g., "NH PORTFOLIO 2030" or "NH PORTFOLIO 2036")
            fund_match = re.search(r'(NH PORTFOLIO \d+)', line)
            if not fund_match:
                continue

            fund_name = fund_match.group(1)

            # Create ticker from fund name (e.g., "NH2030")
            year_match = re.search(r'\d+', fund_name)
            ticker = f"NH{year_match.group()}" if year_match else "NH529"

            # Extract numbers: look for pattern Percent BeginValue Quantity Price EndValue
            # Pattern: 100% $14,814.79 483.715 $31.9300 $15,445.02
            numbers = re.findall(r'\$?([\d,]+\.\d+)', line)
            if len(numbers) < 4:
                continue

            try:
                # Numbers are: begin_value, quantity, price, end_value
                quantity = float(numbers[1].replace(',', ''))  # 483.715
                price = float(numbers[2].replace(',', ''))     # 31.9300
                end_value = float(numbers[3].replace(',', '')) # 15,445.02

                # Verify calculation
                calc_value = quantity * price
                if abs(calc_value - end_value) > end_value * 0.05:
                    # Values don't match, skip
                    continue

                holdings.append({
                    'ticker': ticker,
                    'description': fund_name,
                    'shares': quantity,
                    'price': price,
                    'value': end_value,
                    'cost_basis': end_value  # No cost basis in 529 statements
                })
            except (ValueError, IndexError):
                continue

    return holdings


def parse_fidelity_holdings_from_page(page_text: str) -> List[Dict]:
    """
    Parse holdings from a Fidelity page.

    LEARNING: Fidelity has two formats:
    1. Stocks (single line): DESCRIPTION (TICKER) $begin qty $price $end ...
       Example: APPLE INC (AAPL) $2,386.43 9.197 $264.1800 $2,429.66 ...
    2. ETFs (multi-line): DESCRIPTION begin qty price end ... then more lines with (TICKER)
       Example: J P MORGAN EXCHANGE TRADED FD 2,808.12 47.251 58.0400 ...
                NASDAQ EQT 10.580
                PREM (JEPQ)

    Note: Stocks have $ before begin value, ETFs don't always have $

    Args:
        page_text: Full text of one PDF page

    Returns:
        List of holding dicts with ticker, shares, price, value, cost_basis
    """
    holdings = []
    lines = page_text.split('\n')

    # Skip patterns - lines containing these are headers/footers
    skip_patterns = [
        'Beginning', 'Market Value', 'Description', 'Account #',
        'INVESTMENT REPORT', 'Page', 'Feb 1', 'Feb 28',
        'Brokerage services', 'Member NYSE', 'EAI', 'Estimated',
        'Cost Basis', 'Per Unit', 'Gain/Loss', '% of account',
        'of account holdings', 'continued', 'GANAPATHI', 'JOINT TIC',
        'Equity ETPs', 'Common Stock', 'Exchange Traded', 'Stocks',
        'Mutual Funds', 'Stock Funds', 'Core Account', 'Holdings',
        'FIDELITY ACCOUNT', 'EDUCATION'
    ]

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty or header/footer lines
        if not line or line.startswith('Total') or any(skip in line for skip in skip_patterns):
            i += 1
            continue

        # Skip page numbers like "4 of 10"
        if re.match(r'^\d+ of \d+$', line):
            i += 1
            continue

        # Look for holding patterns - need either:
        # 1. Ticker on this line with $ values: DESC (TICKER) $val qty $price ...
        # 2. Data line with numbers, ticker on later line

        # Check for ticker on this line
        ticker_match = re.search(r'\(([A-Z]{2,5})\)', line)

        if ticker_match:
            ticker = ticker_match.group(1)

            # Skip invalid tickers
            if ticker in ['SIPC', 'NFS', 'FBS', 'NYSE', 'ETN', 'MKT']:
                i += 1
                continue

            # This is a single-line holding (stocks format)
            # Format: DESCRIPTION (TICKER) $begin qty $price $end $cost $gain ...
            # Extract values after ticker
            after_ticker = line[ticker_match.end():]

            # Find quantity (3 decimal places, no $)
            qty_match = re.search(r'(?<!\$)\b(\d+\.\d{3})\b', after_ticker)
            if not qty_match:
                # Try 2 decimal places
                qty_match = re.search(r'(?<!\$)\b(\d+\.\d{2})\b', after_ticker)
            if not qty_match:
                i += 1
                continue

            quantity = float(qty_match.group(1))

            # Find price (usually 4 decimal places with $)
            price_match = re.search(r'\$?([\d,]+\.\d{4})', after_ticker)
            if not price_match:
                # Try 2 decimal places
                price_match = re.search(r'\$?([\d,]+\.\d{2})', after_ticker[qty_match.end():])
            if not price_match:
                i += 1
                continue

            price = float(price_match.group(1).replace(',', ''))

            # Calculate value
            end_value = quantity * price

            # Get cost basis - usually the 4th or 5th number after ticker
            dollar_amounts = re.findall(r'\$?([\d,]+\.\d{2})', after_ticker)
            cost_basis = end_value
            if len(dollar_amounts) >= 4:
                try:
                    cost_basis = float(dollar_amounts[3].replace(',', ''))
                except:
                    pass

            # Description is before ticker
            description = line[:ticker_match.start()].strip()

            holdings.append({
                'ticker': ticker,
                'description': description,
                'shares': quantity,
                'price': price,
                'value': end_value,
                'cost_basis': cost_basis
            })
            i += 1

        else:
            # No ticker on this line - check if it's a multi-line ETF entry
            # ETF format: DESC begin qty price end cost gain income
            #             continuation
            #             more (TICKER)

            # Must have multiple numbers to be a data line
            numbers = re.findall(r'[\d,]+\.\d+', line)
            if len(numbers) < 4:
                i += 1
                continue

            # Check next 3 lines for ticker
            ticker = None
            ticker_offset = 0
            for j in range(1, 4):
                if i + j >= len(lines):
                    break
                next_line = lines[i + j].strip()
                next_ticker_match = re.search(r'\(([A-Z]{2,5})\)', next_line)
                if next_ticker_match:
                    ticker = next_ticker_match.group(1)
                    ticker_offset = j
                    break

            if not ticker or ticker in ['SIPC', 'NFS', 'FBS', 'NYSE', 'ETN', 'MKT']:
                i += 1
                continue

            # Parse the data line
            # Format: DESC begin qty price end cost gain [income]
            # Numbers in order: begin(skip), qty, price, end(skip), cost, gain, [income]

            # Find quantity (usually 3 decimal places)
            qty_match = re.search(r'(?<!\d)([\d,]+\.\d{3})(?!\d)', line)
            if not qty_match:
                i += 1
                continue

            quantity = float(qty_match.group(1).replace(',', ''))

            # Find price (4 decimal places, right after quantity)
            qty_end = qty_match.end()
            after_qty = line[qty_end:]
            price_match = re.search(r'([\d,]+\.\d{4})', after_qty)
            if not price_match:
                # Try 2 decimal places
                price_match = re.search(r'([\d,]+\.\d{2})', after_qty)
            if not price_match:
                i += 1
                continue

            price = float(price_match.group(1).replace(',', ''))

            # End value is the next number after price
            end_value = quantity * price
            price_end = qty_end + price_match.end()
            after_price = line[price_end:]
            end_match = re.search(r'([\d,]+\.\d{2})', after_price)
            if end_match:
                end_value = float(end_match.group(1).replace(',', ''))

            # Cost basis is the next number
            cost_basis = end_value
            if end_match:
                after_end = after_price[end_match.end():]
                cost_match = re.search(r'([\d,]+\.\d{2})', after_end)
                if cost_match:
                    cost_basis = float(cost_match.group(1).replace(',', ''))

            # Build description from current line + continuation lines
            # Description is text before the first number
            first_num = re.search(r'[\d,]+\.\d', line)
            desc_parts = []
            if first_num:
                desc_parts.append(line[:first_num.start()].strip())

            # Add continuation lines (before ticker line)
            for j in range(1, ticker_offset + 1):
                if i + j < len(lines):
                    cont_line = lines[i + j].strip()
                    # Remove ticker from ticker line
                    cont_line = re.sub(r'\([A-Z]{2,5}\)', '', cont_line)
                    # Remove numbers
                    cont_line = re.sub(r'[\d,]+\.\d+', '', cont_line).strip()
                    if cont_line:
                        desc_parts.append(cont_line)

            description = ' '.join(desc_parts)
            description = re.sub(r'\s+', ' ', description).strip()

            holdings.append({
                'ticker': ticker,
                'description': description,
                'shares': quantity,
                'price': price,
                'value': end_value,
                'cost_basis': cost_basis
            })

            # Skip past processed lines
            i += ticker_offset + 1

    return holdings


def classify_fidelity_ticker(ticker: str, description: str = "") -> Tuple[str, str]:
    """Classify Fidelity holdings by ticker and description."""
    desc_lower = description.lower()
    ticker_upper = ticker.upper()

    # 529 Portfolio funds
    if 'NH PORTFOLIO' in description or '529' in description or 'PORTFOLIO 20' in description:
        return ('Target Date Fund', 'Education Savings')

    # Money market
    if 'MONEY MARKET' in description or ticker in ['FZFXX', 'SPAXX', 'FDRXX']:
        return ('Cash', 'Money Market')

    # Fidelity mutual funds
    fidelity_funds = {
        'FXAIX': ('Mutual Fund', 'US Large Cap'),
        'FSRPX': ('Mutual Fund', 'Consumer'),
        'MIOPX': ('Mutual Fund', 'International'),
        'FSKAX': ('Mutual Fund', 'US Total Market'),
        'FTBFX': ('Mutual Fund', 'Fixed Income'),
    }
    if ticker in fidelity_funds:
        return fidelity_funds[ticker]

    # ETFs
    etfs = {
        'PAVE': ('ETF', 'Infrastructure'),
        'IEFA': ('ETF', 'International Developed'),
        'JEPQ': ('ETF', 'Technology'),
        'VWO': ('ETF', 'Emerging Markets'),
        'VOO': ('ETF', 'US Large Cap'),
        'VTI': ('ETF', 'US Total Market'),
    }
    if ticker in etfs:
        return etfs[ticker]

    # Stocks by sector
    tech_stocks = ['NVDA', 'AAPL', 'MSFT', 'AMD', 'AVGO', 'MRVL', 'SMCI', 'GOOGL', 'GOOG']
    if ticker in tech_stocks:
        return ('Stock', 'Technology')

    finance_stocks = ['JPM', 'BAC', 'IBKR', 'HOOD', 'V', 'MA']
    if ticker in finance_stocks:
        return ('Stock', 'Financials')

    consumer_stocks = ['AMZN', 'TSLA', 'UBER']
    if ticker in consumer_stocks:
        return ('Stock', 'Consumer')

    industrial_stocks = ['DE', 'CAT', 'HON']
    if ticker in industrial_stocks:
        return ('Stock', 'Industrial')

    healthcare_stocks = ['JNJ', 'PFE', 'UNH', 'ABBV']
    if ticker in healthcare_stocks:
        return ('Stock', 'Healthcare')

    # Default based on description
    if 'ETF' in description or 'FUND' in description:
        return ('ETF', 'Diversified')
    if 'COM' in description or 'INC' in description or 'CORP' in description:
        return ('Stock', 'Other')

    return ('Other', 'Other')


def load_portfolio_from_pdf(pdf_path: str, portfolio_name: str = "My Portfolio") -> Optional[Portfolio]:
    """
    Load portfolio from a PDF file.
    Auto-detects the PDF format and uses appropriate parser.

    LEARNING: This is the main entry point for PDF parsing.
    It uses "duck typing" - it checks what the PDF looks like to determine the parser.

    Args:
        pdf_path: Path to the PDF file
        portfolio_name: Name for the portfolio

    Returns:
        Portfolio object or None if parsing fails
    """
    if not PDF_SUPPORT:
        print("PDF support not available. Install pdfplumber: pip install pdfplumber")
        return None

    result = None

    try:
        # Detect PDF type and use appropriate parser
        # LEARNING: Order matters - check most specific formats first
        # NOTE: Each detection opens and closes the PDF, so we force gc between checks
        # to keep memory usage low on limited-memory servers

        if detect_titan_pdf(pdf_path):
            gc.collect()
            print(f"Detected Titan/Apex Clearing PDF format")
            result = load_portfolio_from_titan_pdf(pdf_path, portfolio_name)
            gc.collect()
            return result

        gc.collect()

        if detect_betterment_pdf(pdf_path):
            gc.collect()
            print(f"Detected Betterment PDF format")
            result = load_portfolio_from_betterment_pdf(pdf_path, portfolio_name)
            gc.collect()
            return result

        gc.collect()

        if detect_acorns_pdf(pdf_path):
            gc.collect()
            print(f"Detected Acorns PDF format")
            result = load_portfolio_from_acorns_pdf(pdf_path, portfolio_name)
            gc.collect()
            return result

        gc.collect()

        if detect_arta_pdf(pdf_path):
            gc.collect()
            print(f"Detected Arta Finance PDF format")
            result = load_portfolio_from_arta_pdf(pdf_path, portfolio_name)
            gc.collect()
            return result

        gc.collect()

        if detect_empower_pdf(pdf_path):
            gc.collect()
            print(f"Detected Empower 401k PDF format")
            result = load_portfolio_from_empower_pdf(pdf_path, portfolio_name)
            gc.collect()
            return result

        gc.collect()

        if detect_fidelity_pdf(pdf_path):
            gc.collect()
            print(f"Detected Fidelity Investment Report PDF format")
            result = load_portfolio_from_fidelity_pdf(pdf_path, portfolio_name)
            gc.collect()
            return result

        print(f"Unknown PDF format: {pdf_path}")
        return None

    finally:
        # Always force garbage collection after PDF processing
        gc.collect()

import csv
import yaml
import re
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from ..models import Portfolio, Account, Holding


# Mapping of common tickers to their asset class and sector
TICKER_CLASSIFICATIONS = {
    # ETFs - Broad Market
    'VTI': ('ETF', 'Diversified'),
    'VOO': ('ETF', 'Diversified'),
    'FXAIX': ('Mutual Fund', 'Diversified'),
    'SPY': ('ETF', 'Diversified'),
    'IVV': ('ETF', 'Diversified'),
    'VT': ('ETF', 'Diversified'),

    # ETFs - International
    'VXUS': ('ETF', 'International'),
    'VWO': ('ETF', 'International'),
    'IEFA': ('ETF', 'International'),
    'EFA': ('ETF', 'International'),
    'MIOPX': ('Mutual Fund', 'International'),

    # ETFs - Bonds
    'BND': ('Bond', 'Fixed Income'),
    'AGG': ('Bond', 'Fixed Income'),
    'BNDX': ('Bond', 'Fixed Income'),

    # ETFs - Sector/Thematic
    'PAVE': ('ETF', 'Infrastructure'),
    'JEPQ': ('ETF', 'Technology'),
    'FSRPX': ('Mutual Fund', 'Consumer'),
    'VNQ': ('ETF', 'Real Estate'),
    'GLD': ('ETF', 'Commodities'),
    'VYM': ('ETF', 'Dividends'),

    # Technology Stocks
    'NVDA': ('Stock', 'Technology'),
    'AAPL': ('Stock', 'Technology'),
    'MSFT': ('Stock', 'Technology'),
    'GOOGL': ('Stock', 'Technology'),
    'GOOG': ('Stock', 'Technology'),
    'AMD': ('Stock', 'Technology'),
    'AVGO': ('Stock', 'Technology'),
    'MRVL': ('Stock', 'Technology'),
    'SMCI': ('Stock', 'Technology'),
    'INTC': ('Stock', 'Technology'),

    # Consumer/E-commerce
    'AMZN': ('Stock', 'Consumer'),
    'TSLA': ('Stock', 'Consumer'),
    'UBER': ('Stock', 'Technology'),
    'HOOD': ('Stock', 'Financials'),

    # Financials
    'JPM': ('Stock', 'Financials'),
    'BAC': ('Stock', 'Financials'),
    'IBKR': ('Stock', 'Financials'),
    'BRK.B': ('Stock', 'Financials'),
    'V': ('Stock', 'Financials'),
    'MA': ('Stock', 'Financials'),

    # Healthcare
    'JNJ': ('Stock', 'Healthcare'),
    'PFE': ('Stock', 'Healthcare'),
    'UNH': ('Stock', 'Healthcare'),
    'ABBV': ('Stock', 'Healthcare'),

    # Industrial
    'DE': ('Stock', 'Industrial'),
    'CAT': ('Stock', 'Industrial'),
    'HON': ('Stock', 'Industrial'),

    # Energy
    'XOM': ('Stock', 'Energy'),
    'CVX': ('Stock', 'Energy'),
}


def classify_ticker(ticker: str, description: str = "") -> tuple:
    """
    Classify a ticker into asset_class and sector.
    Returns (asset_class, sector) tuple.
    """
    # Check our known classifications first
    if ticker in TICKER_CLASSIFICATIONS:
        return TICKER_CLASSIFICATIONS[ticker]

    # Try to infer from description
    desc_lower = description.lower() if description else ""

    # Check for target date funds (common in 401k/custodial accounts)
    if 'portfolio' in desc_lower and any(year in desc_lower for year in ['2025', '2030', '2035', '2036', '2040', '2045', '2050', '2055', '2060']):
        return ('Target Date Fund', 'Diversified')

    # Check for money market
    if 'money market' in desc_lower or ticker.endswith('XX'):
        return ('Cash', 'Money Market')

    # Check for ETF patterns
    if 'etf' in desc_lower or 'ishares' in desc_lower or 'vanguard' in desc_lower:
        return ('ETF', 'Diversified')

    # Check for mutual funds
    if 'fund' in desc_lower or 'fidelity' in desc_lower:
        return ('Mutual Fund', 'Diversified')

    # Default to Stock
    return ('Stock', 'Other')


def determine_tax_status(account_name: str) -> str:
    """
    Determine tax status based on account name.
    Returns: 'taxable', 'tax_deferred', or 'tax_free'
    """
    name_lower = account_name.lower()

    # Tax-free accounts
    if 'roth' in name_lower:
        return 'tax_free'
    if 'hsa' in name_lower:
        return 'tax_free'

    # Tax-deferred accounts
    if '401k' in name_lower or '401(k)' in name_lower:
        return 'tax_deferred'
    if 'traditional ira' in name_lower or 'ira' in name_lower:
        return 'tax_deferred'
    if '403b' in name_lower or '403(b)' in name_lower:
        return 'tax_deferred'
    if '457' in name_lower:
        return 'tax_deferred'

    # Custodial accounts (UGMA/UTMA) are taxable
    # Target date funds in custodial accounts are typically taxable

    # Default to taxable (brokerage, joint, individual, custodial)
    return 'taxable'


def detect_csv_format(csv_file: str) -> str:
    """
    Detect whether the CSV is in Fidelity format or standard format.
    Returns: 'fidelity', 'fidelity_summary' (skip), or 'standard'
    """
    with open(csv_file, 'r') as f:
        first_line = f.readline()

        # Fidelity positions format has 'Account Number' as first column
        if 'Account Number' in first_line:
            # Check if it has the detailed columns we need
            if 'Symbol' in first_line and 'Quantity' in first_line:
                return 'fidelity'
            else:
                return 'fidelity_summary'  # Summary file without position details

        # Fidelity summary statement format (different header)
        if 'Account Type' in first_line and 'Beginning mkt Value' in first_line:
            return 'fidelity_summary'

        # Standard format has 'account_id' as first column
        if 'account_id' in first_line:
            return 'standard'

        # Try to auto-detect based on other columns
        if 'Last Price' in first_line or 'Current Value' in first_line:
            return 'fidelity'

        return 'standard'


def load_portfolio_from_fidelity_csv(csv_file: str, portfolio_name: str = "My Portfolio") -> Portfolio:
    """Load portfolio data from a Fidelity CSV export file"""
    portfolio = Portfolio(portfolio_name=portfolio_name)
    accounts_dict = {}

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip empty rows or disclaimer rows
            account_id = row.get('Account Number', '').strip()
            if not account_id or account_id.startswith('"') or account_id.startswith('The data'):
                continue

            symbol = row.get('Symbol', '').strip()
            # Skip rows without symbols or with special markers
            if not symbol or symbol == '**' or '--' in str(row.get('Last Price', '')):
                continue

            # Skip money market holdings (they're just cash)
            if symbol.endswith('**') or 'MONEY MARKET' in row.get('Description', '').upper():
                continue

            # Get values, handling potential formatting issues
            try:
                quantity_str = row.get('Quantity', '0').replace(',', '')
                quantity = float(quantity_str) if quantity_str and quantity_str != '--' else 0

                price_str = row.get('Last Price', '0').replace('$', '').replace(',', '')
                current_price = float(price_str) if price_str and price_str != '--' else 0

                cost_basis_str = row.get('Cost Basis Total', '0').replace('$', '').replace(',', '')
                cost_basis_total = float(cost_basis_str) if cost_basis_str and cost_basis_str != '--' else 0

                # Skip if no meaningful data
                if quantity == 0 or current_price == 0:
                    continue

            except (ValueError, TypeError):
                continue

            account_name = row.get('Account Name', 'Unknown Account').strip()
            description = row.get('Description', '').strip()

            # Create account if it doesn't exist
            if account_id not in accounts_dict:
                tax_status = determine_tax_status(account_name)
                account = Account(
                    account_id=account_id,
                    account_name=account_name,
                    account_type=account_name,  # Use name as type for Fidelity
                    tax_status=tax_status,
                )
                accounts_dict[account_id] = account
                portfolio.add_account(account)
            else:
                account = accounts_dict[account_id]

            # Calculate cost basis per share
            cost_basis_per_share = cost_basis_total / quantity if quantity > 0 else current_price

            # Classify the ticker
            asset_class, sector = classify_ticker(symbol, description)

            # Create holding
            # Note: Fidelity doesn't provide purchase date, so we use a placeholder
            holding = Holding(
                ticker=symbol,
                shares=quantity,
                cost_basis_per_share=cost_basis_per_share,
                purchase_date=datetime(2024, 1, 1),  # Placeholder - Fidelity doesn't provide this
                current_price=current_price,
                asset_class=asset_class,
                sector=sector,
            )

            account.add_holding(holding)

    return portfolio


def load_portfolio_from_csv(csv_file: str, portfolio_name: str = "My Portfolio") -> Optional[Portfolio]:
    """
    Load portfolio data from a CSV file.
    Auto-detects format (Fidelity or standard) and uses appropriate parser.
    Returns None for files that can't be parsed (like summary statements).
    """
    csv_format = detect_csv_format(csv_file)

    if csv_format == 'fidelity':
        print(f"Detected Fidelity CSV format")
        return load_portfolio_from_fidelity_csv(csv_file, portfolio_name)
    elif csv_format == 'fidelity_summary':
        print(f"Skipping {csv_file} (Fidelity summary statement without position details)")
        return None
    else:
        return load_portfolio_from_standard_csv(csv_file, portfolio_name)


def load_portfolio_from_standard_csv(csv_file: str, portfolio_name: str = "My Portfolio") -> Portfolio:
    """Load portfolio data from a standard format CSV file"""
    portfolio = Portfolio(portfolio_name=portfolio_name)
    accounts_dict = {}

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            account_id = row['account_id']

            # Create account if it doesn't exist
            if account_id not in accounts_dict:
                account = Account(
                    account_id=account_id,
                    account_name=row['account_name'],
                    account_type=row['account_type'],
                    tax_status=row['tax_status'],
                )
                accounts_dict[account_id] = account
                portfolio.add_account(account)
            else:
                account = accounts_dict[account_id]

            # Create holding
            holding = Holding(
                ticker=row['ticker'],
                shares=float(row['shares']),
                cost_basis_per_share=float(row['cost_basis_per_share']),
                purchase_date=datetime.strptime(row['purchase_date'], '%Y-%m-%d'),
                current_price=float(row['current_price']),
                asset_class=row['asset_class'],
                sector=row['sector'],
            )

            account.add_holding(holding)

    return portfolio


def extract_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Try to extract a date from a filename.
    Supports formats like:
    - Portfolio_Positions_Jan-22-2026.csv
    - Portfolio_Positions_2026-01-22.csv
    - statement_01-22-2026.csv
    """
    basename = Path(filename).stem

    # Try pattern: Mon-DD-YYYY (e.g., Jan-22-2026)
    month_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{1,2})-(\d{4})'
    match = re.search(month_pattern, basename, re.IGNORECASE)
    if match:
        month_str, day, year = match.groups()
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        month = month_map.get(month_str.lower(), 1)
        return datetime(int(year), month, int(day))

    # Try pattern: YYYY-MM-DD
    iso_pattern = r'(\d{4})-(\d{2})-(\d{2})'
    match = re.search(iso_pattern, basename)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))

    # Try pattern: MM-DD-YYYY
    us_pattern = r'(\d{2})-(\d{2})-(\d{4})'
    match = re.search(us_pattern, basename)
    if match:
        month, day, year = match.groups()
        return datetime(int(year), int(month), int(day))

    # Fall back to file modification time
    try:
        mtime = os.path.getmtime(filename)
        return datetime.fromtimestamp(mtime)
    except:
        return datetime.now()


def load_portfolio_from_multiple_sources(
    file_paths: List[str],
    portfolio_name: str = "My Portfolio"
) -> Portfolio:
    """
    Load and merge portfolio data from multiple CSV files.
    When the same holding appears in multiple files, keeps the one from the most recent file.

    Args:
        file_paths: List of paths to CSV files
        portfolio_name: Name for the combined portfolio

    Returns:
        Merged Portfolio object with deduplicated holdings
    """
    # Sort files by date (newest last so they overwrite older data)
    files_with_dates = []
    for fp in file_paths:
        file_date = extract_date_from_filename(fp)
        files_with_dates.append((fp, file_date))

    files_with_dates.sort(key=lambda x: x[1])

    print(f"Processing files in chronological order:")
    for fp, date in files_with_dates:
        print(f"  {Path(fp).name}: {date.strftime('%Y-%m-%d')}")

    # Create the merged portfolio
    merged_portfolio = Portfolio(portfolio_name=portfolio_name)
    accounts_dict: Dict[str, Account] = {}
    # Track holdings by (account_id, ticker) -> (holding, file_date)
    holdings_tracker: Dict[tuple, tuple] = {}

    for file_path, file_date in files_with_dates:
        # Load portfolio from this file
        temp_portfolio = load_portfolio_from_csv(file_path, "temp")

        # Skip files that couldn't be parsed
        if temp_portfolio is None:
            continue

        for account in temp_portfolio.accounts:
            account_id = account.account_id

            # Create or get account
            if account_id not in accounts_dict:
                new_account = Account(
                    account_id=account.account_id,
                    account_name=account.account_name,
                    account_type=account.account_type,
                    tax_status=account.tax_status,
                )
                accounts_dict[account_id] = new_account

            # Process holdings
            for holding in account.holdings:
                key = (account_id, holding.ticker)
                # Always overwrite with newer data (files are sorted oldest first)
                holdings_tracker[key] = (holding, file_date, account_id)

    # Now build the final portfolio with deduplicated holdings
    for (account_id, ticker), (holding, file_date, acc_id) in holdings_tracker.items():
        if account_id in accounts_dict:
            accounts_dict[account_id].add_holding(holding)

    # Add all accounts to portfolio
    for account in accounts_dict.values():
        if account.holdings:  # Only add accounts that have holdings
            merged_portfolio.add_account(account)

    return merged_portfolio


def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_file}")
        print("Using default configuration.")
        return {}

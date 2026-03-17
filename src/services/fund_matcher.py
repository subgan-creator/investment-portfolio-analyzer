"""
Fund Matcher Service - Matches portfolio holdings to stored fund profiles.

Used to enable look-through analysis for target date funds and other composite investments.
"""
import re
from typing import Dict, List, Any, Optional, Tuple

from src.models.fund_profile import find_matching_profile, get_all_fund_profiles, FundProfile


def match_holding_to_profile(
    ticker: str,
    description: str = '',
    account_type: str = ''
) -> Optional[Dict[str, Any]]:
    """
    Match a single holding to a fund profile.

    Args:
        ticker: The ticker symbol or fund code
        description: Full fund name/description (e.g., "Target Date 2045 Fund")
        account_type: Account type which may contain source info (e.g., "Empower 401k")

    Returns:
        Fund profile dict if matched, None otherwise
    """
    # Extract source from account type
    source = extract_source_from_account_type(account_type)

    # First try matching by description (full fund name)
    if description:
        profile = find_matching_profile(description, source)
        if profile:
            return profile.to_dict()

    # Try matching by ticker
    profile = find_matching_profile(ticker, source)
    if profile:
        return profile.to_dict()

    # Try fuzzy matching for target date funds
    target_year = extract_target_year(ticker, description)
    if target_year:
        profile = find_profile_by_target_year(target_year, source)
        if profile:
            return profile.to_dict()

    return None


def extract_source_from_account_type(account_type: str) -> Optional[str]:
    """Extract the source/brokerage from account type string."""
    if not account_type:
        return None

    account_type_lower = account_type.lower()

    if 'jpmc' in account_type_lower or 'jpmorgan' in account_type_lower:
        return 'JPMC Empower'
    elif 'wells' in account_type_lower and 'fargo' in account_type_lower:
        return 'Wells Fargo Empower'
    elif 'empower' in account_type_lower:
        return 'JPMC Empower'  # Default to JPMC if just "Empower"
    elif 'fidelity' in account_type_lower:
        return 'Fidelity'
    elif 'vanguard' in account_type_lower:
        return 'Vanguard'
    elif 'schwab' in account_type_lower:
        return 'Schwab'

    return None


def extract_target_year(ticker: str, description: str = '') -> Optional[int]:
    """Extract target year from ticker or description."""
    # Combine ticker and description for searching
    search_text = f"{ticker} {description}".upper()

    # Pattern: "2045", "TARGET 2045", "RETIRE 2045", etc.
    year_match = re.search(r'(?:TARGET|RETIRE|TGT|RET|DATE)?\s*(\d{4})', search_text)
    if year_match:
        year = int(year_match.group(1))
        # Validate it's a reasonable target date year
        if 2020 <= year <= 2070:
            return year

    # Try just finding a 4-digit year that looks like a target date
    year_match = re.search(r'\b(20[234567]\d)\b', search_text)
    if year_match:
        return int(year_match.group(1))

    return None


def find_profile_by_target_year(target_year: int, source: Optional[str] = None) -> Optional[FundProfile]:
    """Find a fund profile by target year."""
    from src.models.fund_profile import SessionLocal, FundProfile

    db = SessionLocal()
    try:
        query = db.query(FundProfile).filter(FundProfile.target_year == target_year)
        if source:
            # Try with source first
            profile = query.filter(FundProfile.source == source).first()
            if profile:
                return profile
            # Fall back to any source
            return db.query(FundProfile).filter(FundProfile.target_year == target_year).first()
        return query.first()
    finally:
        db.close()


def apply_look_through_analysis(
    holdings: List[Dict[str, Any]],
    account_type: str = ''
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Apply look-through analysis to a list of holdings.

    For each holding that matches a fund profile, expand it into its
    underlying asset allocation.

    Args:
        holdings: List of holding dictionaries with keys: ticker, description, market_value
        account_type: Account type string for source matching

    Returns:
        Tuple of:
        - List of expanded holdings (original holdings that didn't match, plus
          synthetic holdings representing the look-through allocation)
        - Summary dict with info about which holdings were expanded
    """
    expanded_holdings = []
    match_summary = {
        'matched_holdings': [],
        'unmatched_holdings': [],
        'total_look_through_value': 0,
    }

    for holding in holdings:
        ticker = holding.get('ticker', '')
        description = holding.get('description', '')
        market_value = holding.get('market_value', 0)

        # Try to match to a fund profile
        profile = match_holding_to_profile(ticker, description, account_type)

        if profile:
            # This holding can be expanded
            match_summary['matched_holdings'].append({
                'ticker': ticker,
                'description': description,
                'market_value': market_value,
                'matched_fund': profile['fund_name'],
            })
            match_summary['total_look_through_value'] += market_value

            # Create synthetic holdings for each asset class
            asset_allocation = profile.get('asset_allocation', {})
            for asset_class, percentage in asset_allocation.items():
                if percentage > 0:
                    expanded_holdings.append({
                        'ticker': f"{ticker}__{asset_class}",
                        'description': f"{profile['fund_name']} - {asset_class.replace('_', ' ').title()}",
                        'market_value': market_value * (percentage / 100),
                        'asset_class': map_allocation_to_asset_class(asset_class),
                        'sector': map_allocation_to_sector(asset_class),
                        'is_look_through': True,
                        'source_fund': profile['fund_name'],
                        'source_ticker': ticker,
                    })
        else:
            # Keep original holding
            match_summary['unmatched_holdings'].append({
                'ticker': ticker,
                'description': description,
            })
            expanded_holdings.append({
                **holding,
                'is_look_through': False,
            })

    return expanded_holdings, match_summary


def map_allocation_to_asset_class(allocation_key: str) -> str:
    """Map fund profile allocation key to standard asset class."""
    equity_allocations = {
        'us_large_cap', 'us_mid_cap', 'us_small_cap',
        'international', 'emerging_markets_equity', 'reits'
    }
    fixed_income_allocations = {
        'core_fixed_income', 'high_yield', 'emerging_markets_debt', 'ips'
    }
    cash_allocations = {'cash_alternatives', 'cash'}

    if allocation_key in equity_allocations:
        return 'Equity'
    elif allocation_key in fixed_income_allocations:
        return 'Fixed Income'
    elif allocation_key in cash_allocations:
        return 'Cash'
    else:
        return 'Other'


def map_allocation_to_sector(allocation_key: str) -> str:
    """Map fund profile allocation key to display sector."""
    sector_map = {
        'us_large_cap': 'US Large Cap',
        'us_mid_cap': 'US Mid Cap',
        'us_small_cap': 'US Small Cap',
        'international': 'International Developed',
        'emerging_markets_equity': 'Emerging Markets',
        'reits': 'Real Estate',
        'core_fixed_income': 'Core Bonds',
        'high_yield': 'High Yield Bonds',
        'emerging_markets_debt': 'EM Bonds',
        'ips': 'Inflation Protected',
        'cash_alternatives': 'Cash',
    }
    return sector_map.get(allocation_key, allocation_key.replace('_', ' ').title())


def get_look_through_summary(holdings: List[Dict[str, Any]], account_type: str = '') -> Dict[str, Any]:
    """
    Get a summary of what look-through analysis would show.

    Returns info about which holdings can be expanded without actually expanding.
    """
    profiles = get_all_fund_profiles()
    if not profiles:
        return {
            'available': False,
            'message': 'No fund profiles uploaded. Upload fund profile PDFs to enable look-through analysis.',
            'matchable_holdings': [],
        }

    matchable = []
    for holding in holdings:
        ticker = holding.get('ticker', '')
        description = holding.get('description', '')

        profile = match_holding_to_profile(ticker, description, account_type)
        if profile:
            matchable.append({
                'ticker': ticker,
                'description': description,
                'matched_fund': profile['fund_name'],
                'num_allocations': len(profile.get('asset_allocation', {})),
            })

    return {
        'available': True,
        'message': f'Found {len(matchable)} holdings that can be expanded for look-through analysis.',
        'matchable_holdings': matchable,
        'total_profiles': len(profiles),
    }


def calculate_look_through_allocation(
    holdings: List[Dict[str, Any]],
    total_portfolio_value: float,
    account_type: str = ''
) -> Dict[str, float]:
    """
    Calculate the true asset allocation using look-through analysis.

    Returns a dict mapping asset class to percentage of total portfolio.
    """
    allocation_values = {}

    for holding in holdings:
        ticker = holding.get('ticker', '')
        description = holding.get('description', '')
        market_value = holding.get('market_value', 0)

        # Try to match to a fund profile
        profile = match_holding_to_profile(ticker, description, account_type)

        if profile:
            # Expand using fund profile allocation
            asset_allocation = profile.get('asset_allocation', {})
            for asset_class, percentage in asset_allocation.items():
                if percentage > 0:
                    sector = map_allocation_to_sector(asset_class)
                    if sector not in allocation_values:
                        allocation_values[sector] = 0
                    allocation_values[sector] += market_value * (percentage / 100)
        else:
            # Use existing holding info
            asset_class = holding.get('asset_class', 'Other')
            if asset_class not in allocation_values:
                allocation_values[asset_class] = 0
            allocation_values[asset_class] += market_value

    # Convert to percentages
    allocation_percentages = {}
    for asset_class, value in allocation_values.items():
        pct = (value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        allocation_percentages[asset_class] = round(pct, 2)

    return allocation_percentages

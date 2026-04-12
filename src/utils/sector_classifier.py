"""
Standardized Sector Classification System

Provides consistent categorization of portfolio holdings into:
1. Standardized Labels - Clean, consistent naming
2. Category Groups - High-level consolidated buckets
"""
import re
from typing import Tuple, Dict, List, Optional


# Mapping from various raw labels to standardized labels and category groups
SECTOR_MAPPINGS = {
    # Target Date / Multi-Asset
    'target date': ('Target Date Funds', 'Multi-Asset'),
    'target': ('Target Date Funds', 'Multi-Asset'),
    'lifecycle': ('Target Date Funds', 'Multi-Asset'),
    'retirement': ('Target Date Funds', 'Multi-Asset'),
    'diversified': ('Multi-Asset / Balanced', 'Multi-Asset'),
    'balanced': ('Multi-Asset / Balanced', 'Multi-Asset'),
    'multi-asset': ('Multi-Asset / Balanced', 'Multi-Asset'),
    'allocation': ('Multi-Asset / Balanced', 'Multi-Asset'),

    # Cash Equivalents
    'money market': ('Cash & Money Market', 'Cash Equivalents'),
    'cash': ('Cash & Money Market', 'Cash Equivalents'),
    'cash alternatives': ('Cash & Money Market', 'Cash Equivalents'),
    'stable value': ('Cash & Money Market', 'Cash Equivalents'),
    'short-term': ('Cash & Money Market', 'Cash Equivalents'),
    'short term': ('Cash & Money Market', 'Cash Equivalents'),

    # Equity: Domestic
    'us large cap growth': ('US Large Cap Growth', 'Equity: Domestic'),
    'large cap growth': ('US Large Cap Growth', 'Equity: Domestic'),
    'us large cap value': ('US Large Cap Value', 'Equity: Domestic'),
    'large cap value': ('US Large Cap Value', 'Equity: Domestic'),
    'us large cap': ('US Large Cap Blend', 'Equity: Domestic'),
    'large cap': ('US Large Cap Blend', 'Equity: Domestic'),
    's&p 500': ('US Large Cap Blend', 'Equity: Domestic'),
    'sp500': ('US Large Cap Blend', 'Equity: Domestic'),
    'us mid cap growth': ('US Mid Cap Growth', 'Equity: Domestic'),
    'mid cap growth': ('US Mid Cap Growth', 'Equity: Domestic'),
    'us mid cap value': ('US Mid Cap Value', 'Equity: Domestic'),
    'mid cap value': ('US Mid Cap Value', 'Equity: Domestic'),
    'us mid cap': ('US Mid Cap Blend', 'Equity: Domestic'),
    'mid cap': ('US Mid Cap Blend', 'Equity: Domestic'),
    'us small cap growth': ('US Small Cap Growth', 'Equity: Domestic'),
    'small cap growth': ('US Small Cap Growth', 'Equity: Domestic'),
    'us small cap value': ('US Small Cap Value', 'Equity: Domestic'),
    'small cap value': ('US Small Cap Value', 'Equity: Domestic'),
    'us small cap': ('US Small Cap Blend', 'Equity: Domestic'),
    'small cap': ('US Small Cap Blend', 'Equity: Domestic'),
    'small/mid cap': ('US Small/Mid Cap', 'Equity: Domestic'),
    'us total market': ('US Total Market', 'Equity: Domestic'),
    'total market': ('US Total Market', 'Equity: Domestic'),
    'total stock': ('US Total Market', 'Equity: Domestic'),

    # Equity: International
    'international developed': ('International Developed Equity', 'Equity: International'),
    'developed markets': ('International Developed Equity', 'Equity: International'),
    'international': ('International Equity', 'Equity: International'),
    'foreign': ('International Equity', 'Equity: International'),
    'global': ('International Equity', 'Equity: International'),
    'emerging markets equity': ('Emerging Markets Equity', 'Equity: International'),
    'emerging markets': ('Emerging Markets Equity', 'Equity: International'),
    'emerging market': ('Emerging Markets Equity', 'Equity: International'),
    'em equity': ('Emerging Markets Equity', 'Equity: International'),

    # Equity: Sector
    'technology': ('Sector - Technology', 'Equity: Sector'),
    'tech': ('Sector - Technology', 'Equity: Sector'),
    'information technology': ('Sector - Technology', 'Equity: Sector'),
    'financials': ('Sector - Financials', 'Equity: Sector'),
    'financial': ('Sector - Financials', 'Equity: Sector'),
    'consumer discretionary': ('Sector - Consumer Discretionary', 'Equity: Sector'),
    'consumer staples': ('Sector - Consumer Staples', 'Equity: Sector'),
    'consumer': ('Sector - Consumer', 'Equity: Sector'),
    'healthcare': ('Sector - Healthcare', 'Equity: Sector'),
    'health care': ('Sector - Healthcare', 'Equity: Sector'),
    'industrials': ('Sector - Industrials', 'Equity: Sector'),
    'industrial': ('Sector - Industrials', 'Equity: Sector'),
    'energy': ('Sector - Energy', 'Equity: Sector'),
    'uranium': ('Sector - Uranium/Energy', 'Equity: Sector'),
    'utilities': ('Sector - Utilities', 'Equity: Sector'),
    'materials': ('Sector - Materials', 'Equity: Sector'),
    'communication services': ('Sector - Communication Services', 'Equity: Sector'),
    'communications': ('Sector - Communication Services', 'Equity: Sector'),
    'infrastructure': ('Sector - Infrastructure', 'Equity: Sector'),
    'gold miners': ('Sector - Gold Miners', 'Equity: Sector'),
    'gold': ('Sector - Gold Miners', 'Equity: Sector'),

    # Fixed Income
    'fixed income': ('US Core Fixed Income', 'Fixed Income'),
    'core bond': ('US Core Fixed Income', 'Fixed Income'),
    'core bonds': ('US Core Fixed Income', 'Fixed Income'),
    'core fixed income': ('US Core Fixed Income', 'Fixed Income'),
    'bond': ('US Core Fixed Income', 'Fixed Income'),
    'bonds': ('US Core Fixed Income', 'Fixed Income'),
    'aggregate bond': ('US Core Fixed Income', 'Fixed Income'),
    'municipal bonds': ('Municipal Bonds', 'Fixed Income'),
    'municipal': ('Municipal Bonds', 'Fixed Income'),
    'muni': ('Municipal Bonds', 'Fixed Income'),
    'tips': ('Inflation-Protected Securities', 'Fixed Income'),
    'inflation protected': ('Inflation-Protected Securities', 'Fixed Income'),
    'inflation-protected': ('Inflation-Protected Securities', 'Fixed Income'),
    'ips': ('Inflation-Protected Securities', 'Fixed Income'),
    'treasury inflation': ('Inflation-Protected Securities', 'Fixed Income'),
    'high yield': ('High Yield Bonds', 'Fixed Income'),
    'high-yield': ('High Yield Bonds', 'Fixed Income'),
    'junk bond': ('High Yield Bonds', 'Fixed Income'),
    'emerging markets debt': ('Emerging Markets Debt', 'Fixed Income'),
    'emerging markets bond': ('Emerging Markets Debt', 'Fixed Income'),
    'em debt': ('Emerging Markets Debt', 'Fixed Income'),
    'em bonds': ('Emerging Markets Debt', 'Fixed Income'),
    'international bonds': ('International Fixed Income', 'Fixed Income'),
    'international bond': ('International Fixed Income', 'Fixed Income'),
    'international fixed income': ('International Fixed Income', 'Fixed Income'),
    'foreign bond': ('International Fixed Income', 'Fixed Income'),

    # Real Assets
    'us real estate': ('US REITs / Real Estate', 'Real Assets'),
    'real estate': ('US REITs / Real Estate', 'Real Assets'),
    'reit': ('US REITs / Real Estate', 'Real Assets'),
    'reits': ('US REITs / Real Estate', 'Real Assets'),
    'international real estate': ('International REITs', 'Real Assets'),
    'global real estate': ('International REITs', 'Real Assets'),
    'commodities': ('Commodities', 'Real Assets'),
    'commodity': ('Commodities', 'Real Assets'),
    'natural resources': ('Commodities', 'Real Assets'),

    # Alternatives
    'private equity': ('Private Equity', 'Alternatives'),
    'crypto': ('Cryptocurrency', 'Alternatives'),
    'cryptocurrency': ('Cryptocurrency', 'Alternatives'),
    'bitcoin': ('Cryptocurrency', 'Alternatives'),
    'digital assets': ('Cryptocurrency', 'Alternatives'),
    'hedge fund': ('Hedge Funds', 'Alternatives'),
    'alternatives': ('Alternatives', 'Alternatives'),
    'alternative': ('Alternatives', 'Alternatives'),

    # Other
    'other': ('Unclassified', 'Other'),
    'unknown': ('Unclassified', 'Other'),
}

# Ticker-based classification for common ETFs and mutual funds
TICKER_CLASSIFICATIONS = {
    # Target Date Funds (patterns handled separately)

    # Cash / Money Market
    'VMFXX': ('Cash & Money Market', 'Cash Equivalents'),
    'SPAXX': ('Cash & Money Market', 'Cash Equivalents'),
    'FDRXX': ('Cash & Money Market', 'Cash Equivalents'),
    'SWVXX': ('Cash & Money Market', 'Cash Equivalents'),

    # US Large Cap Blend
    'VTI': ('US Total Market', 'Equity: Domestic'),
    'VTSAX': ('US Total Market', 'Equity: Domestic'),
    'FSKAX': ('US Total Market', 'Equity: Domestic'),
    'SWTSX': ('US Total Market', 'Equity: Domestic'),
    'ITOT': ('US Total Market', 'Equity: Domestic'),
    'SCHB': ('US Total Market', 'Equity: Domestic'),
    'VOO': ('US Large Cap Blend', 'Equity: Domestic'),
    'VFIAX': ('US Large Cap Blend', 'Equity: Domestic'),
    'SPY': ('US Large Cap Blend', 'Equity: Domestic'),
    'IVV': ('US Large Cap Blend', 'Equity: Domestic'),
    'FXAIX': ('US Large Cap Blend', 'Equity: Domestic'),
    'SWPPX': ('US Large Cap Blend', 'Equity: Domestic'),

    # US Large Cap Growth
    'VUG': ('US Large Cap Growth', 'Equity: Domestic'),
    'VIGAX': ('US Large Cap Growth', 'Equity: Domestic'),
    'QQQ': ('US Large Cap Growth', 'Equity: Domestic'),
    'IWF': ('US Large Cap Growth', 'Equity: Domestic'),
    'SCHG': ('US Large Cap Growth', 'Equity: Domestic'),

    # US Large Cap Value
    'VTV': ('US Large Cap Value', 'Equity: Domestic'),
    'VVIAX': ('US Large Cap Value', 'Equity: Domestic'),
    'IWD': ('US Large Cap Value', 'Equity: Domestic'),
    'SCHV': ('US Large Cap Value', 'Equity: Domestic'),

    # US Mid Cap
    'VO': ('US Mid Cap Blend', 'Equity: Domestic'),
    'VIMAX': ('US Mid Cap Blend', 'Equity: Domestic'),
    'IJH': ('US Mid Cap Blend', 'Equity: Domestic'),
    'MDY': ('US Mid Cap Blend', 'Equity: Domestic'),

    # US Small Cap
    'VB': ('US Small Cap Blend', 'Equity: Domestic'),
    'VSMAX': ('US Small Cap Blend', 'Equity: Domestic'),
    'IJR': ('US Small Cap Blend', 'Equity: Domestic'),
    'IWM': ('US Small Cap Blend', 'Equity: Domestic'),
    'SCHA': ('US Small Cap Blend', 'Equity: Domestic'),

    # International Developed
    'VEA': ('International Developed Equity', 'Equity: International'),
    'VTMGX': ('International Developed Equity', 'Equity: International'),
    'IEFA': ('International Developed Equity', 'Equity: International'),
    'EFA': ('International Developed Equity', 'Equity: International'),
    'SCHF': ('International Developed Equity', 'Equity: International'),

    # International Broad
    'VXUS': ('International Equity', 'Equity: International'),
    'VTIAX': ('International Equity', 'Equity: International'),
    'IXUS': ('International Equity', 'Equity: International'),

    # Emerging Markets
    'VWO': ('Emerging Markets Equity', 'Equity: International'),
    'VEMAX': ('Emerging Markets Equity', 'Equity: International'),
    'IEMG': ('Emerging Markets Equity', 'Equity: International'),
    'EEM': ('Emerging Markets Equity', 'Equity: International'),
    'SCHE': ('Emerging Markets Equity', 'Equity: International'),

    # Sector - Technology
    'VGT': ('Sector - Technology', 'Equity: Sector'),
    'XLK': ('Sector - Technology', 'Equity: Sector'),
    'FTEC': ('Sector - Technology', 'Equity: Sector'),

    # Sector - Healthcare
    'VHT': ('Sector - Healthcare', 'Equity: Sector'),
    'XLV': ('Sector - Healthcare', 'Equity: Sector'),
    'FHLC': ('Sector - Healthcare', 'Equity: Sector'),

    # Sector - Financials
    'VFH': ('Sector - Financials', 'Equity: Sector'),
    'XLF': ('Sector - Financials', 'Equity: Sector'),

    # Sector - Consumer
    'VCR': ('Sector - Consumer Discretionary', 'Equity: Sector'),
    'XLY': ('Sector - Consumer Discretionary', 'Equity: Sector'),
    'VDC': ('Sector - Consumer Staples', 'Equity: Sector'),
    'XLP': ('Sector - Consumer Staples', 'Equity: Sector'),

    # Sector - Industrials
    'VIS': ('Sector - Industrials', 'Equity: Sector'),
    'XLI': ('Sector - Industrials', 'Equity: Sector'),

    # Sector - Energy
    'VDE': ('Sector - Energy', 'Equity: Sector'),
    'XLE': ('Sector - Energy', 'Equity: Sector'),

    # Sector - Utilities
    'VPU': ('Sector - Utilities', 'Equity: Sector'),
    'XLU': ('Sector - Utilities', 'Equity: Sector'),

    # Sector - Materials
    'VAW': ('Sector - Materials', 'Equity: Sector'),
    'XLB': ('Sector - Materials', 'Equity: Sector'),

    # Sector - Communication Services
    'VOX': ('Sector - Communication Services', 'Equity: Sector'),
    'XLC': ('Sector - Communication Services', 'Equity: Sector'),

    # Fixed Income - Core
    'BND': ('US Core Fixed Income', 'Fixed Income'),
    'VBTLX': ('US Core Fixed Income', 'Fixed Income'),
    'AGG': ('US Core Fixed Income', 'Fixed Income'),
    'SCHZ': ('US Core Fixed Income', 'Fixed Income'),

    # Fixed Income - Long Term
    'TLT': ('Long-Term Treasuries', 'Fixed Income'),
    'VGLT': ('Long-Term Treasuries', 'Fixed Income'),

    # Fixed Income - Short Term
    'BSV': ('Short-Term Bonds', 'Fixed Income'),
    'VBIRX': ('Short-Term Bonds', 'Fixed Income'),
    'SHY': ('Short-Term Treasuries', 'Fixed Income'),

    # Fixed Income - TIPS
    'TIP': ('Inflation-Protected Securities', 'Fixed Income'),
    'VTIP': ('Inflation-Protected Securities', 'Fixed Income'),
    'SCHP': ('Inflation-Protected Securities', 'Fixed Income'),

    # Fixed Income - Municipal
    'MUB': ('Municipal Bonds', 'Fixed Income'),
    'VTEB': ('Municipal Bonds', 'Fixed Income'),

    # Fixed Income - High Yield
    'HYG': ('High Yield Bonds', 'Fixed Income'),
    'JNK': ('High Yield Bonds', 'Fixed Income'),

    # Fixed Income - International
    'BNDX': ('International Fixed Income', 'Fixed Income'),
    'VTABX': ('International Fixed Income', 'Fixed Income'),
    'IAGG': ('International Fixed Income', 'Fixed Income'),

    # Fixed Income - Emerging Markets
    'EMB': ('Emerging Markets Debt', 'Fixed Income'),
    'VWOB': ('Emerging Markets Debt', 'Fixed Income'),

    # Real Assets - REITs
    'VNQ': ('US REITs / Real Estate', 'Real Assets'),
    'VGSLX': ('US REITs / Real Estate', 'Real Assets'),
    'XLRE': ('US REITs / Real Estate', 'Real Assets'),
    'IYR': ('US REITs / Real Estate', 'Real Assets'),
    'VNQI': ('International REITs', 'Real Assets'),

    # Real Assets - Commodities
    'DJP': ('Commodities', 'Real Assets'),
    'GSG': ('Commodities', 'Real Assets'),
    'DBC': ('Commodities', 'Real Assets'),
    'GLD': ('Commodities', 'Real Assets'),
    'IAU': ('Commodities', 'Real Assets'),

    # Alternatives - Crypto
    'GBTC': ('Cryptocurrency', 'Alternatives'),
    'BITO': ('Cryptocurrency', 'Alternatives'),
    'ETHE': ('Cryptocurrency', 'Alternatives'),
}

# Category group order for display
CATEGORY_GROUP_ORDER = [
    'Equity: Domestic',
    'Equity: International',
    'Equity: Sector',
    'Fixed Income',
    'Real Assets',
    'Alternatives',
    'Multi-Asset',
    'Cash Equivalents',
    'Other',
]


def classify_holding(
    ticker: str,
    description: str = '',
    existing_sector: str = ''
) -> Tuple[str, str]:
    """
    Classify a holding into standardized label and category group.

    Args:
        ticker: Ticker symbol
        description: Full name/description of the holding
        existing_sector: Any existing sector classification

    Returns:
        Tuple of (standardized_label, category_group)
    """
    ticker_upper = ticker.upper().strip()
    search_text = f"{ticker} {description} {existing_sector}".lower()

    # 1. Check for Target Date Fund pattern first
    target_date_match = re.search(r'(?:target|tgt|retire|lifecycle).*?(\d{4})', search_text)
    if target_date_match or 'target date' in search_text:
        return ('Target Date Funds', 'Multi-Asset')

    # 2. Check ticker-based classification
    if ticker_upper in TICKER_CLASSIFICATIONS:
        return TICKER_CLASSIFICATIONS[ticker_upper]

    # 3. Check description/sector against mappings
    for key, (label, group) in SECTOR_MAPPINGS.items():
        if key in search_text:
            return (label, group)

    # 4. Fallback to existing sector if provided
    if existing_sector and existing_sector.lower() not in ('unknown', 'other', ''):
        # Try to map the existing sector
        existing_lower = existing_sector.lower()
        for key, (label, group) in SECTOR_MAPPINGS.items():
            if key in existing_lower:
                return (label, group)
        # Return existing sector with best-guess group
        return (existing_sector, guess_category_group(existing_sector))

    # 5. Default
    return ('Unclassified', 'Other')


def guess_category_group(label: str) -> str:
    """Guess the category group from a label."""
    label_lower = label.lower()

    if any(x in label_lower for x in ['equity', 'stock', 'cap', 'growth', 'value']):
        if any(x in label_lower for x in ['international', 'foreign', 'emerging', 'global']):
            return 'Equity: International'
        elif any(x in label_lower for x in ['sector', 'technology', 'healthcare', 'financial']):
            return 'Equity: Sector'
        return 'Equity: Domestic'
    elif any(x in label_lower for x in ['bond', 'fixed', 'income', 'treasury', 'municipal']):
        return 'Fixed Income'
    elif any(x in label_lower for x in ['real estate', 'reit', 'commodity']):
        return 'Real Assets'
    elif any(x in label_lower for x in ['private', 'crypto', 'alternative', 'hedge']):
        return 'Alternatives'
    elif any(x in label_lower for x in ['target', 'balanced', 'allocation', 'diversified']):
        return 'Multi-Asset'
    elif any(x in label_lower for x in ['cash', 'money market', 'stable']):
        return 'Cash Equivalents'

    return 'Other'


def consolidate_by_category_group(
    allocations: List[Dict]
) -> List[Dict]:
    """
    Consolidate allocations by category group.

    Args:
        allocations: List of dicts with 'name', 'value', 'percent', 'category_group'

    Returns:
        List of consolidated allocations by category group
    """
    group_totals = {}

    for item in allocations:
        group = item.get('category_group', 'Other')
        if group not in group_totals:
            group_totals[group] = {'value': 0, 'items': []}
        group_totals[group]['value'] += item.get('value', 0)
        group_totals[group]['items'].append(item.get('name', ''))

    # Calculate total for percentages
    total_value = sum(g['value'] for g in group_totals.values())

    # Build result in preferred order
    result = []
    for group in CATEGORY_GROUP_ORDER:
        if group in group_totals:
            data = group_totals[group]
            result.append({
                'name': group,
                'value': data['value'],
                'percent': (data['value'] / total_value * 100) if total_value > 0 else 0,
                'items': data['items'],
            })

    # Add any groups not in our order
    for group, data in group_totals.items():
        if group not in CATEGORY_GROUP_ORDER:
            result.append({
                'name': group,
                'value': data['value'],
                'percent': (data['value'] / total_value * 100) if total_value > 0 else 0,
                'items': data['items'],
            })

    return result


def get_category_group_colors() -> Dict[str, str]:
    """Get consistent colors for category groups."""
    return {
        'Equity: Domestic': '#3b82f6',      # Blue
        'Equity: International': '#06b6d4',  # Cyan
        'Equity: Sector': '#8b5cf6',         # Purple
        'Fixed Income': '#10b981',           # Green
        'Real Assets': '#f59e0b',            # Amber
        'Alternatives': '#ec4899',           # Pink
        'Multi-Asset': '#6366f1',            # Indigo
        'Cash Equivalents': '#64748b',       # Slate
        'Other': '#9ca3af',                  # Gray
    }


# Simplified Asset Allocation Categories
SIMPLIFIED_ASSET_CLASSES = ['Stocks', 'Bonds', 'Cash', 'REITs', 'Alternatives', 'Commodities', 'Other']

SIMPLIFIED_ASSET_COLORS = {
    'Stocks': '#3b82f6',       # Blue - primary investment
    'Bonds': '#10b981',        # Green - fixed income
    'Cash': '#06b6d4',         # Cyan - cash/money market
    'REITs': '#f59e0b',        # Amber - real estate
    'Alternatives': '#ec4899', # Pink - alternatives
    'Commodities': '#eab308',  # Yellow - commodities
    'Other': '#64748b',        # Slate - unknown/other
}

# Target Date Fund Glide Path - estimated stock allocation by target year
# Based on typical industry glide paths (Vanguard, Fidelity, etc.)
TARGET_DATE_GLIDE_PATH = {
    2065: 0.90,  # 90% stocks, 10% bonds
    2060: 0.90,
    2055: 0.90,
    2050: 0.88,
    2045: 0.85,
    2040: 0.80,
    2035: 0.72,
    2030: 0.65,
    2025: 0.55,
    2020: 0.45,
    2015: 0.35,
    2010: 0.30,
}


def extract_target_year(fund_name: str) -> Optional[int]:
    """
    Extract target year from a target date fund name.

    Examples:
        "Target Date 2045 Fund" -> 2045
        "Target Retirement 2030" -> 2030
        "NH PORTFOLIO 2030" -> 2030
        "LifePath Index 2055 Fund" -> 2055

    Returns:
        The target year as int, or None if not found
    """
    import re
    # Look for 4-digit years between 2010 and 2070
    match = re.search(r'20[1-6][0-9]', fund_name)
    if match:
        return int(match.group())
    return None


def get_target_date_allocation(target_year: int) -> Tuple[float, float]:
    """
    Get estimated stock/bond allocation for a target date fund.

    Args:
        target_year: The target retirement year (e.g., 2045)

    Returns:
        Tuple of (stock_percent, bond_percent) as decimals (e.g., (0.85, 0.15))
    """
    # Find the closest year in the glide path
    if target_year in TARGET_DATE_GLIDE_PATH:
        stock_pct = TARGET_DATE_GLIDE_PATH[target_year]
    else:
        # Interpolate between known years
        years = sorted(TARGET_DATE_GLIDE_PATH.keys())
        if target_year > max(years):
            stock_pct = 0.90  # Very far out = aggressive
        elif target_year < min(years):
            stock_pct = 0.30  # Already retired = conservative
        else:
            # Find surrounding years and interpolate
            lower_year = max(y for y in years if y <= target_year)
            upper_year = min(y for y in years if y >= target_year)
            if lower_year == upper_year:
                stock_pct = TARGET_DATE_GLIDE_PATH[lower_year]
            else:
                # Linear interpolation
                lower_pct = TARGET_DATE_GLIDE_PATH[lower_year]
                upper_pct = TARGET_DATE_GLIDE_PATH[upper_year]
                ratio = (target_year - lower_year) / (upper_year - lower_year)
                stock_pct = lower_pct + ratio * (upper_pct - lower_pct)

    bond_pct = 1.0 - stock_pct
    return (stock_pct, bond_pct)


def get_simplified_asset_class(
    standardized_label: str,
    category_group: str
) -> str:
    """
    Map a holding to a simplified asset class.

    Maps detailed category groups to: Stocks, Bonds, REITs, Alternatives, Commodities, Other

    Args:
        standardized_label: The detailed label (e.g., 'US Large Cap Growth')
        category_group: The category group (e.g., 'Equity: Domestic')

    Returns:
        Simplified asset class: Stocks, Bonds, REITs, Alternatives, Commodities, or Other
    """
    label_lower = standardized_label.lower()
    group_lower = category_group.lower()

    # Stocks: All equity categories
    if group_lower in ('equity: domestic', 'equity: international', 'equity: sector'):
        return 'Stocks'

    # Bonds: All fixed income
    if group_lower == 'fixed income':
        return 'Bonds'

    # REITs: Real estate specifically (not commodities)
    if group_lower == 'real assets':
        if any(x in label_lower for x in ['reit', 'real estate']):
            return 'REITs'
        elif any(x in label_lower for x in ['commodity', 'commodities', 'gold', 'natural resources']):
            return 'Commodities'
        # Default real assets to REITs
        return 'REITs'

    # Alternatives: Crypto, private equity, hedge funds, etc.
    if group_lower == 'alternatives':
        return 'Alternatives'

    # Multi-Asset (Target Date Funds): These contain mostly stocks
    # Typical target date fund allocation:
    # - 2050+ funds: ~90% stocks, 10% bonds
    # - 2040 funds: ~85% stocks, 15% bonds
    # - 2030 funds: ~70% stocks, 30% bonds
    # - 2020 funds: ~50% stocks, 50% bonds
    # Since most users have 2030-2050 funds, classify as Stocks (the majority component)
    if group_lower == 'multi-asset':
        # Target date funds are primarily stocks
        return 'Stocks'

    # Cash Equivalents: Separate category for money market, savings, short-term instruments
    if group_lower == 'cash equivalents':
        return 'Cash'

    # Default
    return 'Other'


def calculate_simplified_allocation(
    allocations: List[Dict]
) -> List[Dict]:
    """
    Calculate simplified asset allocation from detailed allocations.

    For Multi-Asset holdings (Target Date Funds), estimates the stock/bond split
    based on the target year using a typical glide path.

    Args:
        allocations: List of dicts with 'name', 'value', 'percent', 'category_group'

    Returns:
        List of simplified allocations: Stocks, Bonds, REITs, Alternatives, Commodities, Other
    """
    simplified_totals = {cls: {'value': 0, 'items': []} for cls in SIMPLIFIED_ASSET_CLASSES}

    for item in allocations:
        label = item.get('name', '')
        group = item.get('category_group', 'Other')
        value = item.get('value', 0)

        # Special handling for Multi-Asset (Target Date Funds)
        # Split their value between Stocks and Bonds based on glide path
        if group.lower() == 'multi-asset':
            target_year = extract_target_year(label)
            if target_year:
                stock_pct, bond_pct = get_target_date_allocation(target_year)
                # Split the value
                stock_value = value * stock_pct
                bond_value = value * bond_pct
                simplified_totals['Stocks']['value'] += stock_value
                simplified_totals['Stocks']['items'].append(f"{label} ({stock_pct*100:.0f}%)")
                simplified_totals['Bonds']['value'] += bond_value
                simplified_totals['Bonds']['items'].append(f"{label} ({bond_pct*100:.0f}%)")
            else:
                # No target year found - use default 70/30 split (balanced fund assumption)
                stock_value = value * 0.70
                bond_value = value * 0.30
                simplified_totals['Stocks']['value'] += stock_value
                simplified_totals['Stocks']['items'].append(f"{label} (est. 70%)")
                simplified_totals['Bonds']['value'] += bond_value
                simplified_totals['Bonds']['items'].append(f"{label} (est. 30%)")
            continue

        # Normal classification for non-multi-asset holdings
        simplified_class = get_simplified_asset_class(label, group)
        simplified_totals[simplified_class]['value'] += value
        simplified_totals[simplified_class]['items'].append(label)

    # Calculate total for percentages
    total_value = sum(data['value'] for data in simplified_totals.values())

    # Build result in order, only include non-zero allocations
    result = []
    for asset_class in SIMPLIFIED_ASSET_CLASSES:
        data = simplified_totals[asset_class]
        if data['value'] > 0:
            result.append({
                'name': asset_class,
                'value': data['value'],
                'percent': (data['value'] / total_value * 100) if total_value > 0 else 0,
                'color': SIMPLIFIED_ASSET_COLORS.get(asset_class, '#9ca3af'),
                'items': data['items'],
            })

    # Sort by value descending
    result.sort(key=lambda x: x['value'], reverse=True)

    return result


def get_simplified_asset_colors() -> Dict[str, str]:
    """Get colors for simplified asset classes."""
    return SIMPLIFIED_ASSET_COLORS

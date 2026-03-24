"""
Fund Profile PDF Parser for JPMC Empower 401k Fund Details.

Extracts Target Date Fund asset allocations from fund profile documents.
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

import pdfplumber


# Standard asset allocation categories for normalization
ASSET_CATEGORIES = {
    'us_large_cap': ['U.S. large cap equity', 'US large cap equity', 'Large cap equity'],
    'us_mid_cap': ['U.S. mid cap equity', 'US mid cap equity', 'Mid cap equity'],
    'us_small_cap': ['U.S. small cap equity', 'US small cap equity', 'Small cap equity'],
    'reits': ['REITs', 'Real Estate Investment Trusts'],
    'international': ['International equity', 'International large cap'],
    'emerging_markets_equity': ['Emerging markets equity', 'Emerging market equity'],
    'core_fixed_income': ['Core fixed income', 'Core bond'],
    'high_yield': ['High yield', 'High-yield'],
    'emerging_markets_debt': ['Emerging markets debt', 'EM debt'],
    'ips': ['IPS', 'Inflation-Protected Securities', 'TIPS'],
    'cash_alternatives': ['Cash alternatives', 'Cash', 'Money market'],
}


def normalize_category(raw_category: str) -> str:
    """Normalize a raw category name to our standard format."""
    raw_lower = raw_category.lower().strip()

    for standard, variants in ASSET_CATEGORIES.items():
        for variant in variants:
            if variant.lower() in raw_lower or raw_lower in variant.lower():
                return standard

    # If no match, clean up the raw name
    return raw_lower.replace(' ', '_').replace('.', '').replace('-', '_')


def parse_percentage(value: str) -> Optional[float]:
    """Parse a percentage string to float."""
    if not value:
        return None

    # Remove % sign and any extra characters
    cleaned = re.sub(r'[^\d.]', '', value.strip())

    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_two_funds_from_page(text: str, year1: int, year2: int) -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    Extract two Target Date Funds from a page with side-by-side layout.

    The JPMC PDF has pages with two funds side-by-side, with allocation legends
    showing left fund first, then right fund for each category.
    """
    fund1 = {
        'fund_name': f'Target Date {year1} Fund',
        'target_year': year1,
        'fund_type': 'Target Date',
        'source': 'JPMC Empower',
        'risk_assessment': None,
        'expense_ratio': None,
        'asset_allocation': {}
    }
    fund2 = {
        'fund_name': f'Target Date {year2} Fund',
        'target_year': year2,
        'fund_type': 'Target Date',
        'source': 'JPMC Empower',
        'risk_assessment': None,
        'expense_ratio': None,
        'asset_allocation': {}
    }

    # Extract risk assessments - they appear in order
    risk_matches = re.findall(r'Risk assessment:\s*([\w\s]+?)(?:\n|Annual)', text)
    if len(risk_matches) >= 1:
        fund1['risk_assessment'] = risk_matches[0].strip()
    if len(risk_matches) >= 2:
        fund2['risk_assessment'] = risk_matches[1].strip()

    # Extract expense ratios - they appear in order
    expense_matches = re.findall(r'Annual expenses[^:]*:\s*(\d+)\s*basis points', text)
    if len(expense_matches) >= 1:
        fund1['expense_ratio'] = int(expense_matches[0]) / 100
    if len(expense_matches) >= 2:
        fund2['expense_ratio'] = int(expense_matches[1]) / 100

    # Extract asset allocations from the legend at the bottom
    # Pattern: "Category – XX.XX%" appears twice per category (left fund, right fund)
    # The legend format is: "U.S. large cap equity – 41.51% Core fixed income – 18.38% U.S. large cap equity – 45.69% Core fixed income – 11.69%"

    # Find the allocation legend section (after all the jumbled chart numbers)
    legend_match = re.search(r'(U\.S\. large cap equity.+?)(?:\d+Note|\d+See)', text, re.DOTALL)
    if legend_match:
        legend_text = legend_match.group(1)

        # Parse allocations - each category appears twice (fund1 then fund2)
        # Categories: U.S. large cap, U.S. mid cap, U.S. small cap, REITs, International, Emerging markets equity,
        #             Core fixed income, High yield, Emerging markets debt, IPS, Cash alternatives
        categories_order = [
            ('U.S. large cap equity', 'us_large_cap'),
            ('Core fixed income', 'core_fixed_income'),
            ('U.S. mid cap equity', 'us_mid_cap'),
            ('High yield', 'high_yield'),
            ('U.S. small cap equity', 'us_small_cap'),
            ('Emerging markets debt', 'emerging_markets_debt'),
            ('REITs', 'reits'),
            ('IPS', 'ips'),
            ('International equity', 'international'),
            ('Cash alternatives', 'cash_alternatives'),
            ('Emerging markets equity', 'emerging_markets_equity'),
        ]

        for display_name, category_key in categories_order:
            # Find all occurrences of this category
            pattern = re.escape(display_name) + r'\s*[–-]\s*(\d+\.?\d*)%'
            matches = re.findall(pattern, legend_text)

            if len(matches) >= 1:
                val = parse_percentage(matches[0])
                if val is not None and val > 0:
                    fund1['asset_allocation'][category_key] = val
            if len(matches) >= 2:
                val = parse_percentage(matches[1])
                if val is not None and val > 0:
                    fund2['asset_allocation'][category_key] = val

    return (
        fund1 if fund1['asset_allocation'] else None,
        fund2 if fund2['asset_allocation'] else None
    )


def extract_target_date_fund_from_text(text: str, fund_year: int) -> Optional[Dict[str, Any]]:
    """
    Extract Target Date Fund data from page text.

    Returns dict with:
    - fund_name
    - target_year
    - risk_assessment
    - expense_ratio
    - asset_allocation
    """
    result = {
        'fund_name': f'Target Date {fund_year} Fund',
        'target_year': fund_year,
        'fund_type': 'Target Date',
        'source': 'JPMC Empower',
        'risk_assessment': None,
        'expense_ratio': None,
        'asset_allocation': {}
    }

    # Extract risk assessment
    risk_match = re.search(r'Risk assessment:\s*([\w\s]+?)(?:\n|Annual)', text)
    if risk_match:
        result['risk_assessment'] = risk_match.group(1).strip()

    # Extract expense ratio (in basis points)
    expense_match = re.search(r'Annual expenses[^:]*:\s*(\d+)\s*basis points', text)
    if expense_match:
        result['expense_ratio'] = int(expense_match.group(1)) / 100  # Convert to percentage

    # Extract asset allocation
    # Pattern: "Category – XX.XX%"
    allocation_pattern = r'([A-Za-z\.\s\-]+)\s+[–-]\s+(\d+\.?\d*)%'

    for match in re.finditer(allocation_pattern, text):
        category_raw = match.group(1).strip()
        percentage = parse_percentage(match.group(2))

        if percentage is not None and percentage > 0:
            category = normalize_category(category_raw)
            # Avoid duplicates - take the first occurrence
            if category not in result['asset_allocation']:
                result['asset_allocation'][category] = percentage

    return result if result['asset_allocation'] else None


def parse_jpmc_fund_profile_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Parse JPMC Empower Fund Profile PDF and extract all Target Date Funds.

    Memory-optimized version that processes pages individually to stay
    under Render's 512MB memory limit.

    Args:
        pdf_path: Path to the fund profile PDF

    Returns:
        List of fund profile dictionaries
    """
    import gc

    funds = []
    processed_years = set()

    # First, determine total pages without loading content
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

    # Target Date Funds are typically on pages 10-25 in JPMC PDFs
    # We'll scan a focused range to save memory
    start_page = max(0, 10)
    end_page = min(total_pages, 30)

    # Process pages one at a time to minimize memory usage
    for page_num in range(start_page, end_page):
        # Open PDF fresh for each page to avoid memory buildup
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num >= len(pdf.pages):
                    break

                page = pdf.pages[page_num]
                text = page.extract_text() or ''

                # Skip pages without Target Date content
                if 'Target Date' not in text:
                    continue

                # Extract fund years mentioned on this page
                year_pattern = r'Target Date (\d{4}) Fund'
                years_found = [int(y) for y in re.findall(year_pattern, text)]
                years_found = sorted(set(years_found))

                # Check for Target Date Income Fund
                if 'Target Date Income Fund' in text and 'income' not in processed_years:
                    income_fund = extract_target_date_income_fund(text)
                    if income_fund:
                        funds.append(income_fund)
                        processed_years.add('income')

                # Handle two-funds-per-page layout
                if len(years_found) == 2:
                    year1, year2 = years_found[0], years_found[1]

                    if year1 not in processed_years or year2 not in processed_years:
                        fund1, fund2 = extract_two_funds_from_page(text, year1, year2)

                        if fund1 and year1 not in processed_years:
                            funds.append(fund1)
                            processed_years.add(year1)

                        if fund2 and year2 not in processed_years:
                            funds.append(fund2)
                            processed_years.add(year2)

                elif len(years_found) == 1:
                    year = years_found[0]
                    if year not in processed_years:
                        fund_data = extract_target_date_fund_from_text(text, year)
                        if fund_data:
                            funds.append(fund_data)
                            processed_years.add(year)

        except Exception as e:
            print(f"[Fund Parser] Error on page {page_num}: {e}", flush=True)
            continue

        # Force garbage collection after each page
        gc.collect()

    # Sort by target year
    funds.sort(key=lambda f: f.get('target_year') or 0)

    return funds


def extract_target_date_income_fund(text: str) -> Optional[Dict[str, Any]]:
    """Extract Target Date Income Fund (for retirees)."""
    if 'Target Date Income Fund' not in text:
        return None

    result = {
        'fund_name': 'Target Date Income Fund',
        'target_year': None,
        'fund_type': 'Target Date Income',
        'source': 'JPMC Empower',
        'risk_assessment': None,
        'expense_ratio': None,
        'asset_allocation': {}
    }

    # Extract from the Income Fund section
    # Risk assessment
    risk_match = re.search(r'Target Date Income Fund.*?Risk assessment:\s*([\w\s]+?)(?:\n|Annual)', text, re.DOTALL)
    if risk_match:
        result['risk_assessment'] = risk_match.group(1).strip()

    # Expense ratio
    expense_match = re.search(r'Target Date Income Fund.*?Annual expenses[^:]*:\s*(\d+)\s*basis points', text, re.DOTALL)
    if expense_match:
        result['expense_ratio'] = int(expense_match.group(1)) / 100

    # Asset allocation - look for the allocation section after Income Fund
    allocation_pattern = r'([A-Za-z\.\s\-]+)\s+[–-]\s+(\d+\.?\d*)%'

    for match in re.finditer(allocation_pattern, text):
        category_raw = match.group(1).strip()
        percentage = parse_percentage(match.group(2))

        if percentage is not None and percentage > 0:
            category = normalize_category(category_raw)
            if category not in result['asset_allocation']:
                result['asset_allocation'][category] = percentage

    return result if result['asset_allocation'] else None


def detect_fund_profile_format(pdf_path: str) -> Optional[str]:
    """
    Detect the format of a fund profile PDF.

    Returns:
        'jpmc_empower' - JPMC Empower 401k format
        'wells_fargo' - Wells Fargo format
        None - Unknown format
    """
    with pdfplumber.open(pdf_path) as pdf:
        # Check first few pages
        for page in pdf.pages[:5]:
            text = (page.extract_text() or '').lower()

            if 'jpmorgan chase' in text and '401(k)' in text:
                return 'jpmc_empower'
            elif 'wells fargo' in text:
                return 'wells_fargo'
            elif 'empower' in text and 'investment fund profiles' in text:
                return 'jpmc_empower'  # Generic Empower format

    return None


def parse_fund_profile_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Parse any supported fund profile PDF format.

    Args:
        pdf_path: Path to the fund profile PDF

    Returns:
        List of fund profile dictionaries
    """
    # Detect format
    format_type = detect_fund_profile_format(pdf_path)

    if format_type == 'jpmc_empower':
        return parse_jpmc_fund_profile_pdf(pdf_path)
    else:
        # Default to JPMC format for now
        return parse_jpmc_fund_profile_pdf(pdf_path)


def validate_fund_profile(profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a fund profile has required data.

    Returns:
        (is_valid, list of issues)
    """
    issues = []

    if not profile.get('fund_name'):
        issues.append('Missing fund name')

    if not profile.get('asset_allocation'):
        issues.append('Missing asset allocation')
    else:
        total = sum(profile['asset_allocation'].values())
        if abs(total - 100) > 2:  # Allow 2% tolerance for rounding
            issues.append(f'Asset allocation totals {total:.1f}%, expected ~100%')

    return len(issues) == 0, issues


def summarize_fund_profiles(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a summary of parsed fund profiles.
    """
    return {
        'count': len(profiles),
        'funds': [
            {
                'name': p.get('fund_name'),
                'target_year': p.get('target_year'),
                'risk': p.get('risk_assessment'),
                'expense_ratio': p.get('expense_ratio'),
                'allocations': len(p.get('asset_allocation', {})),
            }
            for p in profiles
        ]
    }


# CLI testing
if __name__ == '__main__':
    import sys
    import json

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = 'data/Fund details/JPMC empower 401k fund details.pdf'

    print(f"Parsing: {pdf_path}")
    print("=" * 60)

    profiles = parse_fund_profile_pdf(pdf_path)

    print(f"\nFound {len(profiles)} fund profiles:\n")

    for profile in profiles:
        print(f"Fund: {profile['fund_name']}")
        print(f"  Target Year: {profile.get('target_year', 'N/A')}")
        print(f"  Risk: {profile.get('risk_assessment', 'Unknown')}")
        print(f"  Expense Ratio: {profile.get('expense_ratio', 'N/A')}")
        print(f"  Asset Allocation:")

        allocation = profile.get('asset_allocation', {})
        total = 0
        for category, pct in sorted(allocation.items(), key=lambda x: -x[1]):
            print(f"    {category}: {pct:.2f}%")
            total += pct
        print(f"    TOTAL: {total:.2f}%")

        is_valid, issues = validate_fund_profile(profile)
        if not is_valid:
            print(f"  VALIDATION ISSUES: {issues}")

        print()

"""
Choices for the investment profile, shared by the /profile page.

Values match the ones the onboarding wizard saves, so profiles created through
either path look the same to the AI advisor.
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple

ACCOUNT_TYPES = [
    ('401k', '401(k) / 403(b)'),
    ('traditional_ira', 'Traditional IRA'),
    ('roth_ira', 'Roth IRA'),
    ('taxable', 'Taxable Brokerage'),
    ('hsa', 'HSA'),
    ('529', '529 Plan'),
    ('other', 'Other'),
]

BROKERAGES = [
    ('fidelity', 'Fidelity'),
    ('vanguard', 'Vanguard'),
    ('schwab', 'Charles Schwab'),
    ('tdameritrade', 'TD Ameritrade'),
    ('etrade', 'E*TRADE'),
    ('robinhood', 'Robinhood'),
    ('betterment', 'Betterment'),
    ('wealthfront', 'Wealthfront'),
    ('merrill', 'Merrill Edge'),
    ('jpmorgan', 'J.P. Morgan'),
    ('other', 'Other'),
]

PORTFOLIO_SIZES = [
    ('under_25k', 'Under $25,000'),
    ('25k_100k', '$25,000 – $100,000'),
    ('100k_500k', '$100,000 – $500,000'),
    ('500k_1m', '$500,000 – $1,000,000'),
    ('over_1m', 'Over $1,000,000'),
]

GOALS = [
    ('retirement', 'Retirement savings'),
    ('growth', 'Wealth growth'),
    ('income', 'Income generation'),
    ('preservation', 'Capital preservation'),
    ('purchase', 'Major purchase'),
]

TIME_HORIZONS = [
    ('short', 'Short-term (1–3 years)'),
    ('medium', 'Medium-term (3–7 years)'),
    ('long', 'Long-term (7–15 years)'),
    ('very_long', 'Very long-term (15+ years)'),
]

RISK_LEVELS = [
    ('conservative', 'Conservative', 'Stability over high returns'),
    ('moderate', 'Moderate', 'Balance of growth and stability'),
    ('aggressive', 'Aggressive', 'Maximize growth, tolerate volatility'),
]

FILING_STATUSES = [
    ('single', 'Single'),
    ('married_joint', 'Married Filing Jointly'),
    ('married_separate', 'Married Filing Separately'),
    ('head_household', 'Head of Household'),
]

STATES = [
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
    ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
    ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
    ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
    ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
    ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
    ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'Washington D.C.'),
]

PROFILE_OPTIONS = {
    'account_types': ACCOUNT_TYPES,
    'brokerages': BROKERAGES,
    'portfolio_sizes': PORTFOLIO_SIZES,
    'goals': GOALS,
    'time_horizons': TIME_HORIZONS,
    'risk_levels': RISK_LEVELS,
    'filing_statuses': FILING_STATUSES,
    'states': STATES,
}


def _allowed(options) -> set:
    return {o[0] for o in options}


def _choice(form, field: str, options) -> Any:
    value = (form.get(field) or '').strip()
    return value if value in _allowed(options) else None


def parse_profile_form(form) -> Tuple[Dict[str, Any], List[str]]:
    """Validate the /profile form. Returns (fields to save, error messages)."""
    errors: List[str] = []
    data: Dict[str, Any] = {
        'name': (form.get('name') or '').strip()[:100] or None,
        'account_types': [v for v in form.getlist('account_types') if v in _allowed(ACCOUNT_TYPES)],
        'brokerages': [v for v in form.getlist('brokerages') if v in _allowed(BROKERAGES)],
        'portfolio_size_range': _choice(form, 'portfolio_size_range', PORTFOLIO_SIZES),
        'primary_goal': _choice(form, 'primary_goal', GOALS),
        'time_horizon': _choice(form, 'time_horizon', TIME_HORIZONS),
        'risk_tolerance': _choice(form, 'risk_tolerance', RISK_LEVELS),
        'filing_status': _choice(form, 'filing_status', FILING_STATUSES),
        'state': _choice(form, 'state', STATES),
        'age': None,
        'target_retirement_year': None,
    }

    age = (form.get('age') or '').strip()
    if age:
        if age.isdigit() and 18 <= int(age) <= 100:
            data['age'] = int(age)
        else:
            errors.append('Age must be a whole number between 18 and 100.')

    year = (form.get('target_retirement_year') or '').strip()
    if year:
        this_year = datetime.now().year
        if year.isdigit() and this_year <= int(year) <= this_year + 60:
            data['target_retirement_year'] = int(year)
        else:
            errors.append(f'Target retirement year must be between {this_year} and {this_year + 60}.')

    return data, errors

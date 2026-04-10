from typing import Dict, Any, List
from ..models import Portfolio


# Diversified funds/ETFs that should NOT be flagged for concentration
# These hold hundreds or thousands of underlying securities
DIVERSIFIED_TICKERS = {
    # Total Market ETFs
    'VTI', 'ITOT', 'SCHB', 'SPTM', 'VT', 'VTSAX', 'VTSMX', 'FSKAX', 'FZROX',
    # S&P 500 ETFs and Mutual Funds
    'VOO', 'SPY', 'IVV', 'SPLG', 'VFIAX', 'VFINX', 'FXAIX', 'SWPPX',
    # Total Bond Market
    'BND', 'AGG', 'SCHZ', 'BNDX', 'VBTLX', 'VBMFX', 'FTBFX',
    # International
    'VXUS', 'IXUS', 'VEU', 'IEFA', 'EFA', 'VWO', 'IEMG', 'EEM', 'VTIAX', 'VGTSX',
    # Balanced/All-in-One
    'AOR', 'AOA', 'AOK', 'VBIAX', 'VBINX',
    # Money Market / Cash
    'VMFXX', 'SPAXX', 'FZFXX', 'FDRXX', 'SWVXX', 'CASH',
    # Fidelity Zero funds
    'FNILX', 'FZILX',
    # Sector ETFs (hold 100+ stocks within sector)
    'VGT', 'XLK', 'QQQ',  # Technology
    'VHT', 'XLV',  # Healthcare
    'VFH', 'XLF',  # Financials
    'VNQ', 'SCHH', 'IYR',  # Real Estate
    'VDE', 'XLE',  # Energy
    'VCR', 'XLY',  # Consumer Discretionary
    'VDC', 'XLP',  # Consumer Staples
    'VIS', 'XLI',  # Industrials
    'VAW', 'XLB',  # Materials
    'VPU', 'XLU',  # Utilities
    # Small/Mid cap ETFs
    'VB', 'IJR', 'SCHA',  # Small Cap
    'VO', 'IJH', 'SCHM',  # Mid Cap
    'VBR', 'VBK', 'IWM',  # Small Cap Value/Growth
}

# Keywords that indicate diversified funds (checked against description/ticker)
DIVERSIFIED_KEYWORDS = [
    'target date', 'target retirement', 'lifecycle', 'freedom',
    'total market', 'total stock', 'total bond', 'total intl',
    's&p 500', 'sp 500', 's&p500',
    'money market', 'cash reserve', 'treasury',
    'balanced', 'all-in-one', 'allocation',
    'index fund', 'total index',
    '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060', '2065',  # Target date years
]


def is_diversified_position(ticker: str, asset_class: str, sector: str, description: str = "") -> bool:
    """
    Check if a position is inherently diversified and shouldn't be flagged for concentration.

    Diversified positions include:
    - Target date funds (contain stocks, bonds, international)
    - Total market ETFs (hold thousands of securities)
    - Cash/Money Market (low risk)
    - Balanced/Allocation funds
    """
    ticker_upper = ticker.upper()

    # Check if it's a known diversified ticker
    if ticker_upper in DIVERSIFIED_TICKERS:
        return True

    # Check asset class
    asset_lower = asset_class.lower() if asset_class else ""
    if asset_lower in ['cash', 'money market', 'target date fund', 'balanced']:
        return True

    # Check sector
    sector_lower = sector.lower() if sector else ""
    if sector_lower in ['money market', 'target date', 'balanced', 'education savings']:
        return True

    # Check description for keywords
    desc_lower = description.lower() if description else ""
    ticker_lower = ticker.lower()
    combined = f"{desc_lower} {ticker_lower}"

    for keyword in DIVERSIFIED_KEYWORDS:
        if keyword in combined:
            return True

    return False


class ConcentrationRiskAnalyzer:
    """Analyzes concentration risk in the portfolio"""

    def __init__(self, portfolio: Portfolio, config: Dict[str, Any] = None):
        self.portfolio = portfolio
        self.config = config or {}
        self.max_position = self.config.get('risk', {}).get('max_single_position', 0.10)
        self.warning_threshold = self.config.get('risk', {}).get('concentration_warning', 0.15)

    def analyze(self) -> Dict[str, Any]:
        """Perform concentration risk analysis"""
        return {
            'concentrated_positions': self.identify_concentrated_positions(),
            'top_10_concentration': self.calculate_top_n_concentration(10),
            'risk_level': self.assess_concentration_risk(),
            'recommendations': self.generate_recommendations(),
        }

    def identify_concentrated_positions(self) -> List[Dict[str, Any]]:
        """
        Identify positions that exceed concentration thresholds.

        IMPORTANT: Excludes diversified positions like:
        - Target date funds (already contain diversified holdings)
        - Total market ETFs (hold thousands of securities)
        - Cash/Money market (low risk, not a concentration concern)
        """
        positions = self.portfolio.get_consolidated_positions()
        concentrated = []

        for ticker, data in positions.items():
            pct = data['percentage_of_portfolio']

            # Skip positions below threshold
            if pct <= self.max_position * 100:
                continue

            # Skip diversified positions - they're not concentration risks
            if is_diversified_position(
                ticker=ticker,
                asset_class=data.get('asset_class', ''),
                sector=data.get('sector', ''),
                description=data.get('description', '')
            ):
                continue

            risk_level = 'High' if pct > self.warning_threshold * 100 else 'Moderate'
            concentrated.append({
                'ticker': ticker,
                'percentage': pct,
                'market_value': data['market_value'],
                'risk_level': risk_level,
                'excess_percentage': pct - (self.max_position * 100),
            })

        return sorted(concentrated, key=lambda x: x['percentage'], reverse=True)
    
    def calculate_top_n_concentration(self, n: int) -> Dict[str, float]:
        """Calculate what percentage of portfolio is in top N positions"""
        positions = self.portfolio.get_consolidated_positions()
        
        if not positions:
            return {'top_positions': 0, 'percentage': 0.0}
        
        sorted_positions = sorted(positions.values(), 
                                 key=lambda x: x['percentage_of_portfolio'], 
                                 reverse=True)
        
        top_n = min(n, len(sorted_positions))
        top_n_pct = sum(pos['percentage_of_portfolio'] for pos in sorted_positions[:top_n])
        
        return {
            'top_positions': top_n,
            'percentage': top_n_pct,
        }
    
    def assess_concentration_risk(self) -> Dict[str, Any]:
        """
        Assess overall concentration risk level.

        Note: The top_10 percentage threshold is only meaningful when there are
        many holdings. For portfolios with <=10 holdings (common for 401k plans),
        the concentrated_positions count is the primary risk indicator.
        """
        concentrated_positions = self.identify_concentrated_positions()
        top_10 = self.calculate_top_n_concentration(10)
        total_holdings = len(self.portfolio.get_all_holdings())

        # For portfolios with few holdings (e.g., 401k plans with ~10 funds),
        # the top_10 percentage is not a useful metric since all holdings
        # would naturally be in the "top 10"
        few_holdings = total_holdings <= 12

        # Determine risk level based on actual concentrated (problematic) positions
        if len(concentrated_positions) == 0:
            # No concentrated positions = Low risk
            # (regardless of top_10 percentage for small portfolios)
            risk_level = 'Low'
            risk_score = 1
        elif len(concentrated_positions) <= 2:
            # Few concentrated positions
            if few_holdings or top_10['percentage'] < 70:
                risk_level = 'Moderate'
                risk_score = 2
            else:
                risk_level = 'High'
                risk_score = 3
        else:
            # Many concentrated positions = High risk
            risk_level = 'High'
            risk_score = 3

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'num_concentrated_positions': len(concentrated_positions),
            'top_10_percentage': top_10['percentage'],
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations to reduce concentration risk"""
        recommendations = []
        concentrated = self.identify_concentrated_positions()

        if not concentrated:
            recommendations.append("Portfolio concentration is within acceptable limits. "
                                   "Diversified funds, target date funds, and cash positions are appropriately excluded from concentration analysis.")
            return recommendations

        for position in concentrated:
            ticker = position['ticker']
            excess_pct = position['excess_percentage']
            excess_value = (excess_pct / 100) * self.portfolio.total_value

            recommendations.append(
                f"Consider reducing {ticker} position by ~${excess_value:,.0f} "
                f"({excess_pct:.1f}% of portfolio) to meet target limits."
            )

        # General recommendations
        top_10 = self.calculate_top_n_concentration(10)
        if top_10['percentage'] > 70:
            recommendations.append(
                f"Top 10 positions represent {top_10['percentage']:.1f}% of portfolio. "
                "Consider adding more positions to improve diversification."
            )

        return recommendations

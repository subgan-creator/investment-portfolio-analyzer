"""
Rebalancing Calculator Service.

Calculates specific buy/sell recommendations to reach target allocation.
"""
from typing import Dict, Any, List, Optional


# Default target allocation (can be customized)
DEFAULT_TARGET_ALLOCATION = {
    'Stocks': 0.70,
    'Bonds': 0.20,
    'Cash': 0.05,
    'Alternatives': 0.05
}

# Sector target allocation (as % of equity portion)
DEFAULT_SECTOR_TARGETS = {
    'Technology': 0.25,
    'Healthcare': 0.15,
    'Financials': 0.15,
    'Consumer Discretionary': 0.12,
    'Consumer Staples': 0.08,
    'Industrials': 0.10,
    'Energy': 0.05,
    'Utilities': 0.03,
    'Real Estate': 0.04,
    'Materials': 0.03
}

# Recommended low-cost ETFs for each asset class
RECOMMENDED_ETFS = {
    'Stocks': [
        {'ticker': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'expense_ratio': 0.03},
        {'ticker': 'SCHB', 'name': 'Schwab US Broad Market ETF', 'expense_ratio': 0.03},
        {'ticker': 'ITOT', 'name': 'iShares Core S&P Total US Stock', 'expense_ratio': 0.03},
    ],
    'International': [
        {'ticker': 'VXUS', 'name': 'Vanguard Total International Stock ETF', 'expense_ratio': 0.07},
        {'ticker': 'IXUS', 'name': 'iShares Core MSCI Total Intl Stock', 'expense_ratio': 0.07},
    ],
    'Bonds': [
        {'ticker': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'expense_ratio': 0.03},
        {'ticker': 'AGG', 'name': 'iShares Core US Aggregate Bond ETF', 'expense_ratio': 0.03},
        {'ticker': 'SCHZ', 'name': 'Schwab US Aggregate Bond ETF', 'expense_ratio': 0.03},
    ],
    'Technology': [
        {'ticker': 'VGT', 'name': 'Vanguard Information Technology ETF', 'expense_ratio': 0.10},
        {'ticker': 'QQQ', 'name': 'Invesco QQQ Trust (Nasdaq-100)', 'expense_ratio': 0.20},
    ],
    'Healthcare': [
        {'ticker': 'VHT', 'name': 'Vanguard Healthcare ETF', 'expense_ratio': 0.10},
        {'ticker': 'XLV', 'name': 'Health Care Select Sector SPDR', 'expense_ratio': 0.10},
    ],
    'Dividend': [
        {'ticker': 'VYM', 'name': 'Vanguard High Dividend Yield ETF', 'expense_ratio': 0.06},
        {'ticker': 'SCHD', 'name': 'Schwab US Dividend Equity ETF', 'expense_ratio': 0.06},
    ],
    'Small Cap': [
        {'ticker': 'VB', 'name': 'Vanguard Small-Cap ETF', 'expense_ratio': 0.05},
        {'ticker': 'IJR', 'name': 'iShares Core S&P Small-Cap ETF', 'expense_ratio': 0.06},
    ],
    'Real Estate': [
        {'ticker': 'VNQ', 'name': 'Vanguard Real Estate ETF', 'expense_ratio': 0.12},
        {'ticker': 'SCHH', 'name': 'Schwab US REIT ETF', 'expense_ratio': 0.07},
    ],
}


class RebalancingCalculator:
    """Calculates specific rebalancing recommendations."""

    def __init__(self, portfolio_data: Dict[str, Any],
                 target_allocation: Optional[Dict[str, float]] = None,
                 sector_targets: Optional[Dict[str, float]] = None):
        """
        Initialize the calculator.

        Args:
            portfolio_data: Portfolio analysis data (same format as passed to AI advisor)
            target_allocation: Optional custom target allocation
            sector_targets: Optional custom sector targets
        """
        self.portfolio_data = portfolio_data
        self.target_allocation = target_allocation or DEFAULT_TARGET_ALLOCATION
        self.sector_targets = sector_targets or DEFAULT_SECTOR_TARGETS
        self.total_value = portfolio_data.get('portfolio', {}).get('total_value', 0)

    def calculate_asset_allocation_gaps(self) -> Dict[str, Any]:
        """
        Calculate the gap between current and target asset allocation.

        Returns:
            Dict with current allocation, target, gap, and rebalancing trades
        """
        asset_allocation = self.portfolio_data.get('asset_allocation', [])

        # Convert to dict
        current = {}
        for item in asset_allocation:
            name = item.get('name', 'Other')
            # Normalize asset class names
            normalized = self._normalize_asset_class(name)
            current[normalized] = current.get(normalized, 0) + item.get('percent', 0) / 100

        # Calculate gaps and trades
        gaps = []
        trades = []

        for asset_class, target_pct in self.target_allocation.items():
            current_pct = current.get(asset_class, 0)
            gap_pct = target_pct - current_pct
            gap_value = gap_pct * self.total_value

            gaps.append({
                'asset_class': asset_class,
                'current_percent': current_pct * 100,
                'target_percent': target_pct * 100,
                'gap_percent': gap_pct * 100,
                'gap_value': gap_value
            })

            # Generate trade if gap exceeds 2%
            if abs(gap_pct) >= 0.02:
                action = 'BUY' if gap_pct > 0 else 'REDUCE'
                trades.append({
                    'action': action,
                    'asset_class': asset_class,
                    'amount': abs(gap_value),
                    'percent_change': abs(gap_pct) * 100,
                    'suggested_etfs': RECOMMENDED_ETFS.get(asset_class, [])[:2]
                })

        return {
            'gaps': sorted(gaps, key=lambda x: abs(x['gap_percent']), reverse=True),
            'trades': sorted(trades, key=lambda x: x['amount'], reverse=True),
            'is_balanced': all(abs(g['gap_percent']) < 5 for g in gaps)
        }

    def calculate_sector_gaps(self) -> Dict[str, Any]:
        """
        Calculate sector allocation gaps (for equity portion only).

        Returns:
            Dict with sector analysis and recommendations
        """
        sector_allocation = self.portfolio_data.get('sector_allocation', [])

        # Convert to dict
        current = {}
        for item in sector_allocation:
            name = item.get('name', 'Other')
            current[name] = item.get('percent', 0) / 100

        # Calculate gaps
        gaps = []
        overweight = []
        underweight = []

        for sector, target_pct in self.sector_targets.items():
            current_pct = current.get(sector, 0)
            gap_pct = target_pct - current_pct

            gap_info = {
                'sector': sector,
                'current_percent': current_pct * 100,
                'target_percent': target_pct * 100,
                'gap_percent': gap_pct * 100
            }
            gaps.append(gap_info)

            if gap_pct > 0.05:  # More than 5% underweight
                underweight.append({
                    'sector': sector,
                    'gap_percent': gap_pct * 100,
                    'suggested_etfs': RECOMMENDED_ETFS.get(sector, [])[:1]
                })
            elif gap_pct < -0.05:  # More than 5% overweight
                overweight.append({
                    'sector': sector,
                    'excess_percent': abs(gap_pct) * 100
                })

        return {
            'gaps': sorted(gaps, key=lambda x: abs(x['gap_percent']), reverse=True),
            'overweight': overweight,
            'underweight': underweight
        }

    def identify_missing_diversification(self) -> Dict[str, Any]:
        """
        Identify missing asset classes or sectors that could improve diversification.

        Returns:
            Dict with missing allocations and recommendations
        """
        asset_allocation = self.portfolio_data.get('asset_allocation', [])
        sector_allocation = self.portfolio_data.get('sector_allocation', [])

        # Check current asset classes
        current_assets = {self._normalize_asset_class(a['name']) for a in asset_allocation if a.get('percent', 0) > 1}

        # Check for missing major asset classes
        missing_assets = []
        for asset_class in ['Bonds', 'International', 'Real Estate']:
            if asset_class not in current_assets:
                missing_assets.append({
                    'asset_class': asset_class,
                    'reason': f'No {asset_class.lower()} exposure detected',
                    'suggested_etfs': RECOMMENDED_ETFS.get(asset_class, [])[:2],
                    'suggested_allocation': self.target_allocation.get(asset_class, 0.10) * 100
                })

        # Check for international exposure specifically
        top_holdings = self.portfolio_data.get('top_holdings', [])
        has_international = any(
            h.get('ticker', '') in ['VXUS', 'IXUS', 'VEU', 'VWO', 'IEMG', 'EFA', 'EEM']
            for h in top_holdings
        )

        if not has_international and 'International' not in [m['asset_class'] for m in missing_assets]:
            missing_assets.append({
                'asset_class': 'International',
                'reason': 'Limited international diversification',
                'suggested_etfs': RECOMMENDED_ETFS.get('International', []),
                'suggested_allocation': 20
            })

        return {
            'missing_assets': missing_assets,
            'recommendation_count': len(missing_assets)
        }

    def analyze_concentration_fixes(self) -> List[Dict[str, Any]]:
        """
        Generate specific recommendations to fix concentration issues.

        Returns:
            List of specific actions to reduce concentration
        """
        concentration = self.portfolio_data.get('concentration', {})
        concentrated_positions = concentration.get('concentrated_positions', [])

        fixes = []
        for pos in concentrated_positions:
            ticker = pos.get('ticker', 'Unknown')
            current_pct = pos.get('percentage', 0)
            target_pct = 10  # Max 10% per position
            excess_pct = current_pct - target_pct

            if excess_pct > 0:
                excess_value = (excess_pct / 100) * self.total_value
                fixes.append({
                    'action': 'REDUCE',
                    'ticker': ticker,
                    'current_percent': current_pct,
                    'target_percent': target_pct,
                    'reduce_by_percent': excess_pct,
                    'reduce_by_value': excess_value,
                    'reason': f'{ticker} exceeds 10% position limit',
                    'suggestion': f'Consider selling ${excess_value:,.0f} of {ticker} and diversifying into underweight sectors'
                })

        return fixes

    def generate_action_plan(self) -> Dict[str, Any]:
        """
        Generate a complete action plan with prioritized recommendations.

        Returns:
            Dict with prioritized actions and summary
        """
        allocation_gaps = self.calculate_asset_allocation_gaps()
        sector_gaps = self.calculate_sector_gaps()
        missing = self.identify_missing_diversification()
        concentration_fixes = self.analyze_concentration_fixes()

        # Prioritize actions
        priority_actions = []

        # Priority 1: Fix concentration issues
        for fix in concentration_fixes:
            priority_actions.append({
                'priority': 1,
                'category': 'Concentration Risk',
                'action': fix['action'],
                'description': fix['suggestion'],
                'amount': fix['reduce_by_value'],
                'ticker': fix['ticker']
            })

        # Priority 2: Add missing asset classes
        for missing_asset in missing['missing_assets']:
            amount = (missing_asset['suggested_allocation'] / 100) * self.total_value
            etfs = missing_asset.get('suggested_etfs', [])
            etf_text = f" using {etfs[0]['ticker']}" if etfs else ""
            priority_actions.append({
                'priority': 2,
                'category': 'Diversification',
                'action': 'BUY',
                'description': f"Add {missing_asset['asset_class']} exposure{etf_text}",
                'amount': amount,
                'suggested_etfs': etfs
            })

        # Priority 3: Rebalance asset allocation
        for trade in allocation_gaps['trades'][:3]:
            etfs = trade.get('suggested_etfs', [])
            etf_text = f" ({etfs[0]['ticker']})" if etfs else ""
            priority_actions.append({
                'priority': 3,
                'category': 'Rebalancing',
                'action': trade['action'],
                'description': f"{trade['action']} {trade['asset_class']}{etf_text}",
                'amount': trade['amount'],
                'percent_change': trade['percent_change'],
                'suggested_etfs': etfs
            })

        # Summary stats
        total_buy = sum(a['amount'] for a in priority_actions if a['action'] == 'BUY')
        total_reduce = sum(a['amount'] for a in priority_actions if a['action'] == 'REDUCE')

        return {
            'actions': priority_actions,
            'summary': {
                'total_recommended_purchases': total_buy,
                'total_recommended_reductions': total_reduce,
                'action_count': len(priority_actions),
                'portfolio_is_balanced': allocation_gaps['is_balanced'] and len(concentration_fixes) == 0
            },
            'allocation_analysis': allocation_gaps,
            'sector_analysis': sector_gaps,
            'missing_diversification': missing,
            'concentration_fixes': concentration_fixes
        }

    def _normalize_asset_class(self, name: str) -> str:
        """Normalize asset class names for comparison."""
        name_lower = name.lower()

        if any(x in name_lower for x in ['stock', 'equity', 'etf', 'fund']):
            return 'Stocks'
        elif any(x in name_lower for x in ['bond', 'fixed', 'treasury', 'income']):
            return 'Bonds'
        elif any(x in name_lower for x in ['cash', 'money market', 'savings']):
            return 'Cash'
        elif any(x in name_lower for x in ['alternative', 'commodity', 'crypto', 'gold']):
            return 'Alternatives'
        elif any(x in name_lower for x in ['international', 'foreign', 'emerging', 'global']):
            return 'International'
        elif any(x in name_lower for x in ['real estate', 'reit']):
            return 'Real Estate'
        else:
            return 'Stocks'  # Default to stocks

    def format_for_ai_context(self) -> str:
        """
        Format the rebalancing analysis as context for the AI advisor.

        Returns:
            String formatted for inclusion in AI system prompt
        """
        action_plan = self.generate_action_plan()

        context = "\n\nREBALANCING ANALYSIS:\n"

        # Summary
        summary = action_plan['summary']
        if summary['portfolio_is_balanced']:
            context += "Portfolio Status: Well-balanced, minor adjustments recommended\n"
        else:
            context += "Portfolio Status: Rebalancing recommended\n"

        # Allocation gaps
        context += "\nAsset Allocation Gaps:\n"
        for gap in action_plan['allocation_analysis']['gaps'][:4]:
            direction = "UNDERWEIGHT" if gap['gap_percent'] > 0 else "OVERWEIGHT"
            context += f"- {gap['asset_class']}: {gap['current_percent']:.1f}% (target {gap['target_percent']:.1f}%) - {direction} by {abs(gap['gap_percent']):.1f}%\n"

        # Concentration issues
        if action_plan['concentration_fixes']:
            context += "\nConcentration Issues to Address:\n"
            for fix in action_plan['concentration_fixes']:
                context += f"- {fix['ticker']}: {fix['current_percent']:.1f}% - REDUCE by ${fix['reduce_by_value']:,.0f}\n"

        # Missing diversification
        missing = action_plan['missing_diversification']
        if missing['missing_assets']:
            context += "\nMissing Diversification:\n"
            for m in missing['missing_assets']:
                etf = m['suggested_etfs'][0]['ticker'] if m['suggested_etfs'] else 'N/A'
                context += f"- No {m['asset_class']} exposure (suggest {m['suggested_allocation']:.0f}% via {etf})\n"

        # Specific trades
        context += "\nSPECIFIC RECOMMENDED TRADES:\n"
        for action in action_plan['actions'][:5]:
            if action['action'] == 'BUY':
                etfs = action.get('suggested_etfs', [])
                if etfs:
                    context += f"- BUY ${action['amount']:,.0f} of {etfs[0]['ticker']} ({etfs[0]['name']})\n"
                else:
                    context += f"- BUY ${action['amount']:,.0f} in {action['description']}\n"
            else:
                context += f"- {action['description']}: ${action['amount']:,.0f}\n"

        return context


def calculate_rebalancing(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to calculate rebalancing recommendations.

    Args:
        portfolio_data: Portfolio analysis data

    Returns:
        Complete action plan with recommendations
    """
    calculator = RebalancingCalculator(portfolio_data)
    return calculator.generate_action_plan()

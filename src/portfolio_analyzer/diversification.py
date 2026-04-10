from typing import Dict, Any, List
import numpy as np
from ..models import Portfolio


class DiversificationAnalyzer:
    """Analyzes portfolio diversification"""
    
    def __init__(self, portfolio: Portfolio, config: Dict[str, Any] = None):
        self.portfolio = portfolio
        self.config = config or {}
    
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive diversification analysis"""
        return {
            'herfindahl_index': self.calculate_herfindahl_index(),
            'number_of_holdings': len(self.portfolio.get_all_holdings()),
            'number_of_positions': len(self.portfolio.get_consolidated_positions()),
            'asset_class_diversity': self.analyze_asset_class_diversity(),
            'sector_diversity': self.analyze_sector_diversity(),
            'diversification_score': self.calculate_diversification_score(),
        }
    
    def calculate_herfindahl_index(self) -> float:
        """
        Calculate Herfindahl-Hirschman Index (HHI) for concentration.
        Lower values indicate better diversification.
        Range: 0 (perfect diversification) to 10,000 (complete concentration)
        """
        positions = self.portfolio.get_consolidated_positions()
        
        if not positions:
            return 0.0
        
        # Calculate squared percentage weights
        hhi = sum((pos['percentage_of_portfolio'] ** 2) for pos in positions.values())
        
        return hhi
    
    def analyze_asset_class_diversity(self) -> Dict[str, Any]:
        """Analyze diversification across asset classes"""
        allocation = self.portfolio.get_asset_allocation()
        target = self.config.get('allocation', {}).get('target', {})
        
        num_asset_classes = len(allocation)
        
        return {
            'num_asset_classes': num_asset_classes,
            'current_allocation': allocation,
            'target_allocation': {k: v * 100 for k, v in target.items()} if target else {},
            'is_well_diversified': num_asset_classes >= 3,
        }
    
    def analyze_sector_diversity(self) -> Dict[str, Any]:
        """Analyze diversification across sectors"""
        sector_allocation = self.portfolio.get_sector_allocation()
        sector_limits = self.config.get('allocation', {}).get('sector_limits', {})
        
        violations = []
        for sector, current_pct in sector_allocation.items():
            limit = sector_limits.get(sector.lower(), 1.0) * 100  # Convert to percentage
            if current_pct > limit:
                violations.append({
                    'sector': sector,
                    'current_percentage': current_pct,
                    'limit': limit,
                    'excess': current_pct - limit,
                })
        
        return {
            'num_sectors': len(sector_allocation),
            'current_allocation': sector_allocation,
            'limit_violations': violations,
            'is_well_diversified': len(sector_allocation) >= 5,
        }
    
    def _detect_target_date_funds(self) -> tuple:
        """
        Detect Target Date Funds in the portfolio.
        Returns (count, total_percentage) of target date fund holdings.

        Target Date Funds are internally diversified (containing hundreds of
        stocks and bonds), so portfolios with significant TDF allocation
        should not be penalized for low holding counts.
        """
        target_date_count = 0
        target_date_value = 0.0

        for holding in self.portfolio.get_all_holdings():
            description = getattr(holding, 'description', '').lower()
            ticker = holding.ticker.lower() if holding.ticker else ''

            # Check for target date fund indicators
            is_target_date = any([
                'target date' in description,
                'target' in description and any(str(year) in description for year in range(2020, 2070)),
                'lifecycle' in description,
                'retirement' in description and any(str(year) in description for year in range(2020, 2070)),
                'tgt' in ticker and any(str(year) in ticker for year in range(2020, 2070)),
            ])

            if is_target_date:
                target_date_count += 1
                target_date_value += holding.market_value

        total_value = self.portfolio.total_value
        target_date_percentage = (target_date_value / total_value * 100) if total_value > 0 else 0

        return target_date_count, target_date_percentage

    def calculate_diversification_score(self) -> Dict[str, Any]:
        """
        Calculate an overall diversification score (0-100).
        Higher is better.

        Note: Target Date Funds are recognized as internally diversified.
        Portfolios with significant TDF allocation receive adjusted scoring
        since TDFs contain hundreds of underlying stocks and bonds.
        """
        score = 100
        feedback = []

        # Detect Target Date Funds
        tdf_count, tdf_percentage = self._detect_target_date_funds()
        has_significant_tdf = tdf_percentage >= 20  # 20%+ in TDFs

        # Check number of holdings
        num_holdings = len(self.portfolio.get_all_holdings())
        min_holdings = self.config.get('risk', {}).get('min_holdings', 15)

        # Adjust minimum holdings requirement if portfolio has significant TDF allocation
        # TDFs are internally diversified with hundreds of underlying holdings
        if has_significant_tdf:
            # Each TDF counts as ~10 effective holdings due to internal diversification
            effective_holdings = num_holdings + (tdf_count * 9)  # Add 9 extra per TDF
            if effective_holdings < min_holdings:
                penalty = min(15, (min_holdings - effective_holdings) * 2)  # Reduced penalty
                score -= penalty
                feedback.append(f"Portfolio has {num_holdings} holdings ({tdf_count} Target Date Funds provide additional diversification)")
        else:
            if num_holdings < min_holdings:
                penalty = min(30, (min_holdings - num_holdings) * 3)
                score -= penalty
                feedback.append(f"Portfolio has only {num_holdings} holdings (recommended: {min_holdings}+)")

        # Check HHI - but adjust threshold for TDF-heavy portfolios
        hhi = self.calculate_herfindahl_index()
        hhi_threshold = 2500 if has_significant_tdf else 2000  # Higher threshold for TDF portfolios

        if hhi > hhi_threshold:
            # Reduced penalty for TDF portfolios since concentration in TDFs is acceptable
            penalty_divisor = 150 if has_significant_tdf else 100
            penalty = min(15 if has_significant_tdf else 20, (hhi - hhi_threshold) / penalty_divisor)
            score -= penalty
            if has_significant_tdf:
                feedback.append(f"High allocation to Target Date Funds (HHI: {hhi:.0f}) - acceptable for TDF strategy")
            else:
                feedback.append(f"High concentration detected (HHI: {hhi:.0f})")

        # Check asset class diversity
        num_asset_classes = len(self.portfolio.get_asset_allocation())
        # TDFs inherently contain multiple asset classes
        if num_asset_classes < 3 and not has_significant_tdf:
            score -= 20
            feedback.append(f"Limited asset class diversity ({num_asset_classes} classes)")
        elif num_asset_classes < 3 and has_significant_tdf:
            # TDFs contain stocks, bonds, and often international - skip penalty
            feedback.append(f"Target Date Funds provide built-in multi-asset diversification")

        # Check sector diversity
        num_sectors = len(self.portfolio.get_sector_allocation())
        # TDFs cover all sectors internally
        if num_sectors < 5 and not has_significant_tdf:
            score -= 15
            feedback.append(f"Limited sector diversity ({num_sectors} sectors)")
        elif num_sectors < 5 and has_significant_tdf:
            # TDFs contain all major sectors - skip penalty
            pass  # No penalty needed

        # Bonus for well-structured TDF portfolios
        if has_significant_tdf and tdf_percentage >= 50:
            score = min(100, score + 10)  # Bonus for TDF-centric strategy
            feedback.append(f"Well-diversified via Target Date Funds ({tdf_percentage:.0f}% of portfolio)")
        
        score = max(0, int(round(score)))  # Ensure score doesn't go negative and is an integer

        # Determine rating
        if score >= 80:
            rating = "Excellent"
        elif score >= 60:
            rating = "Good"
        elif score >= 40:
            rating = "Fair"
        else:
            rating = "Poor"
        
        return {
            'score': score,
            'rating': rating,
            'feedback': feedback,
        }

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
    
    def calculate_diversification_score(self) -> Dict[str, Any]:
        """
        Calculate an overall diversification score (0-100).
        Higher is better.
        """
        score = 100
        feedback = []
        
        # Check number of holdings
        num_holdings = len(self.portfolio.get_all_holdings())
        min_holdings = self.config.get('risk', {}).get('min_holdings', 15)
        
        if num_holdings < min_holdings:
            penalty = min(30, (min_holdings - num_holdings) * 3)
            score -= penalty
            feedback.append(f"Portfolio has only {num_holdings} holdings (recommended: {min_holdings}+)")
        
        # Check HHI
        hhi = self.calculate_herfindahl_index()
        if hhi > 2000:
            penalty = min(20, (hhi - 2000) / 100)
            score -= penalty
            feedback.append(f"High concentration detected (HHI: {hhi:.0f})")
        
        # Check asset class diversity
        num_asset_classes = len(self.portfolio.get_asset_allocation())
        if num_asset_classes < 3:
            score -= 20
            feedback.append(f"Limited asset class diversity ({num_asset_classes} classes)")
        
        # Check sector diversity
        num_sectors = len(self.portfolio.get_sector_allocation())
        if num_sectors < 5:
            score -= 15
            feedback.append(f"Limited sector diversity ({num_sectors} sectors)")
        
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

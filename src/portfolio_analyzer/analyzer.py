from typing import Dict, List, Any
from ..models import Portfolio
from .diversification import DiversificationAnalyzer
from .concentration import ConcentrationRiskAnalyzer


class PortfolioAnalyzer:
    """Main analyzer that coordinates various portfolio analysis functions"""
    
    def __init__(self, portfolio: Portfolio, config: Dict[str, Any] = None):
        self.portfolio = portfolio
        self.config = config or {}
        self.diversification_analyzer = DiversificationAnalyzer(portfolio, config)
        self.concentration_analyzer = ConcentrationRiskAnalyzer(portfolio, config)
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive portfolio summary"""
        return {
            'total_value': self.portfolio.total_value,
            'total_cost_basis': self.portfolio.total_cost_basis,
            'total_unrealized_gain_loss': self.portfolio.total_unrealized_gain_loss,
            'return_percentage': (self.portfolio.total_unrealized_gain_loss / 
                                 self.portfolio.total_cost_basis * 100) 
                                 if self.portfolio.total_cost_basis > 0 else 0,
            'num_accounts': len(self.portfolio.accounts),
            'num_positions': len(self.portfolio.get_consolidated_positions()),
            'num_holdings': len(self.portfolio.get_all_holdings()),
        }
    
    def analyze_diversification(self) -> Dict[str, Any]:
        """Analyze portfolio diversification"""
        return self.diversification_analyzer.analyze()
    
    def analyze_concentration_risk(self) -> Dict[str, Any]:
        """Analyze concentration risk"""
        return self.concentration_analyzer.analyze()
    
    def get_rebalancing_recommendations(self) -> List[Dict[str, Any]]:
        """Generate rebalancing recommendations"""
        recommendations = []
        
        # Get current vs target allocation
        current_allocation = self.portfolio.get_asset_allocation()
        target_allocation = self.config.get('allocation', {}).get('target', {})
        
        if not target_allocation:
            return recommendations
        
        threshold = self.config.get('analysis', {}).get('rebalance_threshold', 0.05)
        
        for asset_class, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_class, 0) / 100  # Convert to decimal
            target_pct_decimal = target_pct
            deviation = abs(current_pct - target_pct_decimal)
            
            if deviation > threshold:
                diff_value = (current_pct - target_pct_decimal) * self.portfolio.total_value
                
                recommendations.append({
                    'asset_class': asset_class,
                    'current_percentage': current_pct * 100,
                    'target_percentage': target_pct_decimal * 100,
                    'deviation': deviation * 100,
                    'action': 'reduce' if diff_value > 0 else 'increase',
                    'amount': abs(diff_value),
                })
        
        return sorted(recommendations, key=lambda x: x['deviation'], reverse=True)
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analysis report"""
        return {
            'summary': self.get_portfolio_summary(),
            'asset_allocation': self.portfolio.get_asset_allocation(),
            'sector_allocation': self.portfolio.get_sector_allocation(),
            'diversification': self.analyze_diversification(),
            'concentration_risk': self.analyze_concentration_risk(),
            'rebalancing_recommendations': self.get_rebalancing_recommendations(),
            'top_positions': self._get_top_positions(10),
        }
    
    def _get_top_positions(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get top N positions by value"""
        positions = self.portfolio.get_consolidated_positions()
        sorted_positions = sorted(positions.values(), 
                                 key=lambda x: x['market_value'], 
                                 reverse=True)
        return sorted_positions[:n]

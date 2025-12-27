from typing import Dict, Any, List
from ..models import Portfolio


class ConcentrationRiskAnalyzer:
    """Analyzes concentration risk in the portfolio"""
    
    def __init__(self, portfolio: Portfolio, config: Dict[str, Any] = None):
        self.portfolio = portfolio
        self.config = config or {}
        self.max_position = config.get('risk', {}).get('max_single_position', 0.10)
        self.warning_threshold = config.get('risk', {}).get('concentration_warning', 0.15)
    
    def analyze(self) -> Dict[str, Any]:
        """Perform concentration risk analysis"""
        return {
            'concentrated_positions': self.identify_concentrated_positions(),
            'top_10_concentration': self.calculate_top_n_concentration(10),
            'risk_level': self.assess_concentration_risk(),
            'recommendations': self.generate_recommendations(),
        }
    
    def identify_concentrated_positions(self) -> List[Dict[str, Any]]:
        """Identify positions that exceed concentration thresholds"""
        positions = self.portfolio.get_consolidated_positions()
        concentrated = []
        
        for ticker, data in positions.items():
            pct = data['percentage_of_portfolio']
            
            if pct > self.max_position * 100:
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
        """Assess overall concentration risk level"""
        concentrated_positions = self.identify_concentrated_positions()
        top_10 = self.calculate_top_n_concentration(10)
        
        # Determine risk level
        if len(concentrated_positions) == 0 and top_10['percentage'] < 50:
            risk_level = 'Low'
            risk_score = 1
        elif len(concentrated_positions) <= 2 and top_10['percentage'] < 70:
            risk_level = 'Moderate'
            risk_score = 2
        else:
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
            recommendations.append("Portfolio concentration is within acceptable limits.")
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

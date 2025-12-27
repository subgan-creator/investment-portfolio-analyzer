from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..models import Portfolio, Holding


class TaxOptimizer:
    """Analyzes tax optimization opportunities"""
    
    def __init__(self, portfolio: Portfolio, config: Dict[str, Any] = None):
        self.portfolio = portfolio
        self.config = config or {}
        self.federal_rate = config.get('tax', {}).get('federal_bracket', 0.24)
        self.state_rate = config.get('tax', {}).get('state_bracket', 0.05)
        self.ltcg_rate = config.get('tax', {}).get('long_term_cap_gains', 0.15)
    
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive tax analysis"""
        return {
            'tax_loss_harvesting': self.identify_tax_loss_harvesting_opportunities(),
            'capital_gains_summary': self.calculate_capital_gains_summary(),
            'tax_efficiency_score': self.calculate_tax_efficiency_score(),
            'recommendations': self.generate_tax_recommendations(),
        }
    
    def identify_tax_loss_harvesting_opportunities(self) -> List[Dict[str, Any]]:
        """Identify positions with unrealized losses for tax-loss harvesting"""
        opportunities = []
        
        for account in self.portfolio.accounts:
            # Only consider taxable accounts
            if account.tax_status != 'taxable':
                continue
            
            for holding in account.holdings:
                if holding.unrealized_gain_loss < 0:
                    potential_tax_savings = abs(holding.unrealized_gain_loss) * (
                        self.federal_rate + self.state_rate
                    )
                    
                    opportunities.append({
                        'ticker': holding.ticker,
                        'account': account.account_name,
                        'unrealized_loss': holding.unrealized_gain_loss,
                        'market_value': holding.market_value,
                        'cost_basis': holding.total_cost_basis,
                        'potential_tax_savings': potential_tax_savings,
                        'holding_period_days': holding.holding_period_days,
                        'is_long_term': holding.is_long_term,
                    })
        
        return sorted(opportunities, key=lambda x: abs(x['unrealized_loss']), reverse=True)
    
    def calculate_capital_gains_summary(self) -> Dict[str, Any]:
        """Calculate summary of unrealized capital gains by holding period"""
        short_term_gains = 0.0
        short_term_losses = 0.0
        long_term_gains = 0.0
        long_term_losses = 0.0
        
        for account in self.portfolio.accounts:
            # Only consider taxable accounts for capital gains tax
            if account.tax_status != 'taxable':
                continue
            
            for holding in account.holdings:
                gain_loss = holding.unrealized_gain_loss
                
                if holding.is_long_term:
                    if gain_loss > 0:
                        long_term_gains += gain_loss
                    else:
                        long_term_losses += abs(gain_loss)
                else:
                    if gain_loss > 0:
                        short_term_gains += gain_loss
                    else:
                        short_term_losses += abs(gain_loss)
        
        # Calculate net gains
        net_short_term = short_term_gains - short_term_losses
        net_long_term = long_term_gains - long_term_losses
        
        # Estimate tax liability
        short_term_tax = max(0, net_short_term) * (self.federal_rate + self.state_rate)
        long_term_tax = max(0, net_long_term) * (self.ltcg_rate + self.state_rate)
        total_estimated_tax = short_term_tax + long_term_tax
        
        return {
            'short_term': {
                'gains': short_term_gains,
                'losses': short_term_losses,
                'net': net_short_term,
                'estimated_tax': short_term_tax,
            },
            'long_term': {
                'gains': long_term_gains,
                'losses': long_term_losses,
                'net': net_long_term,
                'estimated_tax': long_term_tax,
            },
            'total_estimated_tax_liability': total_estimated_tax,
        }
    
    def calculate_tax_efficiency_score(self) -> Dict[str, Any]:
        """Calculate tax efficiency score (0-100)"""
        score = 100
        feedback = []
        
        # Check for unharvested losses in taxable accounts
        tlh_opportunities = self.identify_tax_loss_harvesting_opportunities()
        if tlh_opportunities:
            total_unharvested_loss = sum(abs(opp['unrealized_loss']) 
                                        for opp in tlh_opportunities)
            if total_unharvested_loss > 5000:
                penalty = min(30, total_unharvested_loss / 1000)
                score -= penalty
                feedback.append(
                    f"${total_unharvested_loss:,.0f} in unharvested losses available"
                )
        
        # Check account type allocation (prefer tax-advantaged for high-growth assets)
        # This is a simplified check - could be more sophisticated
        taxable_value = sum(acc.total_value for acc in self.portfolio.accounts 
                          if acc.tax_status == 'taxable')
        total_value = self.portfolio.total_value
        
        if total_value > 0:
            taxable_pct = (taxable_value / total_value) * 100
            if taxable_pct > 70:
                score -= 15
                feedback.append(
                    f"{taxable_pct:.0f}% of portfolio is in taxable accounts"
                )
        
        # Check for short-term gains that could become long-term
        cap_gains = self.calculate_capital_gains_summary()
        if cap_gains['short_term']['gains'] > 10000:
            score -= 10
            feedback.append(
                f"${cap_gains['short_term']['gains']:,.0f} in short-term gains"
            )
        
        score = max(0, score)
        
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
    
    def generate_tax_recommendations(self) -> List[str]:
        """Generate actionable tax optimization recommendations"""
        recommendations = []
        
        # Tax-loss harvesting recommendations
        tlh_opportunities = self.identify_tax_loss_harvesting_opportunities()
        if tlh_opportunities:
            top_losses = tlh_opportunities[:3]
            total_potential_savings = sum(opp['potential_tax_savings'] 
                                        for opp in top_losses)
            recommendations.append(
                f"Consider tax-loss harvesting on {len(tlh_opportunities)} positions. "
                f"Top 3 opportunities could save ~${total_potential_savings:,.0f} in taxes."
            )
        
        # Capital gains recommendations
        cap_gains = self.calculate_capital_gains_summary()
        if cap_gains['total_estimated_tax_liability'] > 10000:
            recommendations.append(
                f"Estimated tax liability on unrealized gains: ${cap_gains['total_estimated_tax_liability']:,.0f}. "
                "Consider strategic selling to manage tax impact."
            )
        
        # Short-term vs long-term
        if cap_gains['short_term']['gains'] > 5000:
            recommendations.append(
                f"${cap_gains['short_term']['gains']:,.0f} in short-term gains. "
                "Consider holding positions longer to qualify for lower long-term rates."
            )
        
        # Account location optimization
        taxable_accounts = [acc for acc in self.portfolio.accounts 
                          if acc.tax_status == 'taxable']
        if taxable_accounts:
            recommendations.append(
                "Review asset location: Consider holding tax-efficient investments "
                "(index funds, municipal bonds) in taxable accounts and "
                "tax-inefficient investments (REITs, bonds) in tax-advantaged accounts."
            )
        
        if not recommendations:
            recommendations.append("Portfolio is reasonably tax-efficient. Continue monitoring for opportunities.")
        
        return recommendations

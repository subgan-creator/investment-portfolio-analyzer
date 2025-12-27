import json
from typing import Dict, Any
from ..models import Portfolio
from ..portfolio_analyzer import PortfolioAnalyzer
from ..portfolio_analyzer.tax_optimizer import TaxOptimizer


class PortfolioReporter:
    """Generate reports and visualizations for portfolio analysis"""
    
    def __init__(self, portfolio: Portfolio, config: Dict[str, Any] = None):
        self.portfolio = portfolio
        self.config = config or {}
        self.analyzer = PortfolioAnalyzer(portfolio, config)
        self.tax_optimizer = TaxOptimizer(portfolio, config)
    
    def generate_text_report(self) -> str:
        """Generate a comprehensive text-based report"""
        report = []
        report.append("=" * 80)
        report.append("INVESTMENT PORTFOLIO ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Portfolio Summary
        report.append("PORTFOLIO SUMMARY")
        report.append("-" * 80)
        summary = self.analyzer.get_portfolio_summary()
        report.append(f"Total Value:               ${summary['total_value']:>20,.2f}")
        report.append(f"Total Cost Basis:          ${summary['total_cost_basis']:>20,.2f}")
        report.append(f"Unrealized Gain/Loss:      ${summary['total_unrealized_gain_loss']:>20,.2f}")
        report.append(f"Return:                    {summary['return_percentage']:>20,.2f}%")
        report.append(f"Number of Accounts:        {summary['num_accounts']:>20}")
        report.append(f"Number of Positions:       {summary['num_positions']:>20}")
        report.append("")
        
        # Asset Allocation
        report.append("ASSET ALLOCATION")
        report.append("-" * 80)
        asset_allocation = self.portfolio.get_asset_allocation()
        for asset_class, percentage in sorted(asset_allocation.items(), 
                                             key=lambda x: x[1], reverse=True):
            value = (percentage / 100) * self.portfolio.total_value
            report.append(f"{asset_class:<30} {percentage:>6.2f}%    ${value:>15,.2f}")
        report.append("")
        
        # Top Holdings
        report.append("TOP 10 HOLDINGS")
        report.append("-" * 80)
        positions = self.portfolio.get_consolidated_positions()
        sorted_positions = sorted(positions.values(), 
                                 key=lambda x: x['market_value'], 
                                 reverse=True)[:10]
        
        for i, pos in enumerate(sorted_positions, 1):
            report.append(
                f"{i:>2}. {pos['ticker']:<10} "
                f"{pos['percentage_of_portfolio']:>6.2f}%    "
                f"${pos['market_value']:>15,.2f}    "
                f"Gain/Loss: ${pos['unrealized_gain_loss']:>12,.2f}"
            )
        report.append("")
        
        # Diversification Analysis
        report.append("DIVERSIFICATION ANALYSIS")
        report.append("-" * 80)
        diversification = self.analyzer.analyze_diversification()
        div_score = diversification['diversification_score']
        report.append(f"Diversification Score:     {div_score['score']:>20.0f}/100")
        report.append(f"Rating:                    {div_score['rating']:>20}")
        report.append(f"Herfindahl Index:          {diversification['herfindahl_index']:>20.2f}")
        report.append(f"Number of Holdings:        {diversification['number_of_holdings']:>20}")
        
        if div_score['feedback']:
            report.append("\nFeedback:")
            for feedback in div_score['feedback']:
                report.append(f"  - {feedback}")
        report.append("")
        
        # Concentration Risk
        report.append("CONCENTRATION RISK ANALYSIS")
        report.append("-" * 80)
        concentration = self.analyzer.analyze_concentration_risk()
        risk_level = concentration['risk_level']
        report.append(f"Risk Level:                {risk_level['risk_level']:>20}")
        report.append(f"Concentrated Positions:    {risk_level['num_concentrated_positions']:>20}")
        report.append(f"Top 10 Concentration:      {risk_level['top_10_percentage']:>20.2f}%")
        
        concentrated_pos = concentration['concentrated_positions']
        if concentrated_pos:
            report.append("\nConcentrated Positions:")
            for pos in concentrated_pos:
                report.append(
                    f"  {pos['ticker']:<10} {pos['percentage']:>6.2f}%    "
                    f"Risk: {pos['risk_level']}"
                )
        report.append("")
        
        # Tax Analysis
        report.append("TAX OPTIMIZATION ANALYSIS")
        report.append("-" * 80)
        tax_analysis = self.tax_optimizer.analyze()
        tax_score = tax_analysis['tax_efficiency_score']
        report.append(f"Tax Efficiency Score:      {tax_score['score']:>20.0f}/100")
        report.append(f"Rating:                    {tax_score['rating']:>20}")
        
        cap_gains = tax_analysis['capital_gains_summary']
        report.append(f"\nEstimated Tax Liability:   ${cap_gains['total_estimated_tax_liability']:>20,.2f}")
        report.append(f"  Short-term gains:        ${cap_gains['short_term']['net']:>20,.2f}")
        report.append(f"  Long-term gains:         ${cap_gains['long_term']['net']:>20,.2f}")
        
        tlh_opps = tax_analysis['tax_loss_harvesting']
        if tlh_opps:
            report.append(f"\nTax-Loss Harvesting Opportunities: {len(tlh_opps)}")
            for opp in tlh_opps[:5]:
                report.append(
                    f"  {opp['ticker']:<10} Loss: ${abs(opp['unrealized_loss']):>12,.2f}    "
                    f"Potential Savings: ${opp['potential_tax_savings']:>10,.2f}"
                )
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 80)
        
        report.append("\nRebalancing Recommendations:")
        rebalancing = self.analyzer.get_rebalancing_recommendations()
        if rebalancing:
            for rec in rebalancing[:5]:
                report.append(
                    f"  {rec['asset_class']}: {rec['action'].upper()} by "
                    f"${rec['amount']:,.0f} "
                    f"(current: {rec['current_percentage']:.1f}%, "
                    f"target: {rec['target_percentage']:.1f}%)"
                )
        else:
            report.append("  Portfolio is well-balanced relative to targets.")
        
        report.append("\nConcentration Risk Recommendations:")
        for rec in concentration['recommendations'][:3]:
            report.append(f"  - {rec}")
        
        report.append("\nTax Optimization Recommendations:")
        for rec in tax_analysis['recommendations'][:3]:
            report.append(f"  - {rec}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_json_report(self) -> str:
        """Generate a JSON report with all analysis data"""
        full_report = self.analyzer.generate_full_report()
        full_report['tax_analysis'] = self.tax_optimizer.analyze()
        return json.dumps(full_report, indent=2, default=str)
    
    def save_report(self, output_file: str, format: str = 'text') -> None:
        """Save report to file"""
        if format == 'text':
            report = self.generate_text_report()
        elif format == 'json':
            report = self.generate_json_report()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with open(output_file, 'w') as f:
            f.write(report)

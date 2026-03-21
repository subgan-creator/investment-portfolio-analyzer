from dataclasses import dataclass, field
from typing import List, Dict
from collections import defaultdict
from .account import Account
from .holding import Holding


@dataclass
class Portfolio:
    """Represents the entire investment portfolio across all accounts"""
    
    portfolio_name: str
    accounts: List[Account] = field(default_factory=list)
    
    @property
    def total_value(self) -> float:
        """Total value across all accounts"""
        return sum(account.total_value for account in self.accounts)
    
    @property
    def total_cost_basis(self) -> float:
        """Total cost basis across all accounts"""
        return sum(account.total_cost_basis for account in self.accounts)
    
    @property
    def total_unrealized_gain_loss(self) -> float:
        """Total unrealized gains/losses"""
        return self.total_value - self.total_cost_basis
    
    def add_account(self, account: Account) -> None:
        """Add an account to the portfolio"""
        self.accounts.append(account)
    
    def get_all_holdings(self) -> List[Holding]:
        """Get all holdings across all accounts"""
        all_holdings = []
        for account in self.accounts:
            all_holdings.extend(account.holdings)
        return all_holdings
    
    def get_holdings_by_ticker(self) -> Dict[str, List[Holding]]:
        """Group holdings by ticker symbol"""
        holdings_map = defaultdict(list)
        for holding in self.get_all_holdings():
            holdings_map[holding.ticker].append(holding)
        return dict(holdings_map)
    
    def get_consolidated_positions(self) -> Dict[str, Dict]:
        """Get consolidated position data by ticker"""
        holdings_by_ticker = self.get_holdings_by_ticker()
        positions = {}
        
        for ticker, holdings in holdings_by_ticker.items():
            total_shares = sum(h.shares for h in holdings)
            total_value = sum(h.market_value for h in holdings)
            total_cost = sum(h.total_cost_basis for h in holdings)
            
            positions[ticker] = {
                'ticker': ticker,
                'total_shares': total_shares,
                'market_value': total_value,
                'cost_basis': total_cost,
                'unrealized_gain_loss': total_value - total_cost,
                'percentage_of_portfolio': (total_value / self.total_value * 100) if self.total_value > 0 else 0,
                'holdings_count': len(holdings),
                'asset_class': holdings[0].asset_class if holdings else "Unknown",
                'sector': holdings[0].sector if holdings else "Unknown",
                'description': holdings[0].description if holdings else ""
            }
        
        return positions
    
    def get_asset_allocation(self) -> Dict[str, float]:
        """Get asset allocation breakdown"""
        allocation = defaultdict(float)
        
        for holding in self.get_all_holdings():
            allocation[holding.asset_class] += holding.market_value
        
        # Convert to percentages
        if self.total_value > 0:
            return {asset_class: (value / self.total_value * 100) 
                    for asset_class, value in allocation.items()}
        return {}
    
    def get_sector_allocation(self) -> Dict[str, float]:
        """Get sector allocation breakdown"""
        allocation = defaultdict(float)

        for holding in self.get_all_holdings():
            if holding.asset_class.lower() in ['stock', 'etf']:
                allocation[holding.sector] += holding.market_value

        total_equity = sum(allocation.values())

        # Convert to percentages of equity portion
        if total_equity > 0:
            return {sector: (value / total_equity * 100)
                    for sector, value in allocation.items()}
        return {}

    def get_cost_basis_stats(self) -> Dict[str, any]:
        """Get statistics about cost basis data availability"""
        all_holdings = self.get_all_holdings()
        total_holdings = len(all_holdings)
        estimated_count = sum(1 for h in all_holdings if h.cost_basis_estimated)
        actual_count = total_holdings - estimated_count

        # Calculate value with estimated vs actual cost basis
        estimated_value = sum(h.market_value for h in all_holdings if h.cost_basis_estimated)
        actual_value = sum(h.market_value for h in all_holdings if not h.cost_basis_estimated)

        return {
            'total_holdings': total_holdings,
            'estimated_count': estimated_count,
            'actual_count': actual_count,
            'estimated_value': estimated_value,
            'actual_value': actual_value,
            'estimated_percentage': (estimated_value / self.total_value * 100) if self.total_value > 0 else 0,
            'has_estimated': estimated_count > 0,
        }
    
    def __repr__(self) -> str:
        return (f"Portfolio(name={self.portfolio_name}, accounts={len(self.accounts)}, "
                f"total_value=${self.total_value:,.2f})")

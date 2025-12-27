from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Holding:
    """Represents a single investment holding"""
    
    ticker: str
    shares: float
    cost_basis_per_share: float
    purchase_date: datetime
    current_price: float
    asset_class: str = "Unknown"  # 'Stock', 'Bond', 'ETF', 'Mutual Fund', 'Cash', etc.
    sector: str = "Unknown"
    
    @property
    def total_cost_basis(self) -> float:
        """Total cost basis for this holding"""
        return self.shares * self.cost_basis_per_share
    
    @property
    def market_value(self) -> float:
        """Current market value of the holding"""
        return self.shares * self.current_price
    
    @property
    def unrealized_gain_loss(self) -> float:
        """Unrealized gain or loss"""
        return self.market_value - self.total_cost_basis
    
    @property
    def return_percentage(self) -> float:
        """Return as a percentage"""
        if self.total_cost_basis == 0:
            return 0.0
        return (self.unrealized_gain_loss / self.total_cost_basis) * 100
    
    @property
    def holding_period_days(self) -> int:
        """Number of days held"""
        return (datetime.now() - self.purchase_date).days
    
    @property
    def is_long_term(self) -> bool:
        """Is this a long-term holding (>365 days)?"""
        return self.holding_period_days > 365
    
    def __repr__(self) -> str:
        return f"Holding(ticker={self.ticker}, shares={self.shares}, value=${self.market_value:,.2f})"

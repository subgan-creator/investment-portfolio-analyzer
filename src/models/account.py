from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class Account:
    """Represents an investment account (e.g., 401k, IRA, Brokerage)"""
    
    account_id: str
    account_name: str
    account_type: str  # e.g., '401k', 'IRA', 'Roth IRA', 'Taxable Brokerage'
    tax_status: str  # 'tax_deferred', 'tax_free', 'taxable'
    holdings: List['Holding'] = field(default_factory=list)
    
    @property
    def total_value(self) -> float:
        """Calculate total value of all holdings in the account"""
        return sum(holding.market_value for holding in self.holdings)
    
    @property
    def total_cost_basis(self) -> float:
        """Calculate total cost basis of all holdings"""
        return sum(holding.total_cost_basis for holding in self.holdings)
    
    @property
    def unrealized_gain_loss(self) -> float:
        """Calculate unrealized gains/losses"""
        return self.total_value - self.total_cost_basis
    
    def add_holding(self, holding: 'Holding') -> None:
        """Add a holding to the account"""
        self.holdings.append(holding)
    
    def __repr__(self) -> str:
        return f"Account(id={self.account_id}, name={self.account_name}, value=${self.total_value:,.2f})"

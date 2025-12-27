from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """Represents a buy/sell transaction"""
    
    transaction_id: str
    account_id: str
    ticker: str
    transaction_type: str  # 'buy', 'sell', 'dividend', 'transfer'
    shares: float
    price_per_share: float
    transaction_date: datetime
    fees: float = 0.0
    notes: Optional[str] = None
    
    @property
    def total_amount(self) -> float:
        """Total transaction amount including fees"""
        base_amount = self.shares * self.price_per_share
        if self.transaction_type == 'buy':
            return base_amount + self.fees
        return base_amount - self.fees
    
    def __repr__(self) -> str:
        return (f"Transaction(type={self.transaction_type}, ticker={self.ticker}, "
                f"shares={self.shares}, amount=${self.total_amount:,.2f})")

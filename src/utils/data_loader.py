import csv
import yaml
from datetime import datetime
from typing import Dict, Any
from ..models import Portfolio, Account, Holding


def load_portfolio_from_csv(csv_file: str, portfolio_name: str = "My Portfolio") -> Portfolio:
    """Load portfolio data from a CSV file"""
    portfolio = Portfolio(portfolio_name=portfolio_name)
    accounts_dict = {}
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            account_id = row['account_id']
            
            # Create account if it doesn't exist
            if account_id not in accounts_dict:
                account = Account(
                    account_id=account_id,
                    account_name=row['account_name'],
                    account_type=row['account_type'],
                    tax_status=row['tax_status'],
                )
                accounts_dict[account_id] = account
                portfolio.add_account(account)
            else:
                account = accounts_dict[account_id]
            
            # Create holding
            holding = Holding(
                ticker=row['ticker'],
                shares=float(row['shares']),
                cost_basis_per_share=float(row['cost_basis_per_share']),
                purchase_date=datetime.strptime(row['purchase_date'], '%Y-%m-%d'),
                current_price=float(row['current_price']),
                asset_class=row['asset_class'],
                sector=row['sector'],
            )
            
            account.add_holding(holding)
    
    return portfolio


def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_file}")
        print("Using default configuration.")
        return {}

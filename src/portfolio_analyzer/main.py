#!/usr/bin/env python3
"""
Investment Portfolio Analyzer - Main Entry Point
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils import load_portfolio_from_csv, load_config
from src.visualization import PortfolioReporter


def main():
    parser = argparse.ArgumentParser(
        description='Analyze investment portfolio for diversification, concentration risk, and tax optimization'
    )
    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='Path to input CSV file with portfolio data'
    )
    parser.add_argument(
        '--config',
        '-c',
        default='config.yaml',
        help='Path to configuration YAML file (default: config.yaml)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Path to output report file (optional)'
    )
    parser.add_argument(
        '--format',
        '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--name',
        '-n',
        default='My Portfolio',
        help='Portfolio name (default: My Portfolio)'
    )
    
    args = parser.parse_args()
    
    # Load portfolio data
    print(f"Loading portfolio from {args.input}...")
    try:
        portfolio = load_portfolio_from_csv(args.input, args.name)
        print(f"✓ Loaded portfolio with {len(portfolio.accounts)} accounts and "
              f"{len(portfolio.get_all_holdings())} holdings")
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        sys.exit(1)
    
    # Load configuration
    config = load_config(args.config)
    if config:
        print(f"✓ Loaded configuration from {args.config}")
    
    # Generate report
    print("\nGenerating analysis report...")
    reporter = PortfolioReporter(portfolio, config)
    
    if args.output:
        reporter.save_report(args.output, args.format)
        print(f"✓ Report saved to {args.output}")
    else:
        # Print to console
        if args.format == 'text':
            print("\n" + reporter.generate_text_report())
        else:
            print(reporter.generate_json_report())


if __name__ == '__main__':
    main()

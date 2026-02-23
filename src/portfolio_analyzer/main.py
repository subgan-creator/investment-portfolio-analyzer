#!/usr/bin/env python3
"""
Investment Portfolio Analyzer - Main Entry Point
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils import load_portfolio_from_csv, load_portfolio_from_multiple_sources, load_config
from src.visualization import PortfolioReporter


def main():
    parser = argparse.ArgumentParser(
        description='Analyze investment portfolio for diversification, concentration risk, and tax optimization'
    )
    parser.add_argument(
        '--input',
        '-i',
        nargs='+',
        required=True,
        help='Path to input CSV file(s) or folder containing CSV files. '
             'Can specify multiple files: -i file1.csv file2.csv '
             'Or a folder: -i data/statements/'
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

    # Determine if we have multiple inputs or a folder
    input_paths = args.input

    # Check if single input is a directory
    if len(input_paths) == 1:
        single_path = Path(input_paths[0])
        if single_path.is_dir():
            # Load all CSV files from directory
            csv_files = list(single_path.glob('*.csv'))
            if not csv_files:
                print(f"Error: No CSV files found in {single_path}")
                sys.exit(1)
            input_paths = [str(f) for f in csv_files]
            print(f"Found {len(input_paths)} CSV file(s) in {single_path}")

    # Load portfolio data
    try:
        if len(input_paths) == 1:
            # Single file
            print(f"Loading portfolio from {input_paths[0]}...")
            portfolio = load_portfolio_from_csv(input_paths[0], args.name)
        else:
            # Multiple files
            print(f"Loading portfolio from {len(input_paths)} files...")
            for f in input_paths:
                print(f"  - {f}")
            portfolio = load_portfolio_from_multiple_sources(input_paths, args.name)

        print(f"✓ Loaded portfolio with {len(portfolio.accounts)} accounts and "
              f"{len(portfolio.get_all_holdings())} holdings")
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        import traceback
        traceback.print_exc()
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

# Investment Portfolio Analyzer

A comprehensive tool for individual investors to analyze and optimize their investment portfolios across multiple accounts without requiring a financial advisor. 
Vision is to enable individual investors be informed about their investments, risks, concentration, macro trends and use AI to provide insigths and guidance so the investor can be well informed. Another aspect is to enable investors be prepared for their engagement with their investment professional, tax advisor and other financial specialist. The availability of data and structured insights will enable investors to have meanhigful goal based conversations with advisors and other professionals.

## Features

- **Portfolio Aggregation**: Consolidate holdings from multiple investment accounts
- **Diversification Analysis**: Evaluate asset allocation across sectors, asset classes, and geographies
- **Concentration Risk Detection**: Identify over-concentrated positions that may increase portfolio risk
- **Tax Optimization**: 
  - Tax-loss harvesting opportunities
  - Capital gains analysis
  - Cost basis tracking
- **Performance Metrics**: Track returns, volatility, and risk-adjusted performance
- **Visualization Dashboard**: Interactive charts and reports for portfolio insights
- - 🤖 **AI Investment Advisor**: "Claude-sonnet-4-20250514" powered chat widget that analyzes 
  your portfolio and provides personalized insights and guidance.
- **Fund Plan insights** Get better insights about target date fund allocation by uploading fund plan documents.


## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd investment-portfolio-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. **Prepare Your Data**: Create a CSV or Excel file with your portfolio holdings. See `data/sample/` for example formats.

2. **Run Analysis**:
```bash
python src/portfolio_analyzer/main.py --input data/your_portfolio.csv
```

3. **View Results**: Check the generated reports in the `output/` directory.

## Data Format

Your portfolio data should include:
- Account name/ID
- Ticker symbol
- Shares/units held
- Cost basis
- Purchase date
- Current value

See `data/sample/sample_portfolio.csv` for a complete example.

## Configuration

Copy `config.example.yaml` to `config.yaml` and customize:
- Risk tolerance levels
- Target asset allocation
- Tax bracket information
- Concentration thresholds

## Project Structure

```
investment-portfolio-analyzer/
├── src/
│   ├── models/           # Data models for accounts, holdings, transactions
│   ├── portfolio_analyzer/  # Core analysis logic
│   ├── utils/            # Helper functions
│   └── visualization/    # Charting and dashboard components
├── tests/                # Unit and integration tests
├── data/
│   └── sample/          # Example portfolio data
├── requirements.txt
└── README.md
```

## Contributing

This is a personal project, but suggestions and improvements are welcome!

## Disclaimer

This tool is for informational purposes only and does not constitute financial advice. Always consult with a qualified financial advisor before making investment decisions.

## License

MIT License

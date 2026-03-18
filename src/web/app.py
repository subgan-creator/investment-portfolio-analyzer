#!/usr/bin/env python3
"""
Investment Portfolio Analyzer - Web Application
"""
import os
import sys
import uuid
import gc
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename

from src.utils import load_portfolio_from_csv, load_portfolio_from_multiple_sources, load_config, load_portfolio_from_pdf
from src.portfolio_analyzer import PortfolioAnalyzer
from src.portfolio_analyzer.diversification import DiversificationAnalyzer
from src.portfolio_analyzer.concentration import ConcentrationRiskAnalyzer
from src.portfolio_analyzer.tax_optimizer import TaxOptimizer
from src.models.snapshot import (
    init_db, save_snapshot, get_all_snapshots, get_snapshot_by_id,
    delete_snapshot, get_snapshots_for_chart, calculate_comparison
)
from src.models.chat import (
    init_chat_db, save_message, get_messages, get_messages_for_api,
    clear_messages, get_message_count
)
from src.models.fund_profile import (
    init_fund_profiles_db, save_fund_profile, get_all_fund_profiles,
    get_fund_profile_by_id, delete_fund_profile, get_fund_profiles_summary,
    find_matching_profile
)
from src.services.ai_advisor import AIAdvisor, is_api_configured
from src.services.fund_matcher import (
    get_look_through_summary, calculate_look_through_allocation,
    match_holding_to_profile
)
from src.utils.fund_profile_parser import parse_fund_profile_pdf, validate_fund_profile
from src.utils.sector_classifier import classify_holding, consolidate_by_category_group, CATEGORY_GROUP_ORDER

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.secret_key = 'portfolio-analyzer-secret-key-change-in-production'

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent.parent.parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'csv', 'pdf'}

# Initialize databases
init_db()
init_chat_db()
init_fund_profiles_db()

# Ticker information database - full names and descriptions
TICKER_INFO = {
    # Vanguard ETFs
    'VTI': {'name': 'Vanguard Total Stock Market ETF', 'desc': 'Tracks the entire U.S. stock market'},
    'VOO': {'name': 'Vanguard S&P 500 ETF', 'desc': 'Tracks the S&P 500 index of large U.S. companies'},
    'VT': {'name': 'Vanguard Total World Stock ETF', 'desc': 'Tracks global stocks including U.S. and international'},
    'VXUS': {'name': 'Vanguard Total International Stock ETF', 'desc': 'Tracks stocks outside the U.S.'},
    'VEA': {'name': 'Vanguard FTSE Developed Markets ETF', 'desc': 'Tracks developed markets excluding U.S.'},
    'VWO': {'name': 'Vanguard FTSE Emerging Markets ETF', 'desc': 'Tracks emerging market stocks'},
    'VGT': {'name': 'Vanguard Information Technology ETF', 'desc': 'Tracks U.S. technology sector'},
    'VHT': {'name': 'Vanguard Health Care ETF', 'desc': 'Tracks U.S. healthcare sector'},
    'VNQ': {'name': 'Vanguard Real Estate ETF', 'desc': 'Tracks U.S. real estate investment trusts (REITs)'},
    'BND': {'name': 'Vanguard Total Bond Market ETF', 'desc': 'Tracks the U.S. investment-grade bond market'},
    'BNDX': {'name': 'Vanguard Total International Bond ETF', 'desc': 'Tracks international investment-grade bonds'},
    'VB': {'name': 'Vanguard Small-Cap ETF', 'desc': 'Tracks U.S. small-cap stocks'},
    'VO': {'name': 'Vanguard Mid-Cap ETF', 'desc': 'Tracks U.S. mid-cap stocks'},
    'VTV': {'name': 'Vanguard Value ETF', 'desc': 'Tracks U.S. large-cap value stocks'},
    'VUG': {'name': 'Vanguard Growth ETF', 'desc': 'Tracks U.S. large-cap growth stocks'},
    'VYM': {'name': 'Vanguard High Dividend Yield ETF', 'desc': 'Tracks high dividend-paying U.S. stocks'},
    'VIG': {'name': 'Vanguard Dividend Appreciation ETF', 'desc': 'Tracks stocks with growing dividends'},
    'VPU': {'name': 'Vanguard Utilities ETF', 'desc': 'Tracks U.S. utilities sector'},
    'VDC': {'name': 'Vanguard Consumer Staples ETF', 'desc': 'Tracks U.S. consumer staples sector'},
    'VCR': {'name': 'Vanguard Consumer Discretionary ETF', 'desc': 'Tracks U.S. consumer discretionary sector'},
    'VFH': {'name': 'Vanguard Financials ETF', 'desc': 'Tracks U.S. financial sector'},
    'VDE': {'name': 'Vanguard Energy ETF', 'desc': 'Tracks U.S. energy sector'},
    'VIS': {'name': 'Vanguard Industrials ETF', 'desc': 'Tracks U.S. industrial sector'},
    'VAW': {'name': 'Vanguard Materials ETF', 'desc': 'Tracks U.S. materials sector'},
    'VOX': {'name': 'Vanguard Communication Services ETF', 'desc': 'Tracks U.S. communication services sector'},

    # Vanguard Mutual Funds
    'VTSAX': {'name': 'Vanguard Total Stock Market Index Admiral', 'desc': 'Index fund tracking entire U.S. stock market'},
    'VFIAX': {'name': 'Vanguard 500 Index Admiral', 'desc': 'Index fund tracking S&P 500'},
    'VTIAX': {'name': 'Vanguard Total International Stock Index Admiral', 'desc': 'Index fund tracking international stocks'},
    'VBTLX': {'name': 'Vanguard Total Bond Market Index Admiral', 'desc': 'Index fund tracking U.S. bonds'},

    # Schwab ETFs
    'SCHB': {'name': 'Schwab U.S. Broad Market ETF', 'desc': 'Tracks broad U.S. stock market'},
    'SCHX': {'name': 'Schwab U.S. Large-Cap ETF', 'desc': 'Tracks U.S. large-cap stocks'},
    'SCHA': {'name': 'Schwab U.S. Small-Cap ETF', 'desc': 'Tracks U.S. small-cap stocks'},
    'SCHF': {'name': 'Schwab International Equity ETF', 'desc': 'Tracks developed international markets'},
    'SCHE': {'name': 'Schwab Emerging Markets Equity ETF', 'desc': 'Tracks emerging market stocks'},
    'SCHZ': {'name': 'Schwab U.S. Aggregate Bond ETF', 'desc': 'Tracks U.S. investment-grade bonds'},
    'SCHD': {'name': 'Schwab U.S. Dividend Equity ETF', 'desc': 'Tracks high dividend U.S. stocks'},
    'SWTSX': {'name': 'Schwab Total Stock Market Index Fund', 'desc': 'Index fund tracking U.S. stock market'},

    # iShares ETFs
    'IVV': {'name': 'iShares Core S&P 500 ETF', 'desc': 'Tracks the S&P 500 index'},
    'ITOT': {'name': 'iShares Core S&P Total U.S. Stock Market ETF', 'desc': 'Tracks total U.S. stock market'},
    'IEFA': {'name': 'iShares Core MSCI EAFE ETF', 'desc': 'Tracks developed markets outside U.S.'},
    'IEMG': {'name': 'iShares Core MSCI Emerging Markets ETF', 'desc': 'Tracks emerging market stocks'},
    'AGG': {'name': 'iShares Core U.S. Aggregate Bond ETF', 'desc': 'Tracks U.S. investment-grade bonds'},
    'IJR': {'name': 'iShares Core S&P Small-Cap ETF', 'desc': 'Tracks U.S. small-cap stocks'},
    'IJH': {'name': 'iShares Core S&P Mid-Cap ETF', 'desc': 'Tracks U.S. mid-cap stocks'},
    'IWM': {'name': 'iShares Russell 2000 ETF', 'desc': 'Tracks U.S. small-cap stocks (Russell 2000)'},
    'EFA': {'name': 'iShares MSCI EAFE ETF', 'desc': 'Tracks developed international markets'},
    'EEM': {'name': 'iShares MSCI Emerging Markets ETF', 'desc': 'Tracks emerging market stocks'},
    'TLT': {'name': 'iShares 20+ Year Treasury Bond ETF', 'desc': 'Tracks long-term U.S. Treasury bonds'},
    'IEF': {'name': 'iShares 7-10 Year Treasury Bond ETF', 'desc': 'Tracks intermediate-term U.S. Treasury bonds'},
    'SHY': {'name': 'iShares 1-3 Year Treasury Bond ETF', 'desc': 'Tracks short-term U.S. Treasury bonds'},
    'LQD': {'name': 'iShares iBoxx Investment Grade Corporate Bond ETF', 'desc': 'Tracks investment-grade corporate bonds'},
    'HYG': {'name': 'iShares iBoxx High Yield Corporate Bond ETF', 'desc': 'Tracks high-yield corporate bonds'},
    'TIP': {'name': 'iShares TIPS Bond ETF', 'desc': 'Tracks Treasury Inflation-Protected Securities'},
    'MUB': {'name': 'iShares National Muni Bond ETF', 'desc': 'Tracks tax-exempt municipal bonds'},

    # SPDR ETFs
    'SPY': {'name': 'SPDR S&P 500 ETF Trust', 'desc': 'Tracks the S&P 500 index (oldest ETF)'},
    'XLK': {'name': 'Technology Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 technology sector'},
    'XLV': {'name': 'Health Care Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 healthcare sector'},
    'XLF': {'name': 'Financial Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 financial sector'},
    'XLE': {'name': 'Energy Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 energy sector'},
    'XLI': {'name': 'Industrial Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 industrial sector'},
    'XLY': {'name': 'Consumer Discretionary Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 consumer discretionary'},
    'XLP': {'name': 'Consumer Staples Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 consumer staples'},
    'XLB': {'name': 'Materials Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 materials sector'},
    'XLU': {'name': 'Utilities Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 utilities sector'},
    'XLRE': {'name': 'Real Estate Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 real estate sector'},
    'XLC': {'name': 'Communication Services Select Sector SPDR Fund', 'desc': 'Tracks S&P 500 communication services'},
    'MDY': {'name': 'SPDR S&P MidCap 400 ETF', 'desc': 'Tracks U.S. mid-cap stocks'},

    # Invesco ETFs
    'QQQ': {'name': 'Invesco QQQ Trust', 'desc': 'Tracks the Nasdaq-100 (large tech-focused)'},

    # Fidelity Funds
    'FXAIX': {'name': 'Fidelity 500 Index Fund', 'desc': 'Index fund tracking S&P 500'},
    'FSKAX': {'name': 'Fidelity Total Market Index Fund', 'desc': 'Index fund tracking total U.S. market'},
    'FTIHX': {'name': 'Fidelity Total International Index Fund', 'desc': 'Index fund tracking international stocks'},
    'FZROX': {'name': 'Fidelity ZERO Total Market Index Fund', 'desc': 'Zero expense ratio total market fund'},
    'FZILX': {'name': 'Fidelity ZERO International Index Fund', 'desc': 'Zero expense ratio international fund'},

    # Major Stocks
    'AAPL': {'name': 'Apple Inc.', 'desc': 'Technology company - iPhones, Macs, services'},
    'MSFT': {'name': 'Microsoft Corporation', 'desc': 'Technology company - Windows, Azure, Office'},
    'GOOGL': {'name': 'Alphabet Inc. (Class A)', 'desc': 'Parent of Google - search, ads, cloud'},
    'GOOG': {'name': 'Alphabet Inc. (Class C)', 'desc': 'Parent of Google - search, ads, cloud'},
    'AMZN': {'name': 'Amazon.com Inc.', 'desc': 'E-commerce and cloud computing (AWS)'},
    'META': {'name': 'Meta Platforms Inc.', 'desc': 'Social media - Facebook, Instagram, WhatsApp'},
    'NVDA': {'name': 'NVIDIA Corporation', 'desc': 'Semiconductors - GPUs, AI chips'},
    'TSLA': {'name': 'Tesla Inc.', 'desc': 'Electric vehicles and clean energy'},
    'BRK.A': {'name': 'Berkshire Hathaway Inc. (Class A)', 'desc': 'Warren Buffett\'s conglomerate'},
    'BRK.B': {'name': 'Berkshire Hathaway Inc. (Class B)', 'desc': 'Warren Buffett\'s conglomerate'},
    'JPM': {'name': 'JPMorgan Chase & Co.', 'desc': 'Largest U.S. bank by assets'},
    'V': {'name': 'Visa Inc.', 'desc': 'Global payments technology company'},
    'MA': {'name': 'Mastercard Inc.', 'desc': 'Global payments technology company'},
    'JNJ': {'name': 'Johnson & Johnson', 'desc': 'Healthcare - pharmaceuticals, medical devices'},
    'UNH': {'name': 'UnitedHealth Group Inc.', 'desc': 'Health insurance and healthcare services'},
    'PG': {'name': 'Procter & Gamble Co.', 'desc': 'Consumer goods - household and personal care'},
    'HD': {'name': 'The Home Depot Inc.', 'desc': 'Home improvement retail'},
    'DIS': {'name': 'The Walt Disney Company', 'desc': 'Entertainment - movies, parks, streaming'},
    'NFLX': {'name': 'Netflix Inc.', 'desc': 'Streaming entertainment service'},
    'KO': {'name': 'The Coca-Cola Company', 'desc': 'Beverage company'},
    'PEP': {'name': 'PepsiCo Inc.', 'desc': 'Food and beverage company'},
    'WMT': {'name': 'Walmart Inc.', 'desc': 'Retail - world\'s largest company by revenue'},
    'COST': {'name': 'Costco Wholesale Corporation', 'desc': 'Membership-only warehouse club'},
    'XOM': {'name': 'Exxon Mobil Corporation', 'desc': 'Oil and gas - largest U.S. oil company'},
    'CVX': {'name': 'Chevron Corporation', 'desc': 'Oil and gas multinational'},
    'AMD': {'name': 'Advanced Micro Devices Inc.', 'desc': 'Semiconductors - CPUs and GPUs'},
    'INTC': {'name': 'Intel Corporation', 'desc': 'Semiconductors - processors'},
    'CRM': {'name': 'Salesforce Inc.', 'desc': 'Cloud-based CRM software'},
    'ADBE': {'name': 'Adobe Inc.', 'desc': 'Software - Creative Cloud, PDF'},
    'ORCL': {'name': 'Oracle Corporation', 'desc': 'Enterprise software and cloud'},
    'IBM': {'name': 'International Business Machines', 'desc': 'Technology and consulting'},
    'CSCO': {'name': 'Cisco Systems Inc.', 'desc': 'Networking hardware and software'},
    'AVGO': {'name': 'Broadcom Inc.', 'desc': 'Semiconductors and infrastructure software'},
    'TXN': {'name': 'Texas Instruments Inc.', 'desc': 'Semiconductors - analog chips'},
}


def get_ticker_info(ticker: str, full_name: str = '') -> dict:
    """Get ticker information with fallback to Yahoo Finance link.

    Args:
        ticker: The ticker symbol (may be truncated)
        full_name: Full fund/security name from source PDF (optional)
    """
    import re

    ticker_upper = ticker.upper()
    ticker_clean = ticker.strip()

    # If we have a full name from the PDF, use it for pattern matching
    search_text = full_name if full_name else ticker_upper

    # Check exact match first
    if ticker_upper in TICKER_INFO:
        info = TICKER_INFO[ticker_upper].copy()
        info['url'] = f"https://finance.yahoo.com/quote/{ticker_upper}"
        return info

    # Pattern matching for Target Date Funds (common in 401k plans)
    # Use search_text which may be the full fund name from PDF (e.g., "Target Date 2045 Fund")
    target_date_patterns = [
        (r'(?:TARGET|TRGT|TGT).*?(?:DATE|DT)?.*?(\d{4})', 'Target Date {} Fund', 'Automatically adjusts asset allocation as you approach retirement in {}'),
        (r'(?:RETIRE|RET).*?(\d{4})', 'Retirement {} Fund', 'Target retirement fund for those planning to retire around {}'),
        (r'(?:LIFECYCLE|LIFE|LC).*?(\d{4})', 'Lifecycle {} Fund', 'Lifecycle fund targeting retirement in {}'),
        (r'(\d{4}).*?(?:TARGET|RETIRE|FUND)', '{} Target Fund', 'Target date fund for retirement around {}'),
    ]

    for pattern, name_fmt, desc_fmt in target_date_patterns:
        # Search in full_name first (has the complete fund name), then fallback to ticker
        match = re.search(pattern, search_text.upper(), re.IGNORECASE)
        if match:
            year = match.group(1)
            search_query = full_name.replace(' ', '+') if full_name else ticker_clean.replace(' ', '+')
            return {
                'name': name_fmt.format(year),
                'desc': desc_fmt.format(year),
                'url': f"https://www.google.com/search?q={search_query}+fund"
            }

    # Catch truncated Target Date funds without year
    if re.search(r'(?:TARGET|TRGT|TGT)(?:DAT|DATE)?', search_text.upper()):
        return {
            'name': 'Target Date Fund',
            'desc': 'Shifts from stocks to bonds as retirement approaches. Check your 401k plan for target year.',
            'url': f"https://www.google.com/search?q={ticker_clean.replace(' ', '+')}+target+date+fund"
        }

    # Pattern matching for common fund types
    fund_patterns = [
        (r'S&P\s*500|SP500|S&P500', 'S&P 500 Index Fund', 'Tracks the S&P 500 index of large U.S. companies'),
        (r'TOTAL\s*(?:STOCK|MKT|MARKET)', 'Total Stock Market Fund', 'Tracks the entire U.S. stock market'),
        (r'(?:INTL|INT\'?L|INTERNATIONAL)', 'International Fund', 'Invests in stocks outside the U.S.'),
        (r'BOND|FIXED\s*INCOME', 'Bond Fund', 'Invests in fixed income securities'),
        (r'SMALL\s*CAP', 'Small Cap Fund', 'Invests in smaller U.S. companies'),
        (r'MID\s*CAP', 'Mid Cap Fund', 'Invests in medium-sized U.S. companies'),
        (r'LARGE\s*CAP', 'Large Cap Fund', 'Invests in large U.S. companies'),
        (r'GROWTH', 'Growth Fund', 'Focuses on stocks with high growth potential'),
        (r'VALUE', 'Value Fund', 'Focuses on undervalued stocks'),
        (r'BALANCED|MODERATE', 'Balanced Fund', 'Mix of stocks and bonds'),
        (r'STABLE\s*VALUE|MONEY\s*MARKET', 'Stable Value Fund', 'Low-risk, stable returns'),
        (r'REAL\s*ESTATE|REIT', 'Real Estate Fund', 'Invests in real estate securities'),
        (r'EMERGING', 'Emerging Markets Fund', 'Invests in developing economies'),
    ]

    for pattern, name, desc in fund_patterns:
        if re.search(pattern, search_text.upper()):
            return {
                'name': name,
                'desc': desc,
                'url': f"https://www.google.com/search?q={ticker_clean.replace(' ', '+')}+fund"
            }

    # Check if it looks like an internal fund code (short alphanumeric)
    if re.match(r'^[A-Z0-9]{3,6}$', ticker_upper) and not ticker_upper.isalpha():
        return {
            'name': f'{ticker_clean} (Internal Fund)',
            'desc': 'Internal fund code - check your plan documents',
            'url': f"https://www.google.com/search?q={ticker_clean}+fund"
        }

    # Fallback for truly unknown tickers
    return {
        'name': ticker_clean,
        'desc': 'Click to search for more info',
        'url': f"https://www.google.com/search?q={ticker_clean.replace(' ', '+')}+stock+fund"
    }


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with file upload"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file upload and redirect to analysis"""
    if 'files' not in request.files:
        flash('No files selected', 'error')
        return redirect(url_for('index'))

    files = request.files.getlist('files')

    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(url_for('index'))

    # Save uploaded files
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            saved_files.append(filepath)

    if not saved_files:
        flash('No valid CSV files uploaded', 'error')
        return redirect(url_for('index'))

    # Store file paths in session-like manner (using query params for simplicity)
    # In production, use proper session management
    file_params = '&'.join([f'file={os.path.basename(f)}' for f in saved_files])
    return redirect(url_for('select_accounts') + '?' + file_params)


@app.route('/select_accounts')
def select_accounts():
    """Show accounts and let user select which to include in analysis"""
    file_names = request.args.getlist('file')

    if not file_names:
        flash('No files to analyze', 'error')
        return redirect(url_for('index'))

    # Build full paths
    file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in file_names]
    file_paths = [f for f in file_paths if os.path.exists(f)]

    if not file_paths:
        flash('Upload files not found. Please upload again.', 'error')
        return redirect(url_for('index'))

    try:
        # Separate CSV and PDF files
        csv_files = [f for f in file_paths if f.lower().endswith('.csv')]
        pdf_files = [f for f in file_paths if f.lower().endswith('.pdf')]

        portfolios = []

        # Load CSV files
        if len(csv_files) == 1:
            csv_portfolio = load_portfolio_from_csv(csv_files[0], "My Portfolio")
            if csv_portfolio:
                portfolios.append(csv_portfolio)
        elif len(csv_files) > 1:
            csv_portfolio = load_portfolio_from_multiple_sources(csv_files, "My Portfolio")
            if csv_portfolio:
                portfolios.append(csv_portfolio)

        # Load PDF files (with explicit garbage collection for memory efficiency)
        for pdf_file in pdf_files:
            pdf_portfolio = load_portfolio_from_pdf(pdf_file, "My Portfolio")
            if pdf_portfolio:
                portfolios.append(pdf_portfolio)
            # Free memory after each PDF to avoid OOM on limited memory servers
            gc.collect()

        if not portfolios:
            flash('Could not parse the uploaded file(s). Please check the format.', 'error')
            return redirect(url_for('index'))

        # Collect all accounts
        all_accounts = []
        for portfolio in portfolios:
            for account in portfolio.accounts:
                all_accounts.append({
                    'id': account.account_id,
                    'name': account.account_name,
                    'type': account.account_type,
                    'tax_status': account.tax_status,
                    'value': account.total_value,
                    'num_holdings': len(account.holdings),
                })

        file_params = '&'.join([f'file={f}' for f in file_names])
        return render_template('select_accounts.html', accounts=all_accounts, file_params=file_params)

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error loading portfolio: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/analyze')
def analyze():
    """Analyze uploaded files and show results"""
    file_names = request.args.getlist('file')
    included_accounts = request.args.getlist('include_account')

    if not file_names:
        flash('No files to analyze', 'error')
        return redirect(url_for('index'))

    # Build full paths
    file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in file_names]

    # Verify files exist
    file_paths = [f for f in file_paths if os.path.exists(f)]

    if not file_paths:
        flash('Upload files not found. Please upload again.', 'error')
        return redirect(url_for('index'))

    try:
        # Separate CSV and PDF files
        csv_files = [f for f in file_paths if f.lower().endswith('.csv')]
        pdf_files = [f for f in file_paths if f.lower().endswith('.pdf')]

        portfolios = []

        # Load CSV files
        if len(csv_files) == 1:
            csv_portfolio = load_portfolio_from_csv(csv_files[0], "My Portfolio")
            if csv_portfolio:
                portfolios.append(csv_portfolio)
        elif len(csv_files) > 1:
            csv_portfolio = load_portfolio_from_multiple_sources(csv_files, "My Portfolio")
            if csv_portfolio:
                portfolios.append(csv_portfolio)

        # Load PDF files (with explicit garbage collection for memory efficiency)
        for pdf_file in pdf_files:
            pdf_portfolio = load_portfolio_from_pdf(pdf_file, "My Portfolio")
            if pdf_portfolio:
                portfolios.append(pdf_portfolio)
            # Free memory after each PDF to avoid OOM on limited memory servers
            gc.collect()

        # Merge all portfolios if multiple
        if not portfolios:
            flash('Could not parse the uploaded file(s). Please check the format.', 'error')
            return redirect(url_for('index'))

        if len(portfolios) == 1:
            portfolio = portfolios[0]
        else:
            # Merge portfolios
            portfolio = portfolios[0]
            for p in portfolios[1:]:
                for account in p.accounts:
                    portfolio.add_account(account)

        # Filter accounts if selection was made
        if included_accounts:
            portfolio.accounts = [acc for acc in portfolio.accounts if acc.account_id in included_accounts]
            if not portfolio.accounts:
                flash('No accounts selected for analysis.', 'error')
                return redirect(url_for('index'))

        # Load config (if exists)
        config = load_config('config.yaml') or {}

        # Run analysis
        analyzer = PortfolioAnalyzer(portfolio, config)
        diversification = DiversificationAnalyzer(portfolio, config)
        concentration = ConcentrationRiskAnalyzer(portfolio, config)
        tax_optimizer = TaxOptimizer(portfolio, config)

        # Prepare data for template
        analysis_data = {
            'portfolio': {
                'name': portfolio.portfolio_name,
                'total_value': portfolio.total_value,
                'total_cost_basis': portfolio.total_cost_basis,
                'unrealized_gain_loss': portfolio.total_value - portfolio.total_cost_basis,
                'return_percent': ((portfolio.total_value - portfolio.total_cost_basis) / portfolio.total_cost_basis * 100) if portfolio.total_cost_basis > 0 else 0,
                'num_accounts': len(portfolio.accounts),
                'num_holdings': len(portfolio.get_all_holdings()),
                'cost_basis_stats': portfolio.get_cost_basis_stats(),
            },
            'accounts': [],
            'asset_allocation': [],
            'sector_allocation': [],  # Per-sector breakdown
            'top_holdings': [],
            'source_breakdown': [],  # Per-brokerage breakdown
            'diversification': {},
            'concentration': {},
            'tax': {},
        }

        # Helper function to infer sector from ticker
        def infer_sector(ticker: str, existing_sector: str) -> str:
            """Infer sector from ticker if not already set."""
            if existing_sector and existing_sector != "Unknown":
                return existing_sector

            ticker_upper = ticker.upper()

            # Technology sector ETFs and stocks
            tech_tickers = {'QQQ', 'VGT', 'XLK', 'FTEC', 'IYW', 'SMH', 'SOXX', 'IGV',
                           'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'NVDA', 'AMD', 'INTC',
                           'CRM', 'ADBE', 'NOW', 'ORCL', 'IBM', 'CSCO', 'AVGO', 'TXN'}
            if ticker_upper in tech_tickers:
                return 'Technology'

            # Healthcare sector
            healthcare_tickers = {'XLV', 'VHT', 'IYH', 'FHLC', 'IBB', 'XBI',
                                 'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT'}
            if ticker_upper in healthcare_tickers:
                return 'Healthcare'

            # Financials sector
            financial_tickers = {'XLF', 'VFH', 'IYF', 'FNCL', 'KBE', 'KRE',
                                'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BRK.A', 'BRK.B', 'V', 'MA'}
            if ticker_upper in financial_tickers:
                return 'Financials'

            # Consumer Discretionary
            consumer_disc_tickers = {'XLY', 'VCR', 'FDIS', 'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW'}
            if ticker_upper in consumer_disc_tickers:
                return 'Consumer Discretionary'

            # Consumer Staples
            consumer_staples_tickers = {'XLP', 'VDC', 'FSTA', 'PG', 'KO', 'PEP', 'WMT', 'COST', 'PM', 'MO'}
            if ticker_upper in consumer_staples_tickers:
                return 'Consumer Staples'

            # Energy
            energy_tickers = {'XLE', 'VDE', 'FENY', 'IYE', 'XOP', 'OIH',
                             'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'VLO', 'PSX'}
            if ticker_upper in energy_tickers:
                return 'Energy'

            # Industrials
            industrial_tickers = {'XLI', 'VIS', 'FIDU', 'IYJ',
                                 'UNP', 'UPS', 'HON', 'BA', 'CAT', 'GE', 'MMM', 'RTX', 'LMT'}
            if ticker_upper in industrial_tickers:
                return 'Industrials'

            # Materials
            materials_tickers = {'XLB', 'VAW', 'FMAT', 'IYM', 'LIN', 'APD', 'SHW', 'FCX', 'NEM', 'DOW'}
            if ticker_upper in materials_tickers:
                return 'Materials'

            # Utilities
            utilities_tickers = {'XLU', 'VPU', 'FUTY', 'IDU', 'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC'}
            if ticker_upper in utilities_tickers:
                return 'Utilities'

            # Real Estate
            real_estate_tickers = {'VNQ', 'XLRE', 'FREL', 'IYR', 'AMT', 'PLD', 'CCI', 'EQIX', 'SPG', 'O'}
            if ticker_upper in real_estate_tickers:
                return 'Real Estate'

            # Communication Services
            comm_tickers = {'XLC', 'VOX', 'FCOM', 'DIS', 'NFLX', 'T', 'VZ', 'TMUS', 'CMCSA', 'CHTR'}
            if ticker_upper in comm_tickers:
                return 'Communication Services'

            # Bonds / Fixed Income
            bond_tickers = {'BND', 'AGG', 'SCHZ', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'TIP', 'MUB',
                           'VBTLX', 'VTBIX', 'VBIRX', 'VBILX', 'VCIT', 'VCSH', 'BSV', 'BIV', 'BLV'}
            if ticker_upper in bond_tickers:
                return 'Fixed Income'

            # International / Global
            intl_tickers = {'VXUS', 'VEA', 'VWO', 'IEFA', 'EFA', 'EEM', 'IEMG', 'IXUS', 'VEU', 'VTIAX'}
            if ticker_upper in intl_tickers:
                return 'International'

            # Broad Market / Diversified
            broad_tickers = {'VTI', 'VOO', 'SPY', 'IVV', 'SCHB', 'ITOT', 'SWTSX', 'SPTM', 'VT',
                            'VTSAX', 'VFIAX', 'FXAIX', 'FSKAX', 'FZROX'}
            if ticker_upper in broad_tickers:
                return 'Diversified'

            # Small/Mid Cap
            smallmid_tickers = {'VB', 'VBK', 'VBR', 'IJR', 'IWM', 'VO', 'IJH', 'MDY', 'SCHA', 'SCHM'}
            if ticker_upper in smallmid_tickers:
                return 'Small/Mid Cap'

            return 'Other'

        # Helper function to extract source/brokerage from account_type
        def extract_source(account_type: str) -> str:
            """Extract the brokerage source from account type string."""
            account_type_lower = account_type.lower()
            if 'betterment' in account_type_lower:
                return 'Betterment'
            elif 'titan' in account_type_lower:
                return 'Titan'
            elif 'fidelity' in account_type_lower:
                return 'Fidelity'
            elif 'empower' in account_type_lower:
                return 'Empower'
            elif 'acorns' in account_type_lower:
                return 'Acorns'
            elif 'arta' in account_type_lower:
                return 'Arta Finance'
            elif 'schwab' in account_type_lower:
                return 'Schwab'
            elif 'vanguard' in account_type_lower:
                return 'Vanguard'
            else:
                return 'Other'

        # Calculate per-source breakdown
        source_values = {}
        for account in portfolio.accounts:
            source = extract_source(account.account_type)
            if source not in source_values:
                source_values[source] = {'value': 0, 'accounts': 0}
            source_values[source]['value'] += account.total_value
            source_values[source]['accounts'] += 1

        # Sort by value descending and add to analysis_data
        for source, data in sorted(source_values.items(), key=lambda x: x[1]['value'], reverse=True):
            percent = (data['value'] / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
            analysis_data['source_breakdown'].append({
                'name': source,
                'value': data['value'],
                'percent': percent,
                'accounts': data['accounts'],
            })

        # Account details (now includes source)
        for account in portfolio.accounts:
            source = extract_source(account.account_type)
            analysis_data['accounts'].append({
                'name': account.account_name,
                'type': account.account_type,
                'tax_status': account.tax_status,
                'value': account.total_value,
                'num_holdings': len(account.holdings),
                'source': source,
            })

        # Asset allocation - calculate values by asset class
        asset_values = {}
        for holding in portfolio.get_all_holdings():
            asset_class = holding.asset_class
            if asset_class not in asset_values:
                asset_values[asset_class] = 0
            asset_values[asset_class] += holding.market_value

        for asset_class, value in sorted(asset_values.items(), key=lambda x: x[1], reverse=True):
            percent = (value / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
            analysis_data['asset_allocation'].append({
                'name': asset_class,
                'value': value,
                'percent': percent,
            })

        # Sector allocation - using standardized classification
        # Build detailed allocation with standardized labels and category groups
        sector_details = {}  # key: standardized_label, value: {value, category_group}
        for holding in portfolio.get_all_holdings():
            description = getattr(holding, 'description', '')
            existing_sector = holding.sector if hasattr(holding, 'sector') else ''

            # Use new classifier
            standardized_label, category_group = classify_holding(
                holding.ticker,
                description,
                existing_sector
            )

            if standardized_label not in sector_details:
                sector_details[standardized_label] = {
                    'value': 0,
                    'category_group': category_group
                }
            sector_details[standardized_label]['value'] += holding.market_value

        # Build detailed sector allocation (standardized labels)
        detailed_allocation = []
        for label, data in sorted(sector_details.items(), key=lambda x: x[1]['value'], reverse=True):
            percent = (data['value'] / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
            detailed_allocation.append({
                'name': label,
                'value': data['value'],
                'percent': percent,
                'category_group': data['category_group'],
            })

        # Store detailed allocation
        analysis_data['sector_allocation'] = detailed_allocation

        # Build consolidated category group allocation
        analysis_data['category_allocation'] = consolidate_by_category_group(detailed_allocation)

        # Top holdings - consolidate by ticker to avoid duplicates across accounts
        holdings_by_ticker = {}
        for holding in portfolio.get_all_holdings():
            ticker = holding.ticker
            if ticker in holdings_by_ticker:
                # Consolidate: sum values and recalculate weighted averages
                existing = holdings_by_ticker[ticker]
                total_value = existing['value'] + holding.market_value
                total_cost = existing['cost_basis'] + (holding.cost_basis_per_share * holding.shares)
                total_shares = existing['shares'] + holding.shares
                holdings_by_ticker[ticker] = {
                    'value': total_value,
                    'cost_basis': total_cost,
                    'shares': total_shares,
                    'full_name': existing.get('full_name') or getattr(holding, 'description', ''),
                }
            else:
                holdings_by_ticker[ticker] = {
                    'value': holding.market_value,
                    'cost_basis': holding.cost_basis_per_share * holding.shares,
                    'shares': holding.shares,
                    'full_name': getattr(holding, 'description', ''),  # Full fund name from PDF
                }

        # Sort by total value and get top 10
        sorted_tickers = sorted(holdings_by_ticker.items(), key=lambda x: x[1]['value'], reverse=True)
        for i, (ticker, data) in enumerate(sorted_tickers[:10]):
            pct = (data['value'] / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
            gain_loss = data['value'] - data['cost_basis']
            gain_loss_pct = ((data['value'] / data['cost_basis']) - 1) * 100 if data['cost_basis'] > 0 else 0
            # Pass full fund name from PDF if available (e.g., "Target Date 2045 Fund")
            ticker_info = get_ticker_info(ticker, data.get('full_name', ''))
            analysis_data['top_holdings'].append({
                'rank': i + 1,
                'ticker': ticker,
                'value': data['value'],
                'percent': pct,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_pct,
                'name': ticker_info['name'],
                'description': ticker_info['desc'],
                'url': ticker_info['url'],
            })

        # Diversification analysis
        div_analysis = diversification.analyze()
        # diversification_score is a nested dict with 'score' and 'rating'
        div_score_data = div_analysis.get('diversification_score', {})
        analysis_data['diversification'] = {
            'score': div_score_data.get('score', 0) if isinstance(div_score_data, dict) else 0,
            'rating': div_score_data.get('rating', 'Unknown') if isinstance(div_score_data, dict) else 'Unknown',
            'hhi': div_analysis.get('herfindahl_index', 0),
        }

        # Concentration analysis
        conc_analysis = concentration.analyze()
        # risk_level is a dict with 'risk_level' key, or could be a string
        risk_level_data = conc_analysis.get('risk_level', {})
        if isinstance(risk_level_data, dict):
            risk_level = risk_level_data.get('risk_level', 'Unknown')
        else:
            risk_level = risk_level_data

        # top_10_concentration is a dict with 'percentage' key
        top_10_data = conc_analysis.get('top_10_concentration', {})
        if isinstance(top_10_data, dict):
            top_10_pct = top_10_data.get('percentage', 0)
        else:
            top_10_pct = top_10_data

        analysis_data['concentration'] = {
            'risk_level': risk_level,
            'concentrated_positions': conc_analysis.get('concentrated_positions', []),
            'top_10_concentration': top_10_pct,
            'recommendations': conc_analysis.get('recommendations', []),
        }

        # Tax analysis
        tax_analysis = tax_optimizer.analyze()
        # tax_efficiency_score is a nested dict with 'score' and 'rating'
        tax_score_data = tax_analysis.get('tax_efficiency_score', {})
        # capital_gains_summary has estimated tax liability
        cap_gains = tax_analysis.get('capital_gains_summary', {})
        # tax_loss_harvesting is the list of opportunities
        harvesting_opps = tax_analysis.get('tax_loss_harvesting', [])

        analysis_data['tax'] = {
            'score': tax_score_data.get('score', 0) if isinstance(tax_score_data, dict) else 0,
            'rating': tax_score_data.get('rating', 'Unknown') if isinstance(tax_score_data, dict) else 'Unknown',
            'estimated_liability': cap_gains.get('total_estimated_tax_liability', 0) if isinstance(cap_gains, dict) else 0,
            'harvesting_opportunities': harvesting_opps,
            'potential_savings': sum(h.get('potential_tax_savings', 0) for h in harvesting_opps),
        }

        # Look-Through Analysis for Target Date Funds
        # Build holdings list for look-through analysis
        holdings_for_lookthrough = []
        for holding in portfolio.get_all_holdings():
            holdings_for_lookthrough.append({
                'ticker': holding.ticker,
                'description': getattr(holding, 'description', ''),
                'market_value': holding.market_value,
                'asset_class': holding.asset_class,
            })

        # Get look-through summary (which holdings can be expanded)
        # Use the first account's type as a hint for source matching
        account_type_hint = portfolio.accounts[0].account_type if portfolio.accounts else ''
        look_through_summary = get_look_through_summary(holdings_for_lookthrough, account_type_hint)

        # Calculate look-through allocation if profiles are available
        look_through_allocation = []
        if look_through_summary.get('available') and look_through_summary.get('matchable_holdings'):
            lt_allocation = calculate_look_through_allocation(
                holdings_for_lookthrough,
                portfolio.total_value,
                account_type_hint
            )
            for asset_class, percent in sorted(lt_allocation.items(), key=lambda x: -x[1]):
                value = portfolio.total_value * (percent / 100)
                look_through_allocation.append({
                    'name': asset_class,
                    'value': value,
                    'percent': percent,
                })

        analysis_data['look_through'] = {
            'available': look_through_summary.get('available', False),
            'message': look_through_summary.get('message', ''),
            'matchable_holdings': look_through_summary.get('matchable_holdings', []),
            'allocation': look_through_allocation,
        }

        return render_template('results.html', data=analysis_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error analyzing portfolio: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for analysis (for future use)"""
    # This can be expanded for AJAX-based updates
    pass


# ==================== HISTORY & SNAPSHOT ROUTES ====================

@app.route('/history')
def history():
    """Display portfolio history with value chart and snapshot list."""
    snapshots = get_all_snapshots()
    chart_data = get_snapshots_for_chart()

    # Format snapshots for display
    snapshot_list = []
    for s in snapshots:
        snapshot_list.append({
            'id': s.id,
            'name': s.name,
            'created_at': s.created_at.strftime('%B %d, %Y'),
            'created_at_time': s.created_at.strftime('%I:%M %p'),
            'total_value': s.total_value,
            'return_percent': s.return_percent,
            'num_accounts': s.num_accounts,
            'num_holdings': s.num_holdings,
        })

    return render_template('history.html',
                           snapshots=snapshot_list,
                           chart_data=chart_data)


@app.route('/snapshot/save', methods=['POST'])
def save_snapshot_route():
    """Save current analysis as a snapshot."""
    import json

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    analysis_data = data.get('analysis_data')
    name = data.get('name', datetime.now().strftime('Snapshot - %B %d, %Y'))

    if not analysis_data:
        return jsonify({'success': False, 'error': 'No analysis data provided'}), 400

    try:
        snapshot = save_snapshot(name, analysis_data)
        return jsonify({
            'success': True,
            'id': snapshot.id,
            'name': snapshot.name,
            'message': 'Snapshot saved successfully!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/snapshot/<int:snapshot_id>')
def view_snapshot(snapshot_id):
    """View a specific snapshot."""
    snapshot = get_snapshot_by_id(snapshot_id)
    if not snapshot:
        flash('Snapshot not found', 'error')
        return redirect(url_for('history'))

    return render_template('snapshot_view.html', data=snapshot.to_dict())


@app.route('/snapshot/<int:snapshot_id>/delete', methods=['POST'])
def delete_snapshot_route(snapshot_id):
    """Delete a snapshot."""
    if delete_snapshot(snapshot_id):
        flash('Snapshot deleted successfully', 'success')
    else:
        flash('Snapshot not found', 'error')
    return redirect(url_for('history'))


@app.route('/compare')
def compare_snapshots_route():
    """Compare two snapshots side-by-side."""
    id1 = request.args.get('snapshot1', type=int)
    id2 = request.args.get('snapshot2', type=int)

    if not id1 or not id2:
        flash('Please select two snapshots to compare', 'error')
        return redirect(url_for('history'))

    snapshot1 = get_snapshot_by_id(id1)
    snapshot2 = get_snapshot_by_id(id2)

    if not snapshot1 or not snapshot2:
        flash('One or both snapshots not found', 'error')
        return redirect(url_for('history'))

    comparison = calculate_comparison(snapshot1, snapshot2)

    return render_template('compare.html',
                           snapshot1=snapshot1.to_dict(),
                           snapshot2=snapshot2.to_dict(),
                           comparison=comparison)


# ==================== AI CHAT API ROUTES ====================

@app.route('/api/chat', methods=['GET'])
def get_chat_history():
    """Get chat history for the current session."""
    # Get or create session ID
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())[:8]

    session_id = session['chat_session_id']
    messages = get_messages(session_id)

    return jsonify({
        'success': True,
        'session_id': session_id,
        'messages': [m.to_dict() for m in messages],
        'api_configured': is_api_configured()
    })


@app.route('/api/chat', methods=['POST'])
def send_chat_message():
    """Send a message and get AI response."""
    # Get or create session ID
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())[:8]

    session_id = session['chat_session_id']

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'No message provided'}), 400

    user_message = data['message'].strip()
    if not user_message:
        return jsonify({'success': False, 'error': 'Empty message'}), 400

    # Get portfolio data from request (passed from frontend)
    portfolio_data = data.get('portfolio_data', {})

    # Check if API is configured
    if not is_api_configured():
        return jsonify({
            'success': False,
            'error': 'Anthropic API key not configured. Please add ANTHROPIC_API_KEY to your .env file.'
        }), 503

    try:
        # Save user message
        save_message(session_id, 'user', user_message)

        # Get conversation history
        conversation = get_messages_for_api(session_id)

        # Get AI response
        advisor = AIAdvisor(portfolio_data)
        ai_response = advisor.get_response(conversation)

        # Save AI response
        save_message(session_id, 'assistant', ai_response)

        return jsonify({
            'success': True,
            'response': ai_response,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing message: {str(e)}'
        }), 500


@app.route('/api/chat', methods=['DELETE'])
def clear_chat_history():
    """Clear chat history for the current session."""
    if 'chat_session_id' not in session:
        return jsonify({'success': True, 'message': 'No chat history to clear'})

    session_id = session['chat_session_id']
    count = clear_messages(session_id)

    # Generate new session ID
    session['chat_session_id'] = str(uuid.uuid4())[:8]

    return jsonify({
        'success': True,
        'message': f'Cleared {count} messages',
        'new_session_id': session['chat_session_id']
    })


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get specific investment recommendations using enhanced AI prompt."""
    if not is_api_configured():
        return jsonify({
            'success': False,
            'error': 'AI advisor is not configured. Please add ANTHROPIC_API_KEY to .env file.'
        }), 400

    try:
        data = request.get_json() or {}
        portfolio_data = data.get('portfolio_data', {})

        # Create advisor with portfolio context
        advisor = AIAdvisor(portfolio_data)

        # Get specific recommendations using the enhanced directive prompt
        recommendations = advisor.get_specific_recommendations()

        # Save to chat history for context
        session_id = session.get('chat_session_id')
        if session_id:
            save_message(session_id, 'user', 'Give me specific investment recommendations for my portfolio')
            save_message(session_id, 'assistant', recommendations)

        return jsonify({
            'success': True,
            'recommendations': recommendations
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat/status')
def chat_status():
    """Check if AI chat is available."""
    return jsonify({
        'available': is_api_configured(),
        'message': 'AI advisor is ready' if is_api_configured() else 'Please configure ANTHROPIC_API_KEY in .env file'
    })


# ==================== FUND PROFILE ROUTES ====================

@app.route('/fund-profiles')
def fund_profiles():
    """Display and manage fund profiles."""
    profiles = get_fund_profiles_summary()
    return render_template('fund_profiles.html', profiles=profiles)


@app.route('/fund-profiles/upload', methods=['POST'])
def upload_fund_profile():
    """Upload and parse a fund profile PDF."""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('fund_profiles'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('fund_profiles'))

    if not file.filename.lower().endswith('.pdf'):
        flash('Please upload a PDF file', 'error')
        return redirect(url_for('fund_profiles'))

    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"fund_profile_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Parse the fund profile PDF
        profiles = parse_fund_profile_pdf(filepath)

        if not profiles:
            flash('Could not extract any fund profiles from the PDF. Please check the format.', 'error')
            return redirect(url_for('fund_profiles'))

        # Save each profile to database
        saved_count = 0
        skipped_count = 0
        for profile_data in profiles:
            # Validate profile
            is_valid, issues = validate_fund_profile(profile_data)

            if is_valid:
                # Check if fund already exists
                existing = find_matching_profile(
                    profile_data['fund_name'],
                    profile_data.get('source')
                )

                if existing:
                    skipped_count += 1
                    continue

                # Save to database
                save_fund_profile(
                    fund_name=profile_data['fund_name'],
                    source=profile_data.get('source'),
                    fund_type=profile_data.get('fund_type'),
                    target_year=profile_data.get('target_year'),
                    risk_assessment=profile_data.get('risk_assessment'),
                    expense_ratio=profile_data.get('expense_ratio'),
                    asset_allocation=profile_data.get('asset_allocation'),
                    sector_breakdown=profile_data.get('sector_breakdown'),
                    top_holdings=profile_data.get('top_holdings'),
                )
                saved_count += 1

        if saved_count > 0:
            flash(f'Successfully imported {saved_count} fund profile(s).', 'success')
        if skipped_count > 0:
            flash(f'Skipped {skipped_count} existing fund profile(s).', 'info')

        # Clean up temp file
        os.remove(filepath)

        return redirect(url_for('fund_profiles'))

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error processing fund profile: {str(e)}', 'error')
        return redirect(url_for('fund_profiles'))


@app.route('/fund-profiles/<int:profile_id>')
def view_fund_profile(profile_id):
    """View details of a specific fund profile."""
    profile = get_fund_profile_by_id(profile_id)
    if not profile:
        flash('Fund profile not found', 'error')
        return redirect(url_for('fund_profiles'))

    return render_template('fund_profile_detail.html', profile=profile.to_dict())


@app.route('/fund-profiles/<int:profile_id>/delete', methods=['POST'])
def delete_fund_profile_route(profile_id):
    """Delete a fund profile."""
    if delete_fund_profile(profile_id):
        flash('Fund profile deleted successfully', 'success')
    else:
        flash('Fund profile not found', 'error')
    return redirect(url_for('fund_profiles'))


@app.route('/api/fund-profiles')
def api_get_fund_profiles():
    """API endpoint to get all fund profiles."""
    profiles = get_all_fund_profiles()
    return jsonify({
        'success': True,
        'profiles': [p.to_dict() for p in profiles]
    })


@app.route('/api/fund-profiles/<int:profile_id>')
def api_get_fund_profile(profile_id):
    """API endpoint to get a specific fund profile."""
    profile = get_fund_profile_by_id(profile_id)
    if not profile:
        return jsonify({'success': False, 'error': 'Fund profile not found'}), 404

    return jsonify({
        'success': True,
        'profile': profile.to_dict()
    })


@app.route('/api/fund-profiles/match', methods=['POST'])
def api_match_fund_profile():
    """API endpoint to find a matching fund profile for a holding."""
    data = request.get_json()
    if not data or 'fund_name' not in data:
        return jsonify({'success': False, 'error': 'Fund name required'}), 400

    profile = find_matching_profile(
        data['fund_name'],
        data.get('source')
    )

    if profile:
        return jsonify({
            'success': True,
            'matched': True,
            'profile': profile.to_dict()
        })
    else:
        return jsonify({
            'success': True,
            'matched': False,
            'message': 'No matching fund profile found'
        })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Investment Portfolio Analyzer - Web Interface")
    print("="*60)
    print("\nOpen your browser and go to: http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)

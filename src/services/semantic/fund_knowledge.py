"""
Fund Knowledge Base - Static database of common ETFs, mutual funds, and stocks.

Provides metadata for 200+ common investment holdings including:
- Full names and descriptions
- Asset class categorization
- Sector exposure
- Expense ratios
- Number of holdings (for diversification context)
"""

from typing import Dict, Optional, List, Any


# Asset class categories
class AssetClass:
    US_EQUITY = "US Equity"
    INTL_EQUITY = "International Equity"
    EMERGING_MARKETS = "Emerging Markets"
    FIXED_INCOME = "Fixed Income"
    REAL_ESTATE = "Real Estate"
    COMMODITIES = "Commodities"
    CASH = "Cash/Money Market"
    CRYPTO = "Cryptocurrency"
    ALTERNATIVES = "Alternatives"


# Fund database: ticker -> metadata
FUND_DATABASE: Dict[str, Dict[str, Any]] = {
    # ============================================
    # TOTAL MARKET ETFs (Highly Diversified)
    # ============================================
    "VTI": {
        "name": "Vanguard Total Stock Market ETF",
        "description": "Tracks the entire US stock market including large, mid, small, and micro caps",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Total Market",
        "holdings": 4000,
        "expense_ratio": 0.03,
        "dividend_yield": 1.5,
        "diversified": True,
        "benchmark": "CRSP US Total Market Index",
    },
    "VTSAX": {
        "name": "Vanguard Total Stock Market Index Fund",
        "description": "Mutual fund version of VTI - entire US stock market",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Total Market",
        "holdings": 4000,
        "expense_ratio": 0.04,
        "dividend_yield": 1.5,
        "diversified": True,
        "benchmark": "CRSP US Total Market Index",
    },
    "ITOT": {
        "name": "iShares Core S&P Total US Stock Market ETF",
        "description": "Tracks S&P Total Market Index - comprehensive US exposure",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Total Market",
        "holdings": 3500,
        "expense_ratio": 0.03,
        "dividend_yield": 1.4,
        "diversified": True,
    },
    "SWTSX": {
        "name": "Schwab Total Stock Market Index Fund",
        "description": "Schwab's total US market fund - similar to VTI/VTSAX",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Total Market",
        "holdings": 3500,
        "expense_ratio": 0.03,
        "dividend_yield": 1.4,
        "diversified": True,
    },
    "FSKAX": {
        "name": "Fidelity Total Market Index Fund",
        "description": "Fidelity's total US market fund",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Total Market",
        "holdings": 4000,
        "expense_ratio": 0.015,
        "dividend_yield": 1.4,
        "diversified": True,
    },

    # ============================================
    # S&P 500 ETFs (Large Cap US)
    # ============================================
    "VOO": {
        "name": "Vanguard S&P 500 ETF",
        "description": "Tracks the S&P 500 index - 500 largest US companies",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap",
        "holdings": 500,
        "expense_ratio": 0.03,
        "dividend_yield": 1.5,
        "diversified": True,
        "benchmark": "S&P 500",
    },
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "description": "Original S&P 500 ETF - most traded ETF in the world",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap",
        "holdings": 500,
        "expense_ratio": 0.09,
        "dividend_yield": 1.4,
        "diversified": True,
        "benchmark": "S&P 500",
    },
    "IVV": {
        "name": "iShares Core S&P 500 ETF",
        "description": "iShares S&P 500 tracker - low cost alternative to SPY",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap",
        "holdings": 500,
        "expense_ratio": 0.03,
        "dividend_yield": 1.5,
        "diversified": True,
        "benchmark": "S&P 500",
    },
    "VFIAX": {
        "name": "Vanguard 500 Index Fund Admiral",
        "description": "Mutual fund version of VOO - S&P 500 index",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap",
        "holdings": 500,
        "expense_ratio": 0.04,
        "dividend_yield": 1.5,
        "diversified": True,
        "benchmark": "S&P 500",
    },
    "FXAIX": {
        "name": "Fidelity 500 Index Fund",
        "description": "Fidelity's S&P 500 index fund",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap",
        "holdings": 500,
        "expense_ratio": 0.015,
        "dividend_yield": 1.5,
        "diversified": True,
        "benchmark": "S&P 500",
    },
    "SWPPX": {
        "name": "Schwab S&P 500 Index Fund",
        "description": "Schwab's S&P 500 index fund",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap",
        "holdings": 500,
        "expense_ratio": 0.02,
        "dividend_yield": 1.5,
        "diversified": True,
    },

    # ============================================
    # GROWTH ETFs
    # ============================================
    "VUG": {
        "name": "Vanguard Growth ETF",
        "description": "Large-cap US growth stocks - higher growth potential, higher volatility",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap Growth",
        "holdings": 200,
        "expense_ratio": 0.04,
        "dividend_yield": 0.6,
        "diversified": True,
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "description": "Tracks Nasdaq-100 - heavily weighted toward tech",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap Growth",
        "holdings": 100,
        "expense_ratio": 0.20,
        "dividend_yield": 0.5,
        "diversified": True,
        "sector_tilt": "Technology",
    },
    "QQQM": {
        "name": "Invesco Nasdaq 100 ETF",
        "description": "Lower-cost version of QQQ",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap Growth",
        "holdings": 100,
        "expense_ratio": 0.15,
        "dividend_yield": 0.5,
        "diversified": True,
        "sector_tilt": "Technology",
    },
    "IWF": {
        "name": "iShares Russell 1000 Growth ETF",
        "description": "Large-cap growth stocks from Russell 1000",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap Growth",
        "holdings": 450,
        "expense_ratio": 0.19,
        "dividend_yield": 0.6,
        "diversified": True,
    },
    "MGK": {
        "name": "Vanguard Mega Cap Growth ETF",
        "description": "Mega-cap growth stocks - the largest growth companies",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Mega Cap Growth",
        "holdings": 100,
        "expense_ratio": 0.07,
        "dividend_yield": 0.5,
        "diversified": True,
    },
    "SCHG": {
        "name": "Schwab US Large-Cap Growth ETF",
        "description": "Large-cap US growth stocks",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap Growth",
        "holdings": 250,
        "expense_ratio": 0.04,
        "dividend_yield": 0.5,
        "diversified": True,
    },

    # ============================================
    # VALUE ETFs
    # ============================================
    "VTV": {
        "name": "Vanguard Value ETF",
        "description": "Large-cap US value stocks - undervalued companies",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap Value",
        "holdings": 350,
        "expense_ratio": 0.04,
        "dividend_yield": 2.5,
        "diversified": True,
    },
    "IWD": {
        "name": "iShares Russell 1000 Value ETF",
        "description": "Large-cap value stocks from Russell 1000",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap Value",
        "holdings": 850,
        "expense_ratio": 0.19,
        "dividend_yield": 2.2,
        "diversified": True,
    },
    "SCHV": {
        "name": "Schwab US Large-Cap Value ETF",
        "description": "Large-cap US value stocks",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Large Cap Value",
        "holdings": 350,
        "expense_ratio": 0.04,
        "dividend_yield": 2.4,
        "diversified": True,
    },

    # ============================================
    # MID CAP ETFs
    # ============================================
    "VO": {
        "name": "Vanguard Mid-Cap ETF",
        "description": "Mid-cap US stocks - balance of growth and stability",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Mid Cap",
        "holdings": 350,
        "expense_ratio": 0.04,
        "dividend_yield": 1.5,
        "diversified": True,
    },
    "IJH": {
        "name": "iShares Core S&P Mid-Cap ETF",
        "description": "S&P MidCap 400 index tracker",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Mid Cap",
        "holdings": 400,
        "expense_ratio": 0.05,
        "dividend_yield": 1.4,
        "diversified": True,
    },
    "IVOO": {
        "name": "Vanguard S&P Mid-Cap 400 ETF",
        "description": "Tracks S&P MidCap 400",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Mid Cap",
        "holdings": 400,
        "expense_ratio": 0.10,
        "dividend_yield": 1.4,
        "diversified": True,
    },

    # ============================================
    # SMALL CAP ETFs
    # ============================================
    "VB": {
        "name": "Vanguard Small-Cap ETF",
        "description": "Small-cap US stocks - higher growth potential, higher risk",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Small Cap",
        "holdings": 1400,
        "expense_ratio": 0.05,
        "dividend_yield": 1.5,
        "diversified": True,
    },
    "IJR": {
        "name": "iShares Core S&P Small-Cap ETF",
        "description": "S&P SmallCap 600 index tracker",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Small Cap",
        "holdings": 600,
        "expense_ratio": 0.06,
        "dividend_yield": 1.4,
        "diversified": True,
    },
    "VBK": {
        "name": "Vanguard Small-Cap Growth ETF",
        "description": "Small-cap growth stocks",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Small Cap Growth",
        "holdings": 600,
        "expense_ratio": 0.07,
        "dividend_yield": 0.6,
        "diversified": True,
    },
    "VBR": {
        "name": "Vanguard Small-Cap Value ETF",
        "description": "Small-cap value stocks",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Small Cap Value",
        "holdings": 850,
        "expense_ratio": 0.07,
        "dividend_yield": 2.2,
        "diversified": True,
    },
    "IWM": {
        "name": "iShares Russell 2000 ETF",
        "description": "Russell 2000 small-cap index tracker",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Small Cap",
        "holdings": 2000,
        "expense_ratio": 0.19,
        "dividend_yield": 1.3,
        "diversified": True,
    },
    "SCHA": {
        "name": "Schwab US Small-Cap ETF",
        "description": "US small-cap stocks",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Small Cap",
        "holdings": 1800,
        "expense_ratio": 0.04,
        "dividend_yield": 1.4,
        "diversified": True,
    },

    # ============================================
    # DIVIDEND ETFs
    # ============================================
    "SCHD": {
        "name": "Schwab US Dividend Equity ETF",
        "description": "High-quality dividend growth stocks - popular for income",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Dividend",
        "holdings": 100,
        "expense_ratio": 0.06,
        "dividend_yield": 3.5,
        "diversified": True,
        "focus": "Dividend Growth",
    },
    "VIG": {
        "name": "Vanguard Dividend Appreciation ETF",
        "description": "Companies with 10+ years of dividend growth",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Dividend",
        "holdings": 290,
        "expense_ratio": 0.06,
        "dividend_yield": 1.8,
        "diversified": True,
        "focus": "Dividend Growth",
    },
    "VYM": {
        "name": "Vanguard High Dividend Yield ETF",
        "description": "High-yielding US dividend stocks",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Dividend",
        "holdings": 440,
        "expense_ratio": 0.06,
        "dividend_yield": 3.0,
        "diversified": True,
        "focus": "High Yield",
    },
    "DVY": {
        "name": "iShares Select Dividend ETF",
        "description": "High-yielding US dividend stocks",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Dividend",
        "holdings": 100,
        "expense_ratio": 0.38,
        "dividend_yield": 3.8,
        "diversified": True,
    },
    "DGRO": {
        "name": "iShares Core Dividend Growth ETF",
        "description": "Companies with sustainable dividend growth",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Dividend",
        "holdings": 420,
        "expense_ratio": 0.08,
        "dividend_yield": 2.3,
        "diversified": True,
    },

    # ============================================
    # INTERNATIONAL DEVELOPED MARKETS
    # ============================================
    "VXUS": {
        "name": "Vanguard Total International Stock ETF",
        "description": "All non-US stocks - developed and emerging markets",
        "asset_class": AssetClass.INTL_EQUITY,
        "sub_class": "Total International",
        "holdings": 8000,
        "expense_ratio": 0.07,
        "dividend_yield": 3.0,
        "diversified": True,
    },
    "VTIAX": {
        "name": "Vanguard Total International Stock Index Fund",
        "description": "Mutual fund version of VXUS",
        "asset_class": AssetClass.INTL_EQUITY,
        "sub_class": "Total International",
        "holdings": 8000,
        "expense_ratio": 0.11,
        "dividend_yield": 3.0,
        "diversified": True,
    },
    "IXUS": {
        "name": "iShares Core MSCI Total International Stock ETF",
        "description": "All non-US stocks - comprehensive international",
        "asset_class": AssetClass.INTL_EQUITY,
        "sub_class": "Total International",
        "holdings": 4400,
        "expense_ratio": 0.07,
        "dividend_yield": 2.8,
        "diversified": True,
    },
    "VEA": {
        "name": "Vanguard FTSE Developed Markets ETF",
        "description": "Developed markets outside US - Europe, Japan, Australia",
        "asset_class": AssetClass.INTL_EQUITY,
        "sub_class": "Developed Markets",
        "holdings": 4000,
        "expense_ratio": 0.05,
        "dividend_yield": 3.2,
        "diversified": True,
    },
    "IEFA": {
        "name": "iShares Core MSCI EAFE ETF",
        "description": "Developed markets - Europe, Australasia, Far East",
        "asset_class": AssetClass.INTL_EQUITY,
        "sub_class": "Developed Markets",
        "holdings": 2800,
        "expense_ratio": 0.07,
        "dividend_yield": 2.9,
        "diversified": True,
    },
    "EFA": {
        "name": "iShares MSCI EAFE ETF",
        "description": "EAFE index - developed markets ex-US and Canada",
        "asset_class": AssetClass.INTL_EQUITY,
        "sub_class": "Developed Markets",
        "holdings": 800,
        "expense_ratio": 0.32,
        "dividend_yield": 2.8,
        "diversified": True,
    },
    "SCHF": {
        "name": "Schwab International Equity ETF",
        "description": "Developed markets international stocks",
        "asset_class": AssetClass.INTL_EQUITY,
        "sub_class": "Developed Markets",
        "holdings": 1500,
        "expense_ratio": 0.06,
        "dividend_yield": 2.8,
        "diversified": True,
    },
    "SWISX": {
        "name": "Schwab International Index Fund",
        "description": "International developed markets mutual fund",
        "asset_class": AssetClass.INTL_EQUITY,
        "sub_class": "Developed Markets",
        "holdings": 1500,
        "expense_ratio": 0.06,
        "dividend_yield": 2.5,
        "diversified": True,
    },

    # ============================================
    # EMERGING MARKETS
    # ============================================
    "VWO": {
        "name": "Vanguard FTSE Emerging Markets ETF",
        "description": "Emerging market stocks - China, India, Brazil, etc.",
        "asset_class": AssetClass.EMERGING_MARKETS,
        "sub_class": "Broad Emerging",
        "holdings": 5500,
        "expense_ratio": 0.08,
        "dividend_yield": 3.2,
        "diversified": True,
    },
    "IEMG": {
        "name": "iShares Core MSCI Emerging Markets ETF",
        "description": "Emerging market stocks - comprehensive coverage",
        "asset_class": AssetClass.EMERGING_MARKETS,
        "sub_class": "Broad Emerging",
        "holdings": 2700,
        "expense_ratio": 0.09,
        "dividend_yield": 2.5,
        "diversified": True,
    },
    "EEM": {
        "name": "iShares MSCI Emerging Markets ETF",
        "description": "Emerging market stocks",
        "asset_class": AssetClass.EMERGING_MARKETS,
        "sub_class": "Broad Emerging",
        "holdings": 1200,
        "expense_ratio": 0.68,
        "dividend_yield": 2.3,
        "diversified": True,
    },
    "SCHE": {
        "name": "Schwab Emerging Markets Equity ETF",
        "description": "Emerging market stocks",
        "asset_class": AssetClass.EMERGING_MARKETS,
        "sub_class": "Broad Emerging",
        "holdings": 1600,
        "expense_ratio": 0.11,
        "dividend_yield": 2.8,
        "diversified": True,
    },

    # ============================================
    # BOND ETFs - US
    # ============================================
    "BND": {
        "name": "Vanguard Total Bond Market ETF",
        "description": "Total US bond market - investment grade bonds",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Total Bond Market",
        "holdings": 10000,
        "expense_ratio": 0.03,
        "dividend_yield": 4.5,
        "diversified": True,
    },
    "VBTLX": {
        "name": "Vanguard Total Bond Market Index Fund",
        "description": "Mutual fund version of BND",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Total Bond Market",
        "holdings": 10000,
        "expense_ratio": 0.05,
        "dividend_yield": 4.5,
        "diversified": True,
    },
    "AGG": {
        "name": "iShares Core US Aggregate Bond ETF",
        "description": "US investment grade bonds - Barclays Aggregate",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Total Bond Market",
        "holdings": 11000,
        "expense_ratio": 0.03,
        "dividend_yield": 4.3,
        "diversified": True,
    },
    "SCHZ": {
        "name": "Schwab US Aggregate Bond ETF",
        "description": "US aggregate bond index",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Total Bond Market",
        "holdings": 7000,
        "expense_ratio": 0.03,
        "dividend_yield": 4.2,
        "diversified": True,
    },
    "BSV": {
        "name": "Vanguard Short-Term Bond ETF",
        "description": "Short-term investment grade bonds - lower interest rate risk",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Short-Term",
        "holdings": 2500,
        "expense_ratio": 0.04,
        "dividend_yield": 4.0,
        "diversified": True,
    },
    "BIV": {
        "name": "Vanguard Intermediate-Term Bond ETF",
        "description": "Intermediate-term investment grade bonds",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Intermediate-Term",
        "holdings": 2000,
        "expense_ratio": 0.04,
        "dividend_yield": 4.5,
        "diversified": True,
    },
    "BLV": {
        "name": "Vanguard Long-Term Bond ETF",
        "description": "Long-term investment grade bonds - higher interest rate sensitivity",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Long-Term",
        "holdings": 3000,
        "expense_ratio": 0.04,
        "dividend_yield": 5.0,
        "diversified": True,
    },
    "LQD": {
        "name": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
        "description": "Investment grade corporate bonds",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Corporate",
        "holdings": 2500,
        "expense_ratio": 0.14,
        "dividend_yield": 5.2,
        "diversified": True,
    },
    "VCIT": {
        "name": "Vanguard Intermediate-Term Corporate Bond ETF",
        "description": "Intermediate-term corporate bonds",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Corporate",
        "holdings": 2000,
        "expense_ratio": 0.04,
        "dividend_yield": 5.0,
        "diversified": True,
    },
    "HYG": {
        "name": "iShares iBoxx $ High Yield Corporate Bond ETF",
        "description": "High yield (junk) bonds - higher risk, higher yield",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "High Yield",
        "holdings": 1200,
        "expense_ratio": 0.48,
        "dividend_yield": 6.5,
        "diversified": True,
    },
    "JNK": {
        "name": "SPDR Bloomberg High Yield Bond ETF",
        "description": "High yield corporate bonds",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "High Yield",
        "holdings": 1000,
        "expense_ratio": 0.40,
        "dividend_yield": 6.8,
        "diversified": True,
    },

    # ============================================
    # BOND ETFs - INTERNATIONAL
    # ============================================
    "BNDX": {
        "name": "Vanguard Total International Bond ETF",
        "description": "International investment grade bonds",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "International Bonds",
        "holdings": 6500,
        "expense_ratio": 0.07,
        "dividend_yield": 3.5,
        "diversified": True,
    },
    "IAGG": {
        "name": "iShares Core International Aggregate Bond ETF",
        "description": "International aggregate bonds",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "International Bonds",
        "holdings": 3500,
        "expense_ratio": 0.07,
        "dividend_yield": 3.2,
        "diversified": True,
    },

    # ============================================
    # TREASURY & TIPS
    # ============================================
    "GOVT": {
        "name": "iShares US Treasury Bond ETF",
        "description": "US Treasury bonds - safest fixed income",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Treasury",
        "holdings": 150,
        "expense_ratio": 0.05,
        "dividend_yield": 4.0,
        "diversified": True,
    },
    "SHY": {
        "name": "iShares 1-3 Year Treasury Bond ETF",
        "description": "Short-term treasury bonds - very low risk",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Treasury",
        "holdings": 80,
        "expense_ratio": 0.15,
        "dividend_yield": 4.2,
        "diversified": True,
    },
    "IEF": {
        "name": "iShares 7-10 Year Treasury Bond ETF",
        "description": "Intermediate treasury bonds",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Treasury",
        "holdings": 15,
        "expense_ratio": 0.15,
        "dividend_yield": 4.0,
        "diversified": True,
    },
    "TLT": {
        "name": "iShares 20+ Year Treasury Bond ETF",
        "description": "Long-term treasury bonds - high interest rate sensitivity",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "Treasury",
        "holdings": 40,
        "expense_ratio": 0.15,
        "dividend_yield": 4.5,
        "diversified": True,
    },
    "TIPS": {
        "name": "iShares TIPS Bond ETF",
        "description": "Treasury Inflation-Protected Securities",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "TIPS",
        "holdings": 50,
        "expense_ratio": 0.19,
        "dividend_yield": 2.5,
        "diversified": True,
    },
    "VTIP": {
        "name": "Vanguard Short-Term Inflation-Protected Securities ETF",
        "description": "Short-term TIPS - inflation protection with less duration risk",
        "asset_class": AssetClass.FIXED_INCOME,
        "sub_class": "TIPS",
        "holdings": 20,
        "expense_ratio": 0.04,
        "dividend_yield": 2.8,
        "diversified": True,
    },

    # ============================================
    # REAL ESTATE (REITs)
    # ============================================
    "VNQ": {
        "name": "Vanguard Real Estate ETF",
        "description": "US real estate investment trusts (REITs)",
        "asset_class": AssetClass.REAL_ESTATE,
        "sub_class": "US REITs",
        "holdings": 160,
        "expense_ratio": 0.12,
        "dividend_yield": 4.0,
        "diversified": True,
    },
    "VGSLX": {
        "name": "Vanguard Real Estate Index Fund",
        "description": "Mutual fund version of VNQ",
        "asset_class": AssetClass.REAL_ESTATE,
        "sub_class": "US REITs",
        "holdings": 160,
        "expense_ratio": 0.12,
        "dividend_yield": 4.0,
        "diversified": True,
    },
    "IYR": {
        "name": "iShares US Real Estate ETF",
        "description": "US real estate stocks and REITs",
        "asset_class": AssetClass.REAL_ESTATE,
        "sub_class": "US REITs",
        "holdings": 80,
        "expense_ratio": 0.40,
        "dividend_yield": 3.5,
        "diversified": True,
    },
    "SCHH": {
        "name": "Schwab US REIT ETF",
        "description": "US REITs",
        "asset_class": AssetClass.REAL_ESTATE,
        "sub_class": "US REITs",
        "holdings": 120,
        "expense_ratio": 0.07,
        "dividend_yield": 3.8,
        "diversified": True,
    },
    "VNQI": {
        "name": "Vanguard Global ex-US Real Estate ETF",
        "description": "International real estate",
        "asset_class": AssetClass.REAL_ESTATE,
        "sub_class": "International REITs",
        "holdings": 700,
        "expense_ratio": 0.12,
        "dividend_yield": 4.5,
        "diversified": True,
    },

    # ============================================
    # SECTOR ETFs - TECHNOLOGY
    # ============================================
    "VGT": {
        "name": "Vanguard Information Technology ETF",
        "description": "US technology sector - AAPL, MSFT, NVDA, etc.",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Technology Sector",
        "holdings": 320,
        "expense_ratio": 0.10,
        "dividend_yield": 0.7,
        "diversified": True,
        "sector_tilt": "Technology",
    },
    "XLK": {
        "name": "Technology Select Sector SPDR Fund",
        "description": "S&P 500 technology sector",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Technology Sector",
        "holdings": 65,
        "expense_ratio": 0.10,
        "dividend_yield": 0.8,
        "diversified": True,
        "sector_tilt": "Technology",
    },
    "SMH": {
        "name": "VanEck Semiconductor ETF",
        "description": "Semiconductor companies - NVDA, AMD, AVGO, etc.",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Semiconductors",
        "holdings": 25,
        "expense_ratio": 0.35,
        "dividend_yield": 0.5,
        "diversified": False,
        "sector_tilt": "Semiconductors",
    },

    # ============================================
    # SECTOR ETFs - HEALTHCARE
    # ============================================
    "VHT": {
        "name": "Vanguard Health Care ETF",
        "description": "US healthcare sector",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Healthcare Sector",
        "holdings": 430,
        "expense_ratio": 0.10,
        "dividend_yield": 1.4,
        "diversified": True,
        "sector_tilt": "Healthcare",
    },
    "XLV": {
        "name": "Health Care Select Sector SPDR Fund",
        "description": "S&P 500 healthcare sector",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Healthcare Sector",
        "holdings": 60,
        "expense_ratio": 0.10,
        "dividend_yield": 1.5,
        "diversified": True,
        "sector_tilt": "Healthcare",
    },

    # ============================================
    # SECTOR ETFs - FINANCIALS
    # ============================================
    "VFH": {
        "name": "Vanguard Financials ETF",
        "description": "US financial sector",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Financials Sector",
        "holdings": 400,
        "expense_ratio": 0.10,
        "dividend_yield": 2.0,
        "diversified": True,
        "sector_tilt": "Financials",
    },
    "XLF": {
        "name": "Financial Select Sector SPDR Fund",
        "description": "S&P 500 financial sector",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Financials Sector",
        "holdings": 70,
        "expense_ratio": 0.10,
        "dividend_yield": 1.8,
        "diversified": True,
        "sector_tilt": "Financials",
    },

    # ============================================
    # SECTOR ETFs - ENERGY
    # ============================================
    "VDE": {
        "name": "Vanguard Energy ETF",
        "description": "US energy sector - oil, gas, energy services",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Energy Sector",
        "holdings": 110,
        "expense_ratio": 0.10,
        "dividend_yield": 3.5,
        "diversified": True,
        "sector_tilt": "Energy",
    },
    "XLE": {
        "name": "Energy Select Sector SPDR Fund",
        "description": "S&P 500 energy sector",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Energy Sector",
        "holdings": 22,
        "expense_ratio": 0.10,
        "dividend_yield": 3.8,
        "diversified": True,
        "sector_tilt": "Energy",
    },

    # ============================================
    # SECTOR ETFs - CONSUMER
    # ============================================
    "VCR": {
        "name": "Vanguard Consumer Discretionary ETF",
        "description": "Consumer discretionary sector - retail, autos, etc.",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Consumer Discretionary",
        "holdings": 300,
        "expense_ratio": 0.10,
        "dividend_yield": 0.8,
        "diversified": True,
        "sector_tilt": "Consumer Discretionary",
    },
    "VDC": {
        "name": "Vanguard Consumer Staples ETF",
        "description": "Consumer staples sector - food, household products",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Consumer Staples",
        "holdings": 100,
        "expense_ratio": 0.10,
        "dividend_yield": 2.5,
        "diversified": True,
        "sector_tilt": "Consumer Staples",
    },
    "XLY": {
        "name": "Consumer Discretionary Select Sector SPDR",
        "description": "S&P 500 consumer discretionary",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Consumer Discretionary",
        "holdings": 50,
        "expense_ratio": 0.10,
        "dividend_yield": 0.9,
        "diversified": True,
    },
    "XLP": {
        "name": "Consumer Staples Select Sector SPDR",
        "description": "S&P 500 consumer staples",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Consumer Staples",
        "holdings": 40,
        "expense_ratio": 0.10,
        "dividend_yield": 2.6,
        "diversified": True,
    },

    # ============================================
    # SECTOR ETFs - UTILITIES & INDUSTRIALS
    # ============================================
    "VPU": {
        "name": "Vanguard Utilities ETF",
        "description": "Utilities sector - electric, gas, water utilities",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Utilities Sector",
        "holdings": 65,
        "expense_ratio": 0.10,
        "dividend_yield": 3.2,
        "diversified": True,
        "sector_tilt": "Utilities",
    },
    "VIS": {
        "name": "Vanguard Industrials ETF",
        "description": "Industrial sector - manufacturing, aerospace, etc.",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Industrials Sector",
        "holdings": 360,
        "expense_ratio": 0.10,
        "dividend_yield": 1.5,
        "diversified": True,
        "sector_tilt": "Industrials",
    },
    "XLU": {
        "name": "Utilities Select Sector SPDR Fund",
        "description": "S&P 500 utilities sector",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Utilities Sector",
        "holdings": 30,
        "expense_ratio": 0.10,
        "dividend_yield": 3.0,
        "diversified": True,
    },
    "XLI": {
        "name": "Industrial Select Sector SPDR Fund",
        "description": "S&P 500 industrials sector",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Industrials Sector",
        "holdings": 75,
        "expense_ratio": 0.10,
        "dividend_yield": 1.4,
        "diversified": True,
    },

    # ============================================
    # MONEY MARKET / CASH
    # ============================================
    "VMFXX": {
        "name": "Vanguard Federal Money Market Fund",
        "description": "Government money market - near-zero risk",
        "asset_class": AssetClass.CASH,
        "sub_class": "Money Market",
        "holdings": 50,
        "expense_ratio": 0.11,
        "dividend_yield": 5.0,
        "diversified": True,
    },
    "SPAXX": {
        "name": "Fidelity Government Money Market Fund",
        "description": "Government money market fund",
        "asset_class": AssetClass.CASH,
        "sub_class": "Money Market",
        "holdings": 50,
        "expense_ratio": 0.42,
        "dividend_yield": 4.9,
        "diversified": True,
    },
    "SWVXX": {
        "name": "Schwab Value Advantage Money Fund",
        "description": "Money market fund",
        "asset_class": AssetClass.CASH,
        "sub_class": "Money Market",
        "holdings": 100,
        "expense_ratio": 0.34,
        "dividend_yield": 5.0,
        "diversified": True,
    },
    "FZFXX": {
        "name": "Fidelity Treasury Money Market Fund",
        "description": "Treasury money market fund",
        "asset_class": AssetClass.CASH,
        "sub_class": "Money Market",
        "holdings": 30,
        "expense_ratio": 0.42,
        "dividend_yield": 4.8,
        "diversified": True,
    },

    # ============================================
    # TARGET DATE FUNDS (Vanguard)
    # ============================================
    "VFFVX": {
        "name": "Vanguard Target Retirement 2055 Fund",
        "description": "All-in-one fund for ~2055 retirement - automatically rebalances",
        "asset_class": AssetClass.US_EQUITY,  # Primary, but contains bonds
        "sub_class": "Target Date",
        "holdings": 4,  # Fund of funds
        "expense_ratio": 0.08,
        "dividend_yield": 1.8,
        "diversified": True,
        "target_year": 2055,
        "auto_rebalance": True,
    },
    "VFIFX": {
        "name": "Vanguard Target Retirement 2050 Fund",
        "description": "All-in-one fund for ~2050 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 4,
        "expense_ratio": 0.08,
        "dividend_yield": 1.8,
        "diversified": True,
        "target_year": 2050,
        "auto_rebalance": True,
    },
    "VTIVX": {
        "name": "Vanguard Target Retirement 2045 Fund",
        "description": "All-in-one fund for ~2045 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 4,
        "expense_ratio": 0.08,
        "dividend_yield": 1.9,
        "diversified": True,
        "target_year": 2045,
        "auto_rebalance": True,
    },
    "VTHRX": {
        "name": "Vanguard Target Retirement 2040 Fund",
        "description": "All-in-one fund for ~2040 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 4,
        "expense_ratio": 0.08,
        "dividend_yield": 2.0,
        "diversified": True,
        "target_year": 2040,
        "auto_rebalance": True,
    },
    "VTTHX": {
        "name": "Vanguard Target Retirement 2035 Fund",
        "description": "All-in-one fund for ~2035 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 4,
        "expense_ratio": 0.08,
        "dividend_yield": 2.1,
        "diversified": True,
        "target_year": 2035,
        "auto_rebalance": True,
    },
    "VTWNX": {
        "name": "Vanguard Target Retirement 2030 Fund",
        "description": "All-in-one fund for ~2030 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 4,
        "expense_ratio": 0.08,
        "dividend_yield": 2.2,
        "diversified": True,
        "target_year": 2030,
        "auto_rebalance": True,
    },
    "VTTVX": {
        "name": "Vanguard Target Retirement 2025 Fund",
        "description": "All-in-one fund for ~2025 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 4,
        "expense_ratio": 0.08,
        "dividend_yield": 2.4,
        "diversified": True,
        "target_year": 2025,
        "auto_rebalance": True,
    },
    "VTENX": {
        "name": "Vanguard Target Retirement 2060 Fund",
        "description": "All-in-one fund for ~2060 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 4,
        "expense_ratio": 0.08,
        "dividend_yield": 1.7,
        "diversified": True,
        "target_year": 2060,
        "auto_rebalance": True,
    },
    "VTTSX": {
        "name": "Vanguard Target Retirement 2065 Fund",
        "description": "All-in-one fund for ~2065 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 4,
        "expense_ratio": 0.08,
        "dividend_yield": 1.7,
        "diversified": True,
        "target_year": 2065,
        "auto_rebalance": True,
    },

    # ============================================
    # TARGET DATE FUNDS (Fidelity Freedom Index)
    # ============================================
    "FIPFX": {
        "name": "Fidelity Freedom Index 2055 Fund",
        "description": "Fidelity target date fund for ~2055 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 5,
        "expense_ratio": 0.12,
        "dividend_yield": 1.8,
        "diversified": True,
        "target_year": 2055,
        "auto_rebalance": True,
    },
    "FIPEX": {
        "name": "Fidelity Freedom Index 2050 Fund",
        "description": "Fidelity target date fund for ~2050 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 5,
        "expense_ratio": 0.12,
        "dividend_yield": 1.8,
        "diversified": True,
        "target_year": 2050,
        "auto_rebalance": True,
    },
    "FIPDX": {
        "name": "Fidelity Freedom Index 2045 Fund",
        "description": "Fidelity target date fund for ~2045 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 5,
        "expense_ratio": 0.12,
        "dividend_yield": 1.9,
        "diversified": True,
        "target_year": 2045,
        "auto_rebalance": True,
    },
    "FBIFX": {
        "name": "Fidelity Freedom Index 2040 Fund",
        "description": "Fidelity target date fund for ~2040 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 5,
        "expense_ratio": 0.12,
        "dividend_yield": 2.0,
        "diversified": True,
        "target_year": 2040,
        "auto_rebalance": True,
    },
    "FBIHX": {
        "name": "Fidelity Freedom Index 2035 Fund",
        "description": "Fidelity target date fund for ~2035 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 5,
        "expense_ratio": 0.12,
        "dividend_yield": 2.1,
        "diversified": True,
        "target_year": 2035,
        "auto_rebalance": True,
    },
    "FXIFX": {
        "name": "Fidelity Freedom Index 2030 Fund",
        "description": "Fidelity target date fund for ~2030 retirement",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Target Date",
        "holdings": 5,
        "expense_ratio": 0.12,
        "dividend_yield": 2.2,
        "diversified": True,
        "target_year": 2030,
        "auto_rebalance": True,
    },

    # ============================================
    # POPULAR INDIVIDUAL STOCKS (Mega Caps)
    # ============================================
    "AAPL": {
        "name": "Apple Inc.",
        "description": "Technology - iPhones, Macs, services, wearables",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.5,
        "diversified": False,
        "sector": "Technology",
        "market_cap": "Mega Cap",
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "description": "Technology - Windows, Azure, Office, gaming",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.8,
        "diversified": False,
        "sector": "Technology",
        "market_cap": "Mega Cap",
    },
    "GOOGL": {
        "name": "Alphabet Inc. (Google) Class A",
        "description": "Technology - Search, advertising, cloud, YouTube",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": False,
        "sector": "Communication Services",
        "market_cap": "Mega Cap",
    },
    "GOOG": {
        "name": "Alphabet Inc. (Google) Class C",
        "description": "Technology - Same as GOOGL, no voting rights",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": False,
        "sector": "Communication Services",
        "market_cap": "Mega Cap",
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "description": "E-commerce, cloud (AWS), streaming, devices",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": False,
        "sector": "Consumer Discretionary",
        "market_cap": "Mega Cap",
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "description": "Semiconductors - GPUs, AI chips, data center",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.03,
        "diversified": False,
        "sector": "Technology",
        "market_cap": "Mega Cap",
        "volatility": "High",
    },
    "META": {
        "name": "Meta Platforms Inc. (Facebook)",
        "description": "Social media - Facebook, Instagram, WhatsApp, Reality Labs",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.4,
        "diversified": False,
        "sector": "Communication Services",
        "market_cap": "Mega Cap",
    },
    "TSLA": {
        "name": "Tesla Inc.",
        "description": "Electric vehicles, energy storage, solar",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": False,
        "sector": "Consumer Discretionary",
        "market_cap": "Mega Cap",
        "volatility": "Very High",
    },
    "BRK.B": {
        "name": "Berkshire Hathaway Inc. Class B",
        "description": "Diversified holding company - insurance, utilities, investments",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": False,
        "sector": "Financials",
        "market_cap": "Mega Cap",
    },
    "JPM": {
        "name": "JPMorgan Chase & Co.",
        "description": "Financial services - banking, investment banking, asset management",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 2.3,
        "diversified": False,
        "sector": "Financials",
        "market_cap": "Mega Cap",
    },
    "JNJ": {
        "name": "Johnson & Johnson",
        "description": "Healthcare - pharmaceuticals, medical devices, consumer health",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 3.0,
        "diversified": False,
        "sector": "Healthcare",
        "market_cap": "Mega Cap",
    },
    "V": {
        "name": "Visa Inc.",
        "description": "Payment technology - card network, digital payments",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.8,
        "diversified": False,
        "sector": "Financials",
        "market_cap": "Mega Cap",
    },
    "MA": {
        "name": "Mastercard Inc.",
        "description": "Payment technology - card network, digital payments",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.6,
        "diversified": False,
        "sector": "Financials",
        "market_cap": "Mega Cap",
    },
    "UNH": {
        "name": "UnitedHealth Group Inc.",
        "description": "Healthcare - health insurance, healthcare services",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 1.4,
        "diversified": False,
        "sector": "Healthcare",
        "market_cap": "Mega Cap",
    },
    "PG": {
        "name": "Procter & Gamble Co.",
        "description": "Consumer staples - household products, personal care",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 2.4,
        "diversified": False,
        "sector": "Consumer Staples",
        "market_cap": "Mega Cap",
    },
    "HD": {
        "name": "The Home Depot Inc.",
        "description": "Home improvement retail",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 2.5,
        "diversified": False,
        "sector": "Consumer Discretionary",
        "market_cap": "Mega Cap",
    },
    "KO": {
        "name": "The Coca-Cola Company",
        "description": "Beverages - soft drinks, water, juices",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 3.0,
        "diversified": False,
        "sector": "Consumer Staples",
        "market_cap": "Mega Cap",
    },
    "PEP": {
        "name": "PepsiCo Inc.",
        "description": "Beverages and snacks - Pepsi, Frito-Lay, Gatorade",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 2.8,
        "diversified": False,
        "sector": "Consumer Staples",
        "market_cap": "Mega Cap",
    },
    "DIS": {
        "name": "The Walt Disney Company",
        "description": "Entertainment - theme parks, streaming, media",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": False,
        "sector": "Communication Services",
        "market_cap": "Large Cap",
    },
    "NFLX": {
        "name": "Netflix Inc.",
        "description": "Streaming entertainment",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": False,
        "sector": "Communication Services",
        "market_cap": "Large Cap",
    },
    "AMD": {
        "name": "Advanced Micro Devices Inc.",
        "description": "Semiconductors - CPUs, GPUs, data center chips",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": False,
        "sector": "Technology",
        "market_cap": "Large Cap",
        "volatility": "High",
    },
    "AVGO": {
        "name": "Broadcom Inc.",
        "description": "Semiconductors - networking, broadband, storage",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 1.4,
        "diversified": False,
        "sector": "Technology",
        "market_cap": "Mega Cap",
    },
    "CRM": {
        "name": "Salesforce Inc.",
        "description": "Software - CRM, cloud applications, enterprise software",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.6,
        "diversified": False,
        "sector": "Technology",
        "market_cap": "Large Cap",
    },
    "COST": {
        "name": "Costco Wholesale Corporation",
        "description": "Retail - membership warehouse clubs",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.6,
        "diversified": False,
        "sector": "Consumer Staples",
        "market_cap": "Large Cap",
    },
    "ABBV": {
        "name": "AbbVie Inc.",
        "description": "Pharmaceuticals - Humira, immunology, oncology",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 3.8,
        "diversified": False,
        "sector": "Healthcare",
        "market_cap": "Large Cap",
    },
    "LLY": {
        "name": "Eli Lilly and Company",
        "description": "Pharmaceuticals - diabetes, oncology, neuroscience",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 0.7,
        "diversified": False,
        "sector": "Healthcare",
        "market_cap": "Mega Cap",
    },
    "MRK": {
        "name": "Merck & Co. Inc.",
        "description": "Pharmaceuticals - vaccines, oncology, animal health",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 2.8,
        "diversified": False,
        "sector": "Healthcare",
        "market_cap": "Large Cap",
    },
    "PFE": {
        "name": "Pfizer Inc.",
        "description": "Pharmaceuticals - vaccines, oncology, rare diseases",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 5.8,
        "diversified": False,
        "sector": "Healthcare",
        "market_cap": "Large Cap",
    },
    "BAC": {
        "name": "Bank of America Corporation",
        "description": "Financial services - banking, investments, wealth management",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 2.6,
        "diversified": False,
        "sector": "Financials",
        "market_cap": "Mega Cap",
    },
    "WFC": {
        "name": "Wells Fargo & Company",
        "description": "Financial services - banking, mortgage, investments",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 2.4,
        "diversified": False,
        "sector": "Financials",
        "market_cap": "Large Cap",
    },
    "XOM": {
        "name": "Exxon Mobil Corporation",
        "description": "Energy - oil and gas exploration, refining, chemicals",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 3.4,
        "diversified": False,
        "sector": "Energy",
        "market_cap": "Mega Cap",
    },
    "CVX": {
        "name": "Chevron Corporation",
        "description": "Energy - oil and gas exploration, refining",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Individual Stock",
        "holdings": 1,
        "expense_ratio": 0,
        "dividend_yield": 4.2,
        "diversified": False,
        "sector": "Energy",
        "market_cap": "Mega Cap",
    },

    # ============================================
    # THEMATIC / INNOVATION ETFs
    # ============================================
    "ARKK": {
        "name": "ARK Innovation ETF",
        "description": "Disruptive innovation - genomics, fintech, AI (actively managed)",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Thematic",
        "holdings": 35,
        "expense_ratio": 0.75,
        "dividend_yield": 0,
        "diversified": False,
        "volatility": "Very High",
        "actively_managed": True,
    },
    "ARKG": {
        "name": "ARK Genomic Revolution ETF",
        "description": "Genomics and biotech innovation (actively managed)",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Thematic",
        "holdings": 40,
        "expense_ratio": 0.75,
        "dividend_yield": 0,
        "diversified": False,
        "volatility": "Very High",
        "sector_tilt": "Healthcare",
        "actively_managed": True,
    },
    "ARKW": {
        "name": "ARK Next Generation Internet ETF",
        "description": "Next-gen internet technologies (actively managed)",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Thematic",
        "holdings": 35,
        "expense_ratio": 0.75,
        "dividend_yield": 0,
        "diversified": False,
        "volatility": "Very High",
        "sector_tilt": "Technology",
        "actively_managed": True,
    },
    "ICLN": {
        "name": "iShares Global Clean Energy ETF",
        "description": "Clean energy companies - solar, wind, electric vehicles",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Thematic",
        "holdings": 100,
        "expense_ratio": 0.40,
        "dividend_yield": 0.8,
        "diversified": True,
        "volatility": "High",
        "sector_tilt": "Clean Energy",
    },
    "TAN": {
        "name": "Invesco Solar ETF",
        "description": "Solar energy companies",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Thematic",
        "holdings": 50,
        "expense_ratio": 0.50,
        "dividend_yield": 0.5,
        "diversified": False,
        "volatility": "Very High",
        "sector_tilt": "Solar Energy",
    },
    "BOTZ": {
        "name": "Global X Robotics & Artificial Intelligence ETF",
        "description": "Robotics and AI companies",
        "asset_class": AssetClass.US_EQUITY,
        "sub_class": "Thematic",
        "holdings": 40,
        "expense_ratio": 0.68,
        "dividend_yield": 0.2,
        "diversified": False,
        "volatility": "High",
        "sector_tilt": "Technology",
    },

    # ============================================
    # COMMODITIES
    # ============================================
    "GLD": {
        "name": "SPDR Gold Shares",
        "description": "Physical gold bullion - inflation hedge",
        "asset_class": AssetClass.COMMODITIES,
        "sub_class": "Gold",
        "holdings": 1,
        "expense_ratio": 0.40,
        "dividend_yield": 0,
        "diversified": False,
    },
    "IAU": {
        "name": "iShares Gold Trust",
        "description": "Physical gold - lower cost than GLD",
        "asset_class": AssetClass.COMMODITIES,
        "sub_class": "Gold",
        "holdings": 1,
        "expense_ratio": 0.25,
        "dividend_yield": 0,
        "diversified": False,
    },
    "SLV": {
        "name": "iShares Silver Trust",
        "description": "Physical silver",
        "asset_class": AssetClass.COMMODITIES,
        "sub_class": "Silver",
        "holdings": 1,
        "expense_ratio": 0.50,
        "dividend_yield": 0,
        "diversified": False,
    },
    "GSG": {
        "name": "iShares S&P GSCI Commodity-Indexed Trust",
        "description": "Broad commodity exposure - energy, agriculture, metals",
        "asset_class": AssetClass.COMMODITIES,
        "sub_class": "Broad Commodities",
        "holdings": 24,
        "expense_ratio": 0.75,
        "dividend_yield": 0,
        "diversified": True,
    },
    "DBC": {
        "name": "Invesco DB Commodity Index Tracking Fund",
        "description": "Diversified commodity futures",
        "asset_class": AssetClass.COMMODITIES,
        "sub_class": "Broad Commodities",
        "holdings": 14,
        "expense_ratio": 0.85,
        "dividend_yield": 0,
        "diversified": True,
    },

    # ============================================
    # CRYPTOCURRENCY-RELATED
    # ============================================
    "BITO": {
        "name": "ProShares Bitcoin Strategy ETF",
        "description": "Bitcoin futures ETF - NOT direct Bitcoin ownership",
        "asset_class": AssetClass.CRYPTO,
        "sub_class": "Bitcoin Futures",
        "holdings": 1,
        "expense_ratio": 0.95,
        "dividend_yield": 0,
        "diversified": False,
        "volatility": "Extreme",
    },
    "IBIT": {
        "name": "iShares Bitcoin Trust",
        "description": "Spot Bitcoin ETF - holds actual Bitcoin",
        "asset_class": AssetClass.CRYPTO,
        "sub_class": "Bitcoin Spot",
        "holdings": 1,
        "expense_ratio": 0.25,
        "dividend_yield": 0,
        "diversified": False,
        "volatility": "Extreme",
    },
    "FBTC": {
        "name": "Fidelity Wise Origin Bitcoin Fund",
        "description": "Spot Bitcoin ETF - holds actual Bitcoin",
        "asset_class": AssetClass.CRYPTO,
        "sub_class": "Bitcoin Spot",
        "holdings": 1,
        "expense_ratio": 0.25,
        "dividend_yield": 0,
        "diversified": False,
        "volatility": "Extreme",
    },
    "GBTC": {
        "name": "Grayscale Bitcoin Trust",
        "description": "Bitcoin trust - converted to spot ETF",
        "asset_class": AssetClass.CRYPTO,
        "sub_class": "Bitcoin",
        "holdings": 1,
        "expense_ratio": 1.50,
        "dividend_yield": 0,
        "diversified": False,
        "volatility": "Extreme",
    },

    # ============================================
    # CASH PLACEHOLDER
    # ============================================
    "CASH": {
        "name": "Cash",
        "description": "Cash or cash equivalents",
        "asset_class": AssetClass.CASH,
        "sub_class": "Cash",
        "holdings": 0,
        "expense_ratio": 0,
        "dividend_yield": 0,
        "diversified": True,
    },
}


class FundKnowledgeBase:
    """Provides fund metadata lookup and enrichment."""

    def __init__(self):
        self.database = FUND_DATABASE

    def get_fund_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get fund information by ticker."""
        ticker = ticker.upper().strip()
        return self.database.get(ticker)

    def get_asset_class(self, ticker: str) -> Optional[str]:
        """Get the asset class for a ticker."""
        info = self.get_fund_info(ticker)
        return info.get("asset_class") if info else None

    def get_expense_ratio(self, ticker: str) -> Optional[float]:
        """Get the expense ratio for a ticker."""
        info = self.get_fund_info(ticker)
        return info.get("expense_ratio") if info else None

    def is_diversified(self, ticker: str) -> bool:
        """Check if a fund is inherently diversified."""
        info = self.get_fund_info(ticker)
        return info.get("diversified", False) if info else False

    def is_target_date_fund(self, ticker: str) -> bool:
        """Check if a fund is a target date fund."""
        info = self.get_fund_info(ticker)
        return info.get("sub_class") == "Target Date" if info else False

    def get_holdings_count(self, ticker: str) -> Optional[int]:
        """Get the number of underlying holdings."""
        info = self.get_fund_info(ticker)
        return info.get("holdings") if info else None

    def enrich_holding(self, ticker: str, description: str = "") -> Dict[str, Any]:
        """
        Enrich a holding with semantic information.

        Returns a dict with all available metadata, or inferred info if unknown.
        """
        info = self.get_fund_info(ticker)

        if info:
            return {
                "ticker": ticker,
                "known": True,
                **info
            }

        # Try to infer from description
        desc_lower = description.lower() if description else ""

        inferred = {
            "ticker": ticker,
            "known": False,
            "name": description or ticker,
            "description": description,
        }

        # Infer asset class from description keywords
        if any(kw in desc_lower for kw in ["target", "retirement", "2030", "2035", "2040", "2045", "2050", "2055", "2060"]):
            inferred["asset_class"] = AssetClass.US_EQUITY
            inferred["sub_class"] = "Target Date"
            inferred["diversified"] = True
        elif any(kw in desc_lower for kw in ["bond", "fixed income", "treasury", "income"]):
            inferred["asset_class"] = AssetClass.FIXED_INCOME
            inferred["diversified"] = True
        elif any(kw in desc_lower for kw in ["international", "foreign", "global", "world"]):
            inferred["asset_class"] = AssetClass.INTL_EQUITY
            inferred["diversified"] = True
        elif any(kw in desc_lower for kw in ["emerging", "em"]):
            inferred["asset_class"] = AssetClass.EMERGING_MARKETS
            inferred["diversified"] = True
        elif any(kw in desc_lower for kw in ["real estate", "reit"]):
            inferred["asset_class"] = AssetClass.REAL_ESTATE
            inferred["diversified"] = True
        elif any(kw in desc_lower for kw in ["money market", "cash", "savings"]):
            inferred["asset_class"] = AssetClass.CASH
            inferred["diversified"] = True
        elif any(kw in desc_lower for kw in ["index", "etf", "fund", "500", "total market"]):
            inferred["asset_class"] = AssetClass.US_EQUITY
            inferred["diversified"] = True
        else:
            # Assume individual stock if short ticker and no fund keywords
            if len(ticker) <= 5 and not any(kw in desc_lower for kw in ["fund", "etf", "index"]):
                inferred["asset_class"] = AssetClass.US_EQUITY
                inferred["sub_class"] = "Individual Stock"
                inferred["diversified"] = False

        return inferred

    def get_similar_funds(self, ticker: str, limit: int = 3) -> List[str]:
        """Get similar funds in the same category with potentially lower costs."""
        info = self.get_fund_info(ticker)
        if not info:
            return []

        asset_class = info.get("asset_class")
        sub_class = info.get("sub_class")
        expense = info.get("expense_ratio", 0)

        similar = []
        for other_ticker, other_info in self.database.items():
            if other_ticker == ticker:
                continue
            if other_info.get("asset_class") == asset_class:
                if other_info.get("sub_class") == sub_class or sub_class in ["Total Market", "Large Cap"]:
                    if other_info.get("expense_ratio", 1) <= expense:
                        similar.append((other_ticker, other_info.get("expense_ratio", 0)))

        # Sort by expense ratio
        similar.sort(key=lambda x: x[1])
        return [t for t, _ in similar[:limit]]


# Module-level convenience function
_kb = FundKnowledgeBase()

def get_fund_info(ticker: str) -> Optional[Dict[str, Any]]:
    """Get fund information by ticker."""
    return _kb.get_fund_info(ticker)

def enrich_holding(ticker: str, description: str = "") -> Dict[str, Any]:
    """Enrich a holding with semantic information."""
    return _kb.enrich_holding(ticker, description)

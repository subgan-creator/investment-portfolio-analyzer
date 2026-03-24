"""
ETF Overlap Detection - Identifies redundant holdings in a portfolio.

Provides warnings when multiple funds hold essentially the same stocks,
helping users avoid unintentional concentration.
"""

from typing import Dict, List, Tuple, Set, Any, Optional


# Known overlap percentages between common ETF pairs
# Format: (ticker1, ticker2): overlap_percent
# Overlap is approximate - based on typical holdings overlap
KNOWN_OVERLAPS: Dict[Tuple[str, str], int] = {
    # ============================================
    # Total Market vs S&P 500 (S&P 500 is subset of Total Market)
    # ============================================
    ("VTI", "VOO"): 85,
    ("VTI", "SPY"): 85,
    ("VTI", "IVV"): 85,
    ("VTI", "VFIAX"): 85,
    ("VTI", "FXAIX"): 85,
    ("VTI", "SWPPX"): 85,
    ("VTSAX", "VOO"): 85,
    ("VTSAX", "SPY"): 85,
    ("VTSAX", "VFIAX"): 85,
    ("ITOT", "VOO"): 85,
    ("ITOT", "SPY"): 85,
    ("ITOT", "IVV"): 85,
    ("SWTSX", "VOO"): 85,
    ("SWTSX", "SWPPX"): 85,
    ("FSKAX", "FXAIX"): 85,

    # S&P 500 funds are essentially identical
    ("VOO", "SPY"): 99,
    ("VOO", "IVV"): 99,
    ("VOO", "VFIAX"): 99,
    ("VOO", "FXAIX"): 99,
    ("VOO", "SWPPX"): 99,
    ("SPY", "IVV"): 99,
    ("SPY", "VFIAX"): 99,
    ("VFIAX", "FXAIX"): 99,

    # Total market funds are essentially identical
    ("VTI", "VTSAX"): 99,
    ("VTI", "ITOT"): 99,
    ("VTI", "SWTSX"): 99,
    ("VTI", "FSKAX"): 99,
    ("VTSAX", "ITOT"): 99,
    ("VTSAX", "SWTSX"): 99,
    ("VTSAX", "FSKAX"): 99,

    # ============================================
    # Growth ETFs overlap with each other and with QQQ/S&P 500
    # ============================================
    ("QQQ", "VGT"): 65,  # QQQ is tech-heavy, VGT is pure tech
    ("QQQ", "VOO"): 45,  # Many QQQ holdings are S&P 500 top holdings
    ("QQQ", "VTI"): 40,
    ("QQQ", "QQQM"): 99,  # Same index, different wrapper
    ("VUG", "QQQ"): 55,
    ("VUG", "VTI"): 75,  # Growth is subset of total market
    ("VUG", "VOO"): 80,  # Growth overlaps heavily with S&P 500
    ("IWF", "VUG"): 90,
    ("MGK", "QQQ"): 70,  # Mega cap growth overlaps with Nasdaq
    ("MGK", "VUG"): 85,
    ("SCHG", "VUG"): 90,
    ("SCHG", "QQQ"): 55,

    # ============================================
    # Value ETFs
    # ============================================
    ("VTV", "VTI"): 45,  # Value is part of total market
    ("VTV", "VOO"): 50,
    ("VTV", "IWD"): 90,
    ("VTV", "SCHV"): 90,
    ("IWD", "SCHV"): 85,

    # ============================================
    # International funds overlap
    # ============================================
    ("VXUS", "VEA"): 75,  # VXUS includes EM, VEA is developed only
    ("VXUS", "VTIAX"): 99,
    ("VXUS", "IXUS"): 95,
    ("VEA", "IEFA"): 90,
    ("VEA", "EFA"): 85,
    ("VEA", "SCHF"): 90,
    ("IEFA", "EFA"): 90,
    ("IEFA", "SCHF"): 85,

    # ============================================
    # Emerging markets
    # ============================================
    ("VWO", "IEMG"): 90,
    ("VWO", "EEM"): 85,
    ("VWO", "SCHE"): 90,
    ("IEMG", "EEM"): 85,
    ("IEMG", "SCHE"): 85,

    # ============================================
    # Bond funds
    # ============================================
    ("BND", "VBTLX"): 99,
    ("BND", "AGG"): 95,
    ("BND", "SCHZ"): 95,
    ("AGG", "SCHZ"): 95,
    ("AGG", "VBTLX"): 95,

    # ============================================
    # Dividend ETFs overlap with value and broad market
    # ============================================
    ("SCHD", "VYM"): 50,
    ("SCHD", "VIG"): 45,
    ("SCHD", "VOO"): 35,
    ("VIG", "VYM"): 40,
    ("VIG", "VOO"): 55,
    ("VYM", "VTV"): 60,
    ("DGRO", "VIG"): 65,
    ("DGRO", "SCHD"): 40,

    # ============================================
    # REITs
    # ============================================
    ("VNQ", "VGSLX"): 99,
    ("VNQ", "IYR"): 85,
    ("VNQ", "SCHH"): 90,
    ("IYR", "SCHH"): 80,

    # ============================================
    # Tech sector vs growth vs QQQ
    # ============================================
    ("VGT", "XLK"): 85,
    ("VGT", "QQQ"): 65,
    ("VGT", "VOO"): 30,  # Tech is ~28% of S&P 500
    ("XLK", "QQQ"): 60,
    ("SMH", "VGT"): 30,  # Semiconductors are subset of tech
    ("SMH", "QQQ"): 25,

    # ============================================
    # Similar individual stocks (common pairs people hold)
    # ============================================
    ("GOOGL", "GOOG"): 100,  # Same company, different share classes

    # ============================================
    # Gold ETFs
    # ============================================
    ("GLD", "IAU"): 99,  # Both hold physical gold
}


# Overlap warning thresholds
OVERLAP_THRESHOLDS = {
    "high": 80,      # Very high overlap - essentially the same
    "moderate": 50,  # Significant overlap - consider consolidating
    "low": 30,       # Some overlap - acceptable in most portfolios
}


class OverlapDetector:
    """Detects holding overlaps in a portfolio."""

    def __init__(self):
        self.overlaps = KNOWN_OVERLAPS
        # Build reverse lookup for efficiency
        self._overlap_lookup: Dict[str, Set[str]] = {}
        for (t1, t2) in self.overlaps.keys():
            self._overlap_lookup.setdefault(t1, set()).add(t2)
            self._overlap_lookup.setdefault(t2, set()).add(t1)

    def get_overlap(self, ticker1: str, ticker2: str) -> Optional[int]:
        """
        Get the overlap percentage between two tickers.

        Returns None if overlap is unknown.
        """
        t1, t2 = ticker1.upper(), ticker2.upper()
        if t1 == t2:
            return 100

        # Check both orderings
        overlap = self.overlaps.get((t1, t2))
        if overlap is not None:
            return overlap

        overlap = self.overlaps.get((t2, t1))
        return overlap

    def find_overlapping_pairs(
        self,
        tickers: List[str],
        min_overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find all pairs of tickers with significant overlap.

        Args:
            tickers: List of tickers in the portfolio
            min_overlap: Minimum overlap percentage to report

        Returns:
            List of overlap info dicts, sorted by overlap percentage (highest first)
        """
        tickers = [t.upper() for t in tickers]
        overlaps = []

        # Check all pairs
        for i, t1 in enumerate(tickers):
            for t2 in tickers[i + 1:]:
                overlap = self.get_overlap(t1, t2)
                if overlap and overlap >= min_overlap:
                    overlaps.append({
                        "ticker1": t1,
                        "ticker2": t2,
                        "overlap_percent": overlap,
                        "severity": self._get_severity(overlap),
                    })

        # Sort by overlap percentage descending
        overlaps.sort(key=lambda x: x["overlap_percent"], reverse=True)
        return overlaps

    def _get_severity(self, overlap: int) -> str:
        """Get severity level for an overlap percentage."""
        if overlap >= OVERLAP_THRESHOLDS["high"]:
            return "high"
        elif overlap >= OVERLAP_THRESHOLDS["moderate"]:
            return "moderate"
        else:
            return "low"

    def get_overlap_warnings(
        self,
        holdings: List[Dict[str, Any]],
        min_overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Generate overlap warnings for a list of holdings.

        Args:
            holdings: List of holding dicts with 'ticker' and 'value' keys
            min_overlap: Minimum overlap to warn about

        Returns:
            List of warning dicts with context for AI recommendations
        """
        tickers = [h.get("ticker", "").upper() for h in holdings if h.get("ticker")]
        ticker_values = {
            h.get("ticker", "").upper(): h.get("value", 0)
            for h in holdings if h.get("ticker")
        }

        overlaps = self.find_overlapping_pairs(tickers, min_overlap)
        warnings = []

        for overlap in overlaps:
            t1, t2 = overlap["ticker1"], overlap["ticker2"]
            v1, v2 = ticker_values.get(t1, 0), ticker_values.get(t2, 0)
            combined = v1 + v2
            overlap_pct = overlap["overlap_percent"]

            # Calculate "effective" exposure
            effective_overlap_value = min(v1, v2) * (overlap_pct / 100)

            warning = {
                **overlap,
                "value1": v1,
                "value2": v2,
                "combined_value": combined,
                "effective_overlap_value": effective_overlap_value,
                "recommendation": self._generate_recommendation(
                    t1, t2, v1, v2, overlap_pct
                ),
            }
            warnings.append(warning)

        return warnings

    def _generate_recommendation(
        self,
        ticker1: str,
        ticker2: str,
        value1: float,
        value2: float,
        overlap_pct: int
    ) -> str:
        """Generate a specific recommendation for overlapping funds."""
        smaller = ticker1 if value1 <= value2 else ticker2
        larger = ticker2 if value1 <= value2 else ticker1
        smaller_val = min(value1, value2)

        if overlap_pct >= 95:
            return (
                f"Consider consolidating into {larger} only. "
                f"These funds hold nearly identical securities."
            )
        elif overlap_pct >= 80:
            return (
                f"Consider selling {smaller} (${smaller_val:,.0f}) and adding to {larger}. "
                f"High overlap ({overlap_pct}%) means limited additional diversification."
            )
        elif overlap_pct >= 50:
            return (
                f"Note: {ticker1} and {ticker2} have {overlap_pct}% overlap. "
                f"Combined exposure is higher than it appears."
            )
        else:
            return (
                f"Minor overlap ({overlap_pct}%) between {ticker1} and {ticker2}. "
                f"Generally acceptable."
            )


# Module-level convenience functions
_detector = OverlapDetector()


def get_overlap_warnings(
    holdings: List[Dict[str, Any]],
    min_overlap: int = 50
) -> List[Dict[str, Any]]:
    """Get overlap warnings for a list of holdings."""
    return _detector.get_overlap_warnings(holdings, min_overlap)


def get_overlap(ticker1: str, ticker2: str) -> Optional[int]:
    """Get overlap percentage between two tickers."""
    return _detector.get_overlap(ticker1, ticker2)


def find_overlapping_pairs(
    tickers: List[str],
    min_overlap: int = 50
) -> List[Dict[str, Any]]:
    """Find overlapping pairs in a list of tickers."""
    return _detector.find_overlapping_pairs(tickers, min_overlap)

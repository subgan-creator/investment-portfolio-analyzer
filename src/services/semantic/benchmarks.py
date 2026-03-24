"""
Benchmark Comparisons - Compare portfolio allocation against standard targets.

Provides:
- Age-based allocation recommendations (100 - age = stocks)
- Standard 60/40 portfolio comparison
- Missing asset class detection
- Sector weight comparison to S&P 500
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .fund_knowledge import AssetClass, FundKnowledgeBase


# S&P 500 approximate sector weights (updated periodically)
SP500_SECTOR_WEIGHTS = {
    "Technology": 30,
    "Healthcare": 12,
    "Financials": 13,
    "Consumer Discretionary": 10,
    "Communication Services": 9,
    "Industrials": 8,
    "Consumer Staples": 6,
    "Energy": 4,
    "Utilities": 2,
    "Real Estate": 2,
    "Materials": 2,
}


# Standard target allocations by investment profile
TARGET_ALLOCATIONS = {
    "aggressive": {
        "stocks": 90,
        "bonds": 10,
        "description": "Aggressive growth - high risk tolerance, long time horizon",
    },
    "growth": {
        "stocks": 80,
        "bonds": 20,
        "description": "Growth-oriented - moderate-high risk tolerance",
    },
    "balanced": {
        "stocks": 60,
        "bonds": 40,
        "description": "Balanced - moderate risk tolerance, classic 60/40",
    },
    "moderate": {
        "stocks": 50,
        "bonds": 50,
        "description": "Moderate - approaching retirement or conservative",
    },
    "conservative": {
        "stocks": 30,
        "bonds": 70,
        "description": "Conservative - low risk tolerance, capital preservation",
    },
}


# Recommended international allocation (as % of stocks)
RECOMMENDED_INTL_ALLOCATION = {
    "min": 20,
    "target": 30,
    "max": 40,
    "rationale": "International diversification reduces country-specific risk",
}


# Recommended asset class ranges
ASSET_CLASS_TARGETS = {
    AssetClass.US_EQUITY: {"min": 40, "max": 70, "typical": 55},
    AssetClass.INTL_EQUITY: {"min": 15, "max": 35, "typical": 25},
    AssetClass.EMERGING_MARKETS: {"min": 0, "max": 15, "typical": 8},
    AssetClass.FIXED_INCOME: {"min": 10, "max": 50, "typical": 25},
    AssetClass.REAL_ESTATE: {"min": 0, "max": 15, "typical": 5},
    AssetClass.COMMODITIES: {"min": 0, "max": 10, "typical": 0},
    AssetClass.CASH: {"min": 0, "max": 10, "typical": 2},
}


@dataclass
class AllocationAnalysis:
    """Results of portfolio allocation analysis."""
    stock_percent: float
    bond_percent: float
    other_percent: float
    intl_percent: float  # As % of total portfolio
    intl_of_stocks: float  # International as % of stock allocation
    missing_asset_classes: List[str]
    overweight_areas: List[Dict[str, Any]]
    underweight_areas: List[Dict[str, Any]]
    profile_match: str
    recommendations: List[str]


class BenchmarkComparator:
    """Compares portfolio allocation against benchmarks and targets."""

    def __init__(self):
        self.fund_kb = FundKnowledgeBase()

    def calculate_age_based_target(self, age: int) -> Dict[str, int]:
        """
        Calculate target allocation based on age.

        Uses the "100 - age" rule for stock allocation.
        More conservative "110 - age" or aggressive "120 - age" can be options.
        """
        # Standard: 100 - age = stock allocation
        stock_pct = max(20, min(90, 100 - age))
        bond_pct = 100 - stock_pct

        return {
            "stocks": stock_pct,
            "bonds": bond_pct,
            "age": age,
            "rule": "100 - age",
            "description": f"At age {age}, consider ~{stock_pct}% stocks and ~{bond_pct}% bonds",
        }

    def analyze_allocation(
        self,
        holdings: List[Dict[str, Any]],
        age: Optional[int] = None
    ) -> AllocationAnalysis:
        """
        Analyze portfolio allocation against benchmarks.

        Args:
            holdings: List of holdings with 'ticker', 'value', and optionally 'description'
            age: Optional age for age-based recommendations

        Returns:
            AllocationAnalysis with detailed breakdown and recommendations
        """
        total_value = sum(h.get("value", 0) for h in holdings)
        if total_value == 0:
            return AllocationAnalysis(
                stock_percent=0,
                bond_percent=0,
                other_percent=0,
                intl_percent=0,
                intl_of_stocks=0,
                missing_asset_classes=[],
                overweight_areas=[],
                underweight_areas=[],
                profile_match="unknown",
                recommendations=["Upload portfolio data to analyze allocation"],
            )

        # Categorize holdings by asset class
        asset_class_values: Dict[str, float] = {}
        for h in holdings:
            ticker = h.get("ticker", "").upper()
            value = h.get("value", 0)
            description = h.get("description", "")

            # Get fund info and asset class
            enriched = self.fund_kb.enrich_holding(ticker, description)
            asset_class = enriched.get("asset_class", AssetClass.US_EQUITY)

            asset_class_values[asset_class] = asset_class_values.get(asset_class, 0) + value

        # Calculate percentages
        def pct(value: float) -> float:
            return (value / total_value * 100) if total_value > 0 else 0

        us_equity = pct(asset_class_values.get(AssetClass.US_EQUITY, 0))
        intl_equity = pct(asset_class_values.get(AssetClass.INTL_EQUITY, 0))
        emerging = pct(asset_class_values.get(AssetClass.EMERGING_MARKETS, 0))
        fixed_income = pct(asset_class_values.get(AssetClass.FIXED_INCOME, 0))
        real_estate = pct(asset_class_values.get(AssetClass.REAL_ESTATE, 0))
        commodities = pct(asset_class_values.get(AssetClass.COMMODITIES, 0))
        cash = pct(asset_class_values.get(AssetClass.CASH, 0))
        crypto = pct(asset_class_values.get(AssetClass.CRYPTO, 0))
        alternatives = pct(asset_class_values.get(AssetClass.ALTERNATIVES, 0))

        # Calculate aggregate categories
        total_stocks = us_equity + intl_equity + emerging
        total_bonds = fixed_income
        total_other = real_estate + commodities + cash + crypto + alternatives

        # International as % of stocks
        intl_of_stocks = ((intl_equity + emerging) / total_stocks * 100) if total_stocks > 0 else 0

        # Find missing asset classes
        missing = []
        if intl_equity + emerging < 5:
            missing.append("International Equities")
        if fixed_income < 5 and total_stocks > 50:
            missing.append("Bonds/Fixed Income")
        if real_estate < 1:
            missing.append("Real Estate (REITs)")

        # Find overweight/underweight areas
        overweight = []
        underweight = []

        # Check against targets
        if us_equity > 75:
            overweight.append({
                "area": "US Equities",
                "current": us_equity,
                "target_max": 70,
                "difference": us_equity - 70,
            })

        if intl_of_stocks < 15 and total_stocks > 30:
            underweight.append({
                "area": "International (% of stocks)",
                "current": intl_of_stocks,
                "target_min": 20,
                "difference": 20 - intl_of_stocks,
            })

        if crypto > 10:
            overweight.append({
                "area": "Cryptocurrency",
                "current": crypto,
                "target_max": 5,
                "difference": crypto - 5,
            })

        # Determine profile match
        profile_match = "balanced"
        if total_stocks >= 85:
            profile_match = "aggressive"
        elif total_stocks >= 75:
            profile_match = "growth"
        elif total_stocks >= 55:
            profile_match = "balanced"
        elif total_stocks >= 40:
            profile_match = "moderate"
        else:
            profile_match = "conservative"

        # Generate recommendations
        recommendations = []

        # Age-based recommendation
        if age:
            target = self.calculate_age_based_target(age)
            target_stocks = target["stocks"]
            diff = total_stocks - target_stocks

            if abs(diff) > 15:
                if diff > 0:
                    recommendations.append(
                        f"Age {age} suggests ~{target_stocks}% stocks. "
                        f"You're at {total_stocks:.0f}% (more aggressive). "
                        f"Consider if this matches your risk tolerance."
                    )
                else:
                    recommendations.append(
                        f"Age {age} suggests ~{target_stocks}% stocks. "
                        f"You're at {total_stocks:.0f}% (more conservative). "
                        f"You may have room for more growth if desired."
                    )

        # International diversification
        if intl_of_stocks < 15 and total_stocks > 30:
            recommendations.append(
                f"International exposure is {intl_of_stocks:.0f}% of stocks. "
                f"Consider adding VXUS or IXUS for global diversification (target: 20-30%)."
            )

        # Missing bonds
        if fixed_income < 10 and total_stocks > 70:
            recommendations.append(
                f"Bond allocation is only {fixed_income:.0f}%. "
                f"Consider adding BND or AGG for portfolio stability."
            )

        # Missing REITs
        if real_estate < 1:
            recommendations.append(
                "No REIT exposure. Consider adding VNQ for real estate diversification (5-10% typical)."
            )

        # High concentration in one area
        if us_equity > 80:
            recommendations.append(
                f"US equities are {us_equity:.0f}% of portfolio. "
                f"Consider diversifying internationally to reduce country-specific risk."
            )

        return AllocationAnalysis(
            stock_percent=total_stocks,
            bond_percent=total_bonds,
            other_percent=total_other,
            intl_percent=intl_equity + emerging,
            intl_of_stocks=intl_of_stocks,
            missing_asset_classes=missing,
            overweight_areas=overweight,
            underweight_areas=underweight,
            profile_match=profile_match,
            recommendations=recommendations,
        )

    def compare_to_60_40(self, stock_percent: float, bond_percent: float) -> Dict[str, Any]:
        """Compare allocation to classic 60/40 portfolio."""
        return {
            "target_stocks": 60,
            "target_bonds": 40,
            "actual_stocks": stock_percent,
            "actual_bonds": bond_percent,
            "stock_difference": stock_percent - 60,
            "bond_difference": bond_percent - 40,
            "assessment": self._assess_60_40_deviation(stock_percent, bond_percent),
        }

    def _assess_60_40_deviation(self, stocks: float, bonds: float) -> str:
        """Assess how far portfolio deviates from 60/40."""
        if stocks >= 85:
            return "Very aggressive - significantly more equity-heavy than 60/40"
        elif stocks >= 70:
            return "Growth-oriented - moderately above typical 60/40 allocation"
        elif stocks >= 55:
            return "Close to 60/40 balanced allocation"
        elif stocks >= 40:
            return "Moderate - more conservative than 60/40"
        else:
            return "Conservative - significantly less equity exposure than 60/40"

    def get_rebalancing_suggestions(
        self,
        analysis: AllocationAnalysis,
        total_value: float
    ) -> List[Dict[str, Any]]:
        """
        Generate specific rebalancing suggestions with dollar amounts.

        Args:
            analysis: AllocationAnalysis from analyze_allocation
            total_value: Total portfolio value

        Returns:
            List of specific rebalancing actions
        """
        suggestions = []

        # Suggest adding international if underweight
        if analysis.intl_of_stocks < 20 and analysis.stock_percent > 30:
            target_intl_pct = 25  # Target 25% of stocks as international
            current_intl_value = (analysis.intl_percent / 100) * total_value
            target_intl_value = (analysis.stock_percent / 100) * total_value * (target_intl_pct / 100)
            add_amount = target_intl_value - current_intl_value

            if add_amount > 1000:
                suggestions.append({
                    "action": "add",
                    "asset_class": "International Equities",
                    "amount": add_amount,
                    "ticker_suggestion": "VXUS",
                    "reason": f"Increase international from {analysis.intl_of_stocks:.0f}% to {target_intl_pct}% of stocks",
                })

        # Suggest adding bonds if underweight (based on 60/40 as reasonable default)
        if analysis.bond_percent < 20 and analysis.stock_percent > 70:
            target_bond_pct = 25
            current_bond_value = (analysis.bond_percent / 100) * total_value
            target_bond_value = (target_bond_pct / 100) * total_value
            add_amount = target_bond_value - current_bond_value

            if add_amount > 1000:
                suggestions.append({
                    "action": "add",
                    "asset_class": "Fixed Income",
                    "amount": add_amount,
                    "ticker_suggestion": "BND",
                    "reason": f"Increase bonds from {analysis.bond_percent:.0f}% to {target_bond_pct}%",
                })

        return suggestions


# Module-level convenience functions
_comparator = BenchmarkComparator()


def get_allocation_analysis(
    holdings: List[Dict[str, Any]],
    age: Optional[int] = None
) -> AllocationAnalysis:
    """Analyze portfolio allocation against benchmarks."""
    return _comparator.analyze_allocation(holdings, age)


def get_age_based_target(age: int) -> Dict[str, int]:
    """Get target allocation for a given age."""
    return _comparator.calculate_age_based_target(age)


def compare_to_60_40(stock_percent: float, bond_percent: float) -> Dict[str, Any]:
    """Compare allocation to 60/40 portfolio."""
    return _comparator.compare_to_60_40(stock_percent, bond_percent)

"""
Semantic Context Builder - Assembles enriched context for AI advisor.

This is the main entry point for the semantic layer. It combines:
- Fund knowledge (what each holding is)
- Overlap detection (redundant holdings)
- Benchmark comparisons (how allocation compares to targets)
- Actionable insights (specific recommendations)

The output is structured text that enhances AI recommendations.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .fund_knowledge import FundKnowledgeBase, AssetClass
from .overlaps import OverlapDetector, get_overlap_warnings
from .benchmarks import BenchmarkComparator, AllocationAnalysis


@dataclass
class SemanticContext:
    """Container for all semantic context."""
    enriched_holdings: List[Dict[str, Any]]
    overlap_warnings: List[Dict[str, Any]]
    allocation_analysis: AllocationAnalysis
    key_insights: List[str]
    formatted_context: str


class SemanticContextBuilder:
    """Builds enriched semantic context for AI advisor."""

    def __init__(self):
        self.fund_kb = FundKnowledgeBase()
        self.overlap_detector = OverlapDetector()
        self.benchmark_comparator = BenchmarkComparator()

    def build_context(
        self,
        portfolio_data: Dict[str, Any],
        user_age: Optional[int] = None
    ) -> SemanticContext:
        """
        Build complete semantic context from portfolio data.

        Args:
            portfolio_data: The portfolio analysis data dict
            user_age: Optional user age for age-based recommendations

        Returns:
            SemanticContext with all enriched data and formatted text
        """
        # Extract holdings from portfolio data
        holdings = self._extract_holdings(portfolio_data)

        # Enrich each holding with semantic information
        enriched_holdings = self._enrich_holdings(holdings)

        # Detect overlaps
        overlap_warnings = get_overlap_warnings(holdings, min_overlap=50)

        # Analyze allocation
        allocation_analysis = self.benchmark_comparator.analyze_allocation(
            holdings, age=user_age
        )

        # Generate key insights
        key_insights = self._generate_key_insights(
            enriched_holdings, overlap_warnings, allocation_analysis, portfolio_data
        )

        # Format everything into context text
        formatted_context = self._format_context(
            enriched_holdings, overlap_warnings, allocation_analysis, key_insights, portfolio_data
        )

        return SemanticContext(
            enriched_holdings=enriched_holdings,
            overlap_warnings=overlap_warnings,
            allocation_analysis=allocation_analysis,
            key_insights=key_insights,
            formatted_context=formatted_context,
        )

    def _extract_holdings(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract holdings list from portfolio data."""
        holdings = []

        # Try to get from top_holdings
        top_holdings = portfolio_data.get("top_holdings", [])
        for h in top_holdings:
            holdings.append({
                "ticker": h.get("ticker", ""),
                "name": h.get("name", ""),
                "value": h.get("value", 0),
                "percent": h.get("percent", 0),
                "gain_loss": h.get("gain_loss", 0),
                "description": h.get("name", ""),
            })

        return holdings

    def _enrich_holdings(self, holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich each holding with semantic information."""
        enriched = []

        for h in holdings:
            ticker = h.get("ticker", "").upper()
            description = h.get("description", h.get("name", ""))

            # Get semantic info
            fund_info = self.fund_kb.enrich_holding(ticker, description)

            enriched.append({
                **h,
                "semantic": fund_info,
            })

        return enriched

    def _get_look_through_allocation(self, portfolio_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract look-through allocation percentages from portfolio data.

        This is the TRUE allocation after expanding target date funds.
        """
        look_through = portfolio_data.get("look_through", {})
        if not look_through.get("available"):
            return {}

        allocation = {}
        for item in look_through.get("allocation", []):
            # Normalize name to lowercase for consistent lookup
            name = item.get("name", "").lower().strip()
            percent = item.get("percent", 0)
            allocation[name] = percent

        return allocation

    def _generate_key_insights(
        self,
        enriched_holdings: List[Dict[str, Any]],
        overlap_warnings: List[Dict[str, Any]],
        allocation: AllocationAnalysis,
        portfolio_data: Dict[str, Any]
    ) -> List[str]:
        """Generate the most important insights for the AI."""
        insights = []

        # Get look-through allocation if available (more accurate)
        look_through = self._get_look_through_allocation(portfolio_data)

        # High-impact overlap warnings
        high_overlaps = [o for o in overlap_warnings if o["overlap_percent"] >= 80]
        if high_overlaps:
            for overlap in high_overlaps[:2]:  # Top 2
                insights.append(
                    f"OVERLAP: {overlap['ticker1']} and {overlap['ticker2']} have "
                    f"{overlap['overlap_percent']}% overlap - consider consolidating"
                )

        # Check for missing asset classes using look-through data if available
        if look_through:
            # Calculate true international exposure
            intl_pct = look_through.get("international developed", 0) + look_through.get("emerging markets", 0)
            bond_pct = look_through.get("core bonds", 0) + look_through.get("high yield bonds", 0) + look_through.get("em bonds", 0)
            reit_pct = look_through.get("real estate", 0)

            # Only flag missing if truly missing after look-through
            if intl_pct < 5:
                insights.append(f"ALLOCATION: International exposure is only {intl_pct:.1f}% (target: 15-30%) - consider adding VXUS")
            elif intl_pct < 15:
                insights.append(f"ALLOCATION: International exposure is {intl_pct:.1f}% (below typical 15-30%) - may want to increase")
            if bond_pct < 5 and allocation.stock_percent > 50:
                insights.append(f"ALLOCATION: Bond exposure is {bond_pct:.1f}% - may need more for stability")
            if reit_pct < 0.5:
                insights.append("MISSING: No significant Real Estate (REIT) exposure - consider VNQ (target: 5-10%)")
            elif reit_pct < 3:
                insights.append(f"ALLOCATION: Real Estate is only {reit_pct:.1f}% (below typical 5-10%)")
        else:
            # Fall back to basic allocation analysis (no look-through data)
            for missing in allocation.missing_asset_classes:
                insights.append(f"MISSING: No {missing} exposure - consider adding for diversification")

            # Only use basic allocation recommendations when no look-through
            for rec in allocation.recommendations[:3]:  # Top 3 recommendations
                insights.append(f"ALLOCATION: {rec}")

        # Individual stock concentration
        for h in enriched_holdings:
            semantic = h.get("semantic", {})
            if not semantic.get("diversified", True) and h.get("percent", 0) > 10:
                ticker = h.get("ticker", "")
                pct = h.get("percent", 0)
                insights.append(
                    f"CONCENTRATION: {ticker} is {pct:.1f}% of portfolio "
                    f"(individual stock > 10% is high risk)"
                )

        # High expense ratios
        for h in enriched_holdings:
            semantic = h.get("semantic", {})
            expense = semantic.get("expense_ratio", 0)
            if expense and expense > 0.50:
                ticker = h.get("ticker", "")
                similar = self.fund_kb.get_similar_funds(ticker, limit=1)
                if similar:
                    insights.append(
                        f"COST: {ticker} has {expense:.2f}% expense ratio - "
                        f"consider lower-cost alternative like {similar[0]}"
                    )

        return insights

    def _format_context(
        self,
        enriched_holdings: List[Dict[str, Any]],
        overlap_warnings: List[Dict[str, Any]],
        allocation: AllocationAnalysis,
        key_insights: List[str],
        portfolio_data: Dict[str, Any]
    ) -> str:
        """Format all semantic data into context text for AI."""
        sections = []

        # Header
        sections.append("=== SEMANTIC PORTFOLIO INTELLIGENCE ===\n")

        # Key insights (most important - AI should prioritize these)
        if key_insights:
            sections.append("## PRIORITY INSIGHTS (Address These First):\n")
            for i, insight in enumerate(key_insights, 1):
                sections.append(f"{i}. {insight}")
            sections.append("")

        # Overlap analysis
        if overlap_warnings:
            sections.append("## HOLDING OVERLAPS:\n")
            for overlap in overlap_warnings[:5]:  # Top 5
                sections.append(
                    f"- {overlap['ticker1']} + {overlap['ticker2']}: "
                    f"{overlap['overlap_percent']}% overlap "
                    f"(${overlap['combined_value']:,.0f} combined)"
                )
                sections.append(f"  → {overlap['recommendation']}")
            sections.append("")

        # Allocation analysis - use look-through if available for accuracy
        look_through = self._get_look_through_allocation(portfolio_data)

        sections.append("## ALLOCATION ANALYSIS:\n")
        sections.append(f"- Portfolio Style: {allocation.profile_match.upper()}")

        if look_through:
            # Use TRUE allocation from look-through analysis
            sections.append("(Based on look-through analysis - target date funds expanded)")
            intl_pct = look_through.get("international developed", 0) + look_through.get("emerging markets", 0)
            bond_pct = look_through.get("core bonds", 0) + look_through.get("high yield bonds", 0) + look_through.get("em bonds", 0) + look_through.get("inflation protected", 0)
            reit_pct = look_through.get("real estate", 0)
            cash_pct = look_through.get("cash", 0)
            stock_pct = look_through.get("stock", 0) + look_through.get("us large cap", 0) + look_through.get("us mid cap", 0) + look_through.get("us small cap", 0) + intl_pct

            sections.append(f"- TRUE Stock Exposure: {stock_pct:.1f}%")
            sections.append(f"- TRUE Bond Exposure: {bond_pct:.1f}%")
            sections.append(f"- TRUE International: {intl_pct:.1f}%")
            sections.append(f"- Cash: {cash_pct:.1f}%")
            sections.append(f"- Real Estate: {reit_pct:.1f}%")
        else:
            sections.append(f"- Stocks: {allocation.stock_percent:.1f}%")
            sections.append(f"- Bonds: {allocation.bond_percent:.1f}%")
            sections.append(f"- Other: {allocation.other_percent:.1f}%")
            sections.append(f"- International (of stocks): {allocation.intl_of_stocks:.1f}%")
        sections.append("")

        # Missing asset classes - only if NOT using look-through (look-through insights are in key_insights)
        if not look_through and allocation.missing_asset_classes:
            sections.append("## MISSING ASSET CLASSES:\n")
            for missing in allocation.missing_asset_classes:
                if missing == "International Equities":
                    sections.append(f"- {missing} → Consider: VXUS, IXUS, or VEA")
                elif missing == "Bonds/Fixed Income":
                    sections.append(f"- {missing} → Consider: BND, AGG, or SCHZ")
                elif missing == "Real Estate (REITs)":
                    sections.append(f"- {missing} → Consider: VNQ or SCHH")
                else:
                    sections.append(f"- {missing}")
            sections.append("")

        # Enriched holding details (top holdings with context)
        sections.append("## TOP HOLDINGS WITH CONTEXT:\n")
        for h in enriched_holdings[:10]:
            ticker = h.get("ticker", "")
            value = h.get("value", 0)
            pct = h.get("percent", 0)
            semantic = h.get("semantic", {})

            name = semantic.get("name", h.get("name", ticker))
            asset_class = semantic.get("asset_class", "Unknown")
            diversified = semantic.get("diversified", False)
            holdings_count = semantic.get("holdings", 0)
            expense = semantic.get("expense_ratio", 0)

            # Build holding line
            line = f"- {ticker}: ${value:,.0f} ({pct:.1f}%)"
            if semantic.get("known", False):
                line += f" | {asset_class}"
                if holdings_count and holdings_count > 1:
                    line += f" | {holdings_count} holdings"
                if expense:
                    line += f" | {expense:.2f}% ER"
                if not diversified:
                    line += " | SINGLE STOCK"
            sections.append(line)
        sections.append("")

        # Final recommendations summary
        if allocation.recommendations:
            sections.append("## RECOMMENDED ACTIONS:\n")
            for i, rec in enumerate(allocation.recommendations, 1):
                sections.append(f"{i}. {rec}")
            sections.append("")

        sections.append("=== END SEMANTIC INTELLIGENCE ===\n")
        sections.append(
            "Use the above semantic context to provide specific, actionable advice. "
            "Reference the priority insights first."
        )

        return "\n".join(sections)


# Module-level convenience function
_builder = SemanticContextBuilder()


def build_semantic_context(
    portfolio_data: Dict[str, Any],
    user_age: Optional[int] = None
) -> SemanticContext:
    """Build semantic context from portfolio data."""
    return _builder.build_context(portfolio_data, user_age)


def get_formatted_context(
    portfolio_data: Dict[str, Any],
    user_age: Optional[int] = None
) -> str:
    """Get just the formatted context string for AI prompt."""
    context = _builder.build_context(portfolio_data, user_age)
    return context.formatted_context

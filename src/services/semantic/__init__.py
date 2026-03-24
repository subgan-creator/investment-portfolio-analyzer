"""
Semantic Layer for Investment Portfolio Analyzer.

Provides enriched context for AI advisor recommendations by transforming
raw portfolio data into meaningful, actionable insights.
"""

from .fund_knowledge import FundKnowledgeBase, get_fund_info
from .overlaps import OverlapDetector, get_overlap_warnings
from .benchmarks import BenchmarkComparator, get_allocation_analysis
from .context_builder import SemanticContextBuilder, build_semantic_context

__all__ = [
    'FundKnowledgeBase',
    'get_fund_info',
    'OverlapDetector',
    'get_overlap_warnings',
    'BenchmarkComparator',
    'get_allocation_analysis',
    'SemanticContextBuilder',
    'build_semantic_context',
]

"""
AI-Powered Investment Advisor using Anthropic Claude.

Provides personalized portfolio insights through natural language conversation.
"""
import os
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import rebalancing calculator
try:
    from src.services.rebalancing import RebalancingCalculator
except ImportError:
    from services.rebalancing import RebalancingCalculator

# Import semantic layer
try:
    from src.services.semantic import build_semantic_context
except ImportError:
    try:
        from services.semantic import build_semantic_context
    except ImportError:
        build_semantic_context = None


class AIAdvisor:
    """AI investment advisor that provides portfolio insights using Claude."""

    def __init__(self, portfolio_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI advisor.

        Args:
            portfolio_data: Dictionary containing portfolio analysis data
        """
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
        self.portfolio_data = portfolio_data or {}

    def build_system_prompt(self) -> str:
        """Build the system prompt with portfolio context."""
        base_prompt = """You are an expert investment advisor with COMPLETE ACCESS to the user's portfolio data.
You can see ALL their holdings, account values, allocations, and analysis scores - no need to ask for this information.

CRITICAL: You already have their complete portfolio data below. When they ask questions like "where should I invest $5k?",
USE THE DATA YOU HAVE to give specific recommendations. Do NOT ask them for information you already have.

IMPORTANT GUIDELINES:
- ALWAYS reference their actual holdings by name when giving advice (e.g., "Since you already have 15% in VTI...")
- Give SPECIFIC recommendations with ticker symbols and dollar amounts
- Compare new investments against their CURRENT allocation to avoid overlap
- Identify gaps in their portfolio that new money could fill
- Consider tax implications based on their account types
- Be conversational but professional
- Keep responses concise but informative (2-4 paragraphs max)
- Recommend clear next steps with specific actions
- If they ask where to invest new money, suggest specific ETFs/funds based on what they're MISSING
- Never provide specific buy/sell timing recommendations
- Always remind users to consult a financial advisor for major decisions

CRITICAL - LOOK-THROUGH ANALYSIS:
- When "LOOK-THROUGH" allocation data is available, USE IT for all allocation calculations
- Target date funds contain stocks, bonds, and international exposure INSIDE them
- The look-through data shows the TRUE allocation after expanding these funds
- Do NOT say "zero international" if look-through shows international exposure exists
- Example: If top holdings show TARGETDAT 22%, but look-through shows 6.7% international - the user HAS 6.7% international

DISCLAIMER: This is educational information, not personalized financial advice."""

        if not self.portfolio_data:
            return base_prompt + "\n\nNote: No portfolio data is currently loaded. Ask the user to upload their portfolio first."

        # Extract portfolio details
        portfolio = self.portfolio_data.get('portfolio', {})
        diversification = self.portfolio_data.get('diversification', {})
        concentration = self.portfolio_data.get('concentration', {})
        tax = self.portfolio_data.get('tax', {})
        top_holdings = self.portfolio_data.get('top_holdings', [])
        asset_allocation = self.portfolio_data.get('asset_allocation', [])
        sector_allocation = self.portfolio_data.get('sector_allocation', [])
        category_allocation = self.portfolio_data.get('category_allocation', [])
        accounts = self.portfolio_data.get('accounts', [])
        source_breakdown = self.portfolio_data.get('source_breakdown', [])
        look_through = self.portfolio_data.get('look_through', {})

        # Build portfolio context
        context = f"""

=== COMPLETE PORTFOLIO DATA (USE THIS TO ANSWER QUESTIONS) ===

PORTFOLIO SUMMARY:
- Total Value: ${portfolio.get('total_value', 0):,.2f}
- Total Cost Basis: ${portfolio.get('total_cost_basis', 0):,.2f}
- Unrealized Gain/Loss: ${portfolio.get('unrealized_gain_loss', 0):,.2f} ({portfolio.get('return_percent', 0):.2f}% return)
- Number of Accounts: {portfolio.get('num_accounts', 0)}
- Number of Holdings: {portfolio.get('num_holdings', 0)}

ANALYSIS SCORES:
- Diversification Score: {diversification.get('score', 'N/A')}/100 ({diversification.get('rating', 'N/A')})
- Concentration Risk: {concentration.get('risk_level', 'N/A')}
- Top 10 Holdings Concentration: {concentration.get('top_10_concentration', 0):.1f}%
- Tax Efficiency Score: {tax.get('score', 'N/A')}/100 ({tax.get('rating', 'N/A')})
"""

        # Add LOOK-THROUGH allocation prominently if available
        # This is the TRUE allocation after expanding target date funds
        if look_through.get('available'):
            context += "\n*** CRITICAL: TRUE ASSET ALLOCATION (Look-Through Analysis) ***\n"
            context += "Target date funds have been expanded to show actual underlying exposure.\n"
            context += "USE THESE NUMBERS for allocation recommendations, not the surface-level holdings.\n\n"
            for item in look_through.get('allocation', []):
                name = item.get('name', 'Unknown')
                pct = item.get('percent', 0)
                value = item.get('value', 0)
                context += f"- {name}: {pct:.1f}% (${value:,.0f})\n"

            # Calculate key aggregates
            alloc_dict = {item.get('name', '').lower(): item.get('percent', 0) for item in look_through.get('allocation', [])}
            intl_pct = alloc_dict.get('international developed', 0) + alloc_dict.get('emerging markets', 0)
            bond_pct = alloc_dict.get('core bonds', 0) + alloc_dict.get('high yield bonds', 0) + alloc_dict.get('em bonds', 0) + alloc_dict.get('inflation protected', 0)

            context += f"\nKEY LOOK-THROUGH TOTALS:\n"
            context += f"- TRUE International Exposure: {intl_pct:.1f}%\n"
            context += f"- TRUE Bond Exposure: {bond_pct:.1f}%\n"
            context += "*** END LOOK-THROUGH DATA ***\n"

        # Add accounts breakdown
        if accounts:
            context += "\nACCOUNTS (by brokerage and tax status):\n"
            for acc in accounts:
                tax_status = acc.get('tax_status', 'unknown').replace('_', ' ').title()
                context += f"- {acc.get('name', 'N/A')} ({acc.get('source', 'Unknown')}): ${acc.get('value', 0):,.0f} - {tax_status}, {acc.get('num_holdings', 0)} holdings\n"

        # Add source breakdown
        if source_breakdown:
            context += "\nBROKERAGE BREAKDOWN:\n"
            for src in source_breakdown:
                context += f"- {src.get('name', 'N/A')}: ${src.get('value', 0):,.0f} ({src.get('percent', 0):.1f}%)\n"

        # Add category allocation (high-level)
        if category_allocation:
            context += "\nCATEGORY ALLOCATION (high-level):\n"
            for cat in category_allocation:
                context += f"- {cat.get('name', 'N/A')}: {cat.get('percent', 0):.1f}% (${cat.get('value', 0):,.0f})\n"

        # Add top holdings
        if top_holdings:
            context += "\nTOP 10 HOLDINGS (with gain/loss):\n"
            for h in top_holdings[:10]:
                gain_status = "+" if h.get('gain_loss', 0) >= 0 else ""
                context += f"- {h.get('ticker', 'N/A')} ({h.get('name', '')}): ${h.get('value', 0):,.0f} ({h.get('percent', 0):.1f}%), Gain/Loss: {gain_status}${h.get('gain_loss', 0):,.0f}\n"

        # Add asset allocation
        if asset_allocation:
            context += "\nASSET CLASS ALLOCATION:\n"
            for a in asset_allocation:
                context += f"- {a.get('name', 'N/A')}: {a.get('percent', 0):.1f}% (${a.get('value', 0):,.0f})\n"

        # Add detailed sector allocation
        if sector_allocation:
            context += "\nDETAILED SECTOR BREAKDOWN:\n"
            for s in sector_allocation[:15]:  # Show more sectors
                context += f"- {s.get('name', 'N/A')}: {s.get('percent', 0):.1f}% (${s.get('value', 0):,.0f})\n"

        # Add tax-loss harvesting opportunities if any
        harvesting_opps = tax.get('harvesting_opportunities', [])
        if harvesting_opps:
            context += "\nTAX-LOSS HARVESTING OPPORTUNITIES:\n"
            for opp in harvesting_opps[:5]:
                context += f"- {opp.get('ticker', 'N/A')}: Loss of ${abs(opp.get('unrealized_loss', 0)):,.0f}, Potential tax savings: ${opp.get('potential_tax_savings', 0):,.0f}\n"

        # Add concentrated positions if any
        concentrated = concentration.get('concentrated_positions', [])
        if concentrated:
            context += "\nCONCENTRATED POSITIONS (above threshold):\n"
            for pos in concentrated:
                context += f"- {pos.get('ticker', 'N/A')}: {pos.get('percentage', 0):.1f}% - Risk Level: {pos.get('risk_level', 'N/A')}\n"

        context += "\n=== END PORTFOLIO DATA ===\n"

        # Add semantic intelligence layer
        semantic_context = ""
        if build_semantic_context and self.portfolio_data:
            try:
                semantic = build_semantic_context(self.portfolio_data)
                semantic_context = "\n" + semantic.formatted_context
            except Exception as e:
                print(f"[AI Advisor] Semantic layer error (non-fatal): {e}")
                semantic_context = ""

        context += semantic_context
        context += "\nUse the above data and semantic intelligence to give specific, personalized recommendations. Do NOT ask the user for portfolio information - you already have it.\n"

        return base_prompt + context

    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Get AI response for the conversation.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys

        Returns:
            AI response string
        """
        try:
            # Validate messages - Anthropic requires at least one message
            if not messages:
                return "Please enter a message to get started."

            # Ensure messages have valid format
            valid_messages = []
            for msg in messages:
                if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
                    valid_messages.append({
                        'role': msg['role'],
                        'content': str(msg['content'])
                    })

            if not valid_messages:
                return "Please enter a message to get started."

            # Anthropic API requires system prompt as separate parameter
            # and messages should only contain user/assistant roles
            response = self.client.messages.create(
                model=self.model,
                system=self.build_system_prompt(),
                messages=valid_messages,
                max_tokens=1024,
            )

            # Handle empty response
            if not response.content:
                print(f"[AI Advisor] Empty response. Stop reason: {response.stop_reason}")
                return "I wasn't able to generate a response. Please try rephrasing your question."

            return response.content[0].text

        except Exception as e:
            error_msg = str(e)
            print(f"[AI Advisor] Error: {error_msg}")
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "I'm unable to connect to the AI service. Please check that your Anthropic API key is configured correctly in the .env file."
            elif "rate_limit" in error_msg.lower():
                return "I'm receiving too many requests right now. Please try again in a few moments."
            else:
                return f"I encountered an error processing your request. Please try again. (Error: {error_msg[:100]})"

    def get_quick_insight(self, topic: str) -> str:
        """
        Get a quick insight on a specific topic.

        Args:
            topic: The topic to get insight on (e.g., "diversification", "risk", "tax")

        Returns:
            Quick insight string
        """
        prompts = {
            "overview": "Give me a brief 2-3 sentence overview of my portfolio's health.",
            "diversification": "What's your assessment of my portfolio diversification in 2-3 sentences?",
            "risk": "What's my biggest portfolio risk right now in 2-3 sentences?",
            "tax": "Any quick tax optimization suggestions for my portfolio in 2-3 sentences?",
            "allocation": "How does my asset allocation look? Quick 2-3 sentence assessment.",
        }

        prompt = prompts.get(topic, prompts["overview"])
        return self.get_response([{"role": "user", "content": prompt}])

    def build_recommendations_system_prompt(self) -> str:
        """Build a directive system prompt for specific recommendations."""
        base_prompt = """You are a senior investment advisor conducting a portfolio review meeting.
Your job is to give SPECIFIC, ACTIONABLE recommendations with exact dollar amounts and ticker symbols.

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:
1. Give SPECIFIC ticker recommendations (e.g., "Buy $5,000 of VTI" not "consider diversifying")
2. Include EXACT dollar amounts for each recommendation
3. Explain WHY each recommendation improves the portfolio
4. Prioritize recommendations by impact (most important first)
5. Consider the investor's current holdings - don't recommend what they already own heavily
6. Use low-cost ETFs when suggesting new positions (Vanguard, Schwab, iShares)
7. Address concentration risks with specific reduction amounts
8. Consider tax implications (harvesting, location)

CRITICAL - LOOK-THROUGH ALLOCATION:
- When "LOOK-THROUGH" or "TRUE" allocation data is shown, USE THOSE NUMBERS
- Target date funds CONTAIN international stocks and bonds INSIDE them
- If look-through shows 6.7% international, DO NOT say "zero international exposure"
- The look-through data is the ACCURATE picture after expanding target date funds

OUTPUT FORMAT - Structure your response like this:

**Portfolio Assessment:**
[2-3 sentences on overall portfolio health]

**Priority Recommendations:**

1. **[Action] - [Ticker/Fund]** - $[Amount]
   - Why: [Specific reason based on their portfolio]
   - Impact: [How this improves diversification/risk/return]

2. **[Action] - [Ticker/Fund]** - $[Amount]
   - Why: [Specific reason]
   - Impact: [Expected improvement]

[Continue with 3-5 total recommendations]

**Tax Considerations:**
[Any tax-loss harvesting or account location suggestions]

**Next Steps:**
[Specific order of operations to implement these changes]

DISCLAIMER: Remind them this is educational guidance, not personalized financial advice."""

        if not self.portfolio_data:
            return base_prompt + "\n\nNote: No portfolio data available."

        # Get the full system prompt which includes look-through data
        full_prompt = self.build_system_prompt()

        # Extract portfolio data section (everything after the guidelines)
        if "=== COMPLETE PORTFOLIO DATA" in full_prompt:
            context = full_prompt.split("=== COMPLETE PORTFOLIO DATA")[1]
            context = "=== COMPLETE PORTFOLIO DATA" + context
        else:
            context = ""

        # Add rebalancing analysis
        try:
            calculator = RebalancingCalculator(self.portfolio_data)
            rebalancing_context = calculator.format_for_ai_context()
            context += "\n" + rebalancing_context
        except Exception:
            pass  # Continue without rebalancing context if it fails

        return base_prompt + "\n\n" + context

    def get_specific_recommendations(self) -> str:
        """
        Get specific, actionable investment recommendations.

        This method uses a more directive prompt that forces Claude to give
        specific ticker recommendations with dollar amounts.

        Returns:
            Detailed recommendations string
        """
        try:
            user_message = """Review my portfolio and give me your TOP 5 specific investment recommendations.

For each recommendation, tell me:
- EXACTLY what to buy or sell (specific ticker symbol)
- EXACTLY how much in dollars
- WHY this improves my portfolio

I want actionable advice I can execute today. Be specific with numbers.

Consider:
1. Any positions I should reduce due to concentration risk
2. Asset classes or sectors I'm missing
3. Rebalancing needed to hit target allocation
4. Tax-loss harvesting opportunities
5. Low-cost alternatives to high-fee funds

Give me the recommendations like a financial advisor would in a portfolio review meeting."""

            response = self.client.messages.create(
                model=self.model,
                system=self.build_recommendations_system_prompt(),
                messages=[{"role": "user", "content": user_message}],
                max_tokens=1500,
            )

            # Handle empty response
            if not response.content:
                print(f"[AI Advisor] Empty recommendations response. Stop reason: {response.stop_reason}")
                return "I wasn't able to generate recommendations. Please try again."

            return response.content[0].text

        except Exception as e:
            error_msg = str(e)
            print(f"[AI Advisor] Recommendations error: {error_msg}")
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "I'm unable to connect to the AI service. Please check that your Anthropic API key is configured correctly in the .env file."
            elif "rate_limit" in error_msg.lower():
                return "I'm receiving too many requests right now. Please try again in a few moments."
            else:
                return f"I encountered an error generating recommendations. Please try again. (Error: {error_msg[:100]})"

    def get_rebalancing_plan(self) -> Dict[str, Any]:
        """
        Get a structured rebalancing plan.

        Returns:
            Dict containing rebalancing recommendations and AI commentary
        """
        try:
            calculator = RebalancingCalculator(self.portfolio_data)
            action_plan = calculator.generate_action_plan()

            # Get AI commentary on the plan
            ai_summary = self.get_quick_insight("allocation")

            return {
                'success': True,
                'action_plan': action_plan,
                'ai_commentary': ai_summary
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def is_api_configured() -> bool:
    """Check if the Anthropic API key is configured."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    return bool(api_key and api_key.strip() and not api_key.startswith('sk-ant-...'))

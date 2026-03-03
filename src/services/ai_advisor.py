"""
AI-Powered Investment Advisor using OpenAI GPT-4o.

Provides personalized portfolio insights through natural language conversation.
"""
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIAdvisor:
    """AI investment advisor that provides portfolio insights using GPT-4o."""

    def __init__(self, portfolio_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI advisor.

        Args:
            portfolio_data: Dictionary containing portfolio analysis data
        """
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
        self.portfolio_data = portfolio_data or {}

    def build_system_prompt(self) -> str:
        """Build the system prompt with portfolio context."""
        base_prompt = """You are an expert investment advisor with access to the user's portfolio data.
Your role as a financial advisor is to provide personalized, actionable investment insights based on their actual holdings.

IMPORTANT GUIDELINES:
- Be specific about their actual holdings when giving advice
- Compare the portfolio for concentration risk and diversification
- Explain complex financial concepts in simple terms
- Provide actionable recommendations when appropriate
- Consider tax implications of any suggested moves
- Mention relevant market trends when helpful
- Be conversational but professional
- Keep responses concise but informative (2-4 paragraphs max)
- Recommend clear next steps on what changes can be made to the investments
- If you don't know something, say so honestly
- Never provide specific buy/sell timing recommendations
- Always remind users to consult a financial advisor for major decisions

DISCLAIMER: Always remind users that this is educational information, not personalized financial advice."""

        if not self.portfolio_data:
            return base_prompt + "\n\nNote: No portfolio data is currently loaded."

        # Extract portfolio details
        portfolio = self.portfolio_data.get('portfolio', {})
        diversification = self.portfolio_data.get('diversification', {})
        concentration = self.portfolio_data.get('concentration', {})
        tax = self.portfolio_data.get('tax', {})
        top_holdings = self.portfolio_data.get('top_holdings', [])
        asset_allocation = self.portfolio_data.get('asset_allocation', [])
        sector_allocation = self.portfolio_data.get('sector_allocation', [])

        # Build portfolio context
        context = f"""

PORTFOLIO CONTEXT:
- Total Value: ${portfolio.get('total_value', 0):,.2f}
- Total Cost Basis: ${portfolio.get('total_cost_basis', 0):,.2f}
- Unrealized Gain/Loss: ${portfolio.get('unrealized_gain_loss', 0):,.2f}
- Return: {portfolio.get('return_percent', 0):.2f}%
- Number of Accounts: {portfolio.get('num_accounts', 0)}
- Number of Holdings: {portfolio.get('num_holdings', 0)}

ANALYSIS SCORES:
- Diversification Score: {diversification.get('score', 'N/A')}/100 ({diversification.get('rating', 'N/A')})
- Concentration Risk: {concentration.get('risk_level', 'N/A')}
- Top 10 Holdings Concentration: {concentration.get('top_10_concentration', 0):.1f}%
- Tax Efficiency Score: {tax.get('score', 'N/A')}/100 ({tax.get('rating', 'N/A')})
"""

        # Add top holdings
        if top_holdings:
            context += "\nTOP HOLDINGS:\n"
            for h in top_holdings[:10]:
                gain_status = "+" if h.get('gain_loss', 0) >= 0 else ""
                context += f"- {h.get('ticker', 'N/A')}: ${h.get('value', 0):,.0f} ({h.get('percent', 0):.1f}%), Gain/Loss: {gain_status}${h.get('gain_loss', 0):,.0f}\n"

        # Add asset allocation
        if asset_allocation:
            context += "\nASSET ALLOCATION:\n"
            for a in asset_allocation[:8]:
                context += f"- {a.get('name', 'N/A')}: {a.get('percent', 0):.1f}% (${a.get('value', 0):,.0f})\n"

        # Add sector allocation
        if sector_allocation:
            context += "\nSECTOR ALLOCATION:\n"
            for s in sector_allocation[:8]:
                context += f"- {s.get('name', 'N/A')}: {s.get('percent', 0):.1f}%\n"

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
            # Build full message list with system prompt
            full_messages = [
                {"role": "system", "content": self.build_system_prompt()}
            ] + messages

            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=1000,
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "I'm unable to connect to the AI service. Please check that your OpenAI API key is configured correctly in the .env file."
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


def is_api_configured() -> bool:
    """Check if the OpenAI API key is configured."""
    api_key = os.getenv('OPENAI_API_KEY')
    return bool(api_key and api_key.strip() and not api_key.startswith('sk-...'))

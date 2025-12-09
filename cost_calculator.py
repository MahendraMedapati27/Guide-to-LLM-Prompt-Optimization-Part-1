from typing import Dict, Optional

class CostCalculator:
    """Calculate costs for Groq LLM provider"""
    
    # Groq pricing (as of 2024) - Very affordable!
    # Note: Groq offers generous free tier for demonstrations
    PRICING = {
        "groq": {
            "llama-3.1-70b-versatile": {
                "input": 0.27,
                "output": 0.27,
                "cached_input": 0.027  # 10% of normal (simulated)
            },
            "llama-3.1-8b-instant": {
                "input": 0.05,
                "output": 0.05,
                "cached_input": 0.005
            },
            "mixtral-8x7b-32768": {
                "input": 0.24,
                "output": 0.24,
                "cached_input": 0.024
            },
            "gemma-7b-it": {
                "input": 0.07,
                "output": 0.07,
                "cached_input": 0.007
            },
            "llama-3.3-70b-versatile": {
                "input": 0.27,
                "output": 0.27,
                "cached_input": 0.027
            }
        }
    }
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        provider: str = "groq",
        model: str = "llama-3.1-70b-versatile"
    ) -> float:
        """Calculate total cost for a request"""
        provider_key = "groq"
        
        if model not in self.PRICING[provider_key]:
            # Use default model as fallback
            model = "llama-3.1-70b-versatile"
        
        pricing = self.PRICING[provider_key][model]
        
        # Calculate costs
        non_cached_input = input_tokens - cached_tokens
        input_cost = (non_cached_input / 1_000_000) * pricing["input"]
        cached_cost = (cached_tokens / 1_000_000) * pricing["cached_input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + cached_cost + output_cost
    
    def calculate_savings(
        self,
        original_cost: float,
        optimized_cost: float
    ) -> Dict[str, float]:
        """Calculate savings from optimization"""
        savings = original_cost - optimized_cost
        savings_percentage = (savings / original_cost * 100) if original_cost > 0 else 0
        
        return {
            "absolute": savings,
            "percentage": savings_percentage
        }
    
    def project_monthly_cost(
        self,
        daily_users: int,
        tokens_per_user: int,
        days_per_month: int = 30,
        provider: str = "groq",
        model: str = "llama-3.1-70b-versatile",
        use_caching: bool = False,
        cache_hit_rate: float = 0.9
    ) -> Dict[str, float]:
        """Project monthly costs"""
        total_tokens = daily_users * tokens_per_user * days_per_month
        
        if use_caching:
            # First request: full cost
            # Subsequent requests: 90% cached (estimated)
            first_request_tokens = tokens_per_user * 0.1  # 10% of tokens are new
            cached_tokens = tokens_per_user * 0.9 * cache_hit_rate
            effective_tokens_per_user = first_request_tokens + (cached_tokens * 0.1)  # Cached tokens cost 10% of normal
            total_tokens = daily_users * effective_tokens_per_user * days_per_month
        
        cost = self.calculate_cost(
            input_tokens=total_tokens,
            output_tokens=total_tokens * 0.1,  # Estimate 10% output
            cached_tokens=total_tokens * 0.9 if use_caching else 0,
            provider=provider,
            model=model
        )
        
        return {
            "monthly_cost": cost,
            "annual_cost": cost * 12,
            "total_tokens": total_tokens
        }

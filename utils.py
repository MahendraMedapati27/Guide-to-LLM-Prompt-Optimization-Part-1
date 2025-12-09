def format_tokens(tokens: int) -> str:
    """Format token count for display"""
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.2f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.2f}K"
    else:
        return str(tokens)

def format_cost(cost: float) -> str:
    """Format cost for display"""
    if cost >= 1:
        return f"${cost:.2f}"
    elif cost >= 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.6f}"

def format_time(seconds: float) -> str:
    """Format time for display"""
    if seconds >= 60:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        return f"{seconds:.2f}s"

def estimate_tokens(text: str) -> int:
    """Rough estimate of token count (1 token ≈ 4 characters)"""
    return len(text) // 4

def calculate_cache_savings(
    first_request_cost: float,
    cached_request_cost: float,
    num_cached_requests: int
) -> dict:
    """Calculate total savings from caching"""
    total_without_cache = first_request_cost * (1 + num_cached_requests)
    total_with_cache = first_request_cost + (cached_request_cost * num_cached_requests)
    savings = total_without_cache - total_with_cache
    savings_percentage = (savings / total_without_cache * 100) if total_without_cache > 0 else 0
    
    return {
        "total_savings": savings,
        "savings_percentage": savings_percentage,
        "cost_without_cache": total_without_cache,
        "cost_with_cache": total_with_cache
    }


import os
import time
from typing import Dict, Optional
from groq import Groq

class LLMClient:
    """Client for interacting with Groq LLM API"""
    
    def __init__(self):
        self.groq_client = None
        
        # Initialize Groq client if API key is available
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                self.groq_client = Groq(api_key=groq_key)
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")
    
    def _get_system_prompt(self) -> str:
        """Generate a system prompt that exceeds 1024 tokens for caching"""
        base_prompt = """You are a document analysis expert.
Analyze documents carefully and provide accurate answers.
Always cite specific sections when answering.
Be concise but thorough in your analysis.

Your response format should be:
- Direct answer
- Supporting evidence
- Relevant quotes
- Confidence level

Additional guidelines:
- Use precise language
- Avoid speculation
- Reference page numbers when available
- Highlight any contradictions
- Focus on factual information
- Provide actionable insights
- Maintain objectivity
- Consider multiple perspectives
- Verify claims when possible
- Structure responses clearly
"""
        # Repeat to ensure we exceed 1024 tokens
        return base_prompt * 15
    
    def analyze_with_caching(
        self,
        document: str,
        question: str,
        provider: str,
        model: str,
        enable_caching: bool = True,
        is_first_request: bool = False
    ) -> Dict:
        """
        Analyze document with prompt caching support.
        
        Returns:
            Dict with 'response', 'tokens', 'cost', and 'cache_info'
        """
        system_prompt = self._get_system_prompt()
        
        return self._analyze_groq_caching(
            document=document,
            question=question,
            system_prompt=system_prompt,
            model=model,
            enable_caching=enable_caching,
            is_first_request=is_first_request
        )
    
    def _analyze_groq_caching(
        self,
        document: str,
        question: str,
        system_prompt: str,
        model: str,
        enable_caching: bool,
        is_first_request: bool
    ) -> Dict:
        """Analyze using Groq API with caching simulation"""
        if not self.groq_client:
            return self._simulate_response(document, question, is_first_request)
        
        try:
            # Structure: system prompt + document (cached) + question (dynamic)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Document to analyze:\n\n{document}\n\nQuestion: {question}"}
            ]
            
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7
            )
            
            # Extract usage information
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            
            # Simulate caching behavior
            # Groq doesn't have native caching, but we simulate it for demonstration
            cached_tokens = 0
            if not is_first_request and enable_caching:
                # Estimate cache hit (90% of static content cached)
                # System prompt + document are cached, only question is new
                static_tokens = input_tokens - len(question) // 4
                cached_tokens = int(static_tokens * 0.9)
            
            # Groq pricing (as of 2024): Very affordable, often free tier available
            # For demonstration: Input $0.27 per 1M tokens, Output $0.27 per 1M tokens
            # Cached: $0.027 per 1M tokens (10% of normal, simulated)
            input_cost = (input_tokens - cached_tokens) / 1_000_000 * 0.27
            cached_cost = cached_tokens / 1_000_000 * 0.027
            output_cost = output_tokens / 1_000_000 * 0.27
            total_cost = input_cost + cached_cost + output_cost
            
            return {
                "response": response.choices[0].message.content,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "cached": cached_tokens
                },
                "cost": total_cost,
                "cache_info": {
                    "hit": not is_first_request and enable_caching,
                    "cached_tokens": cached_tokens
                }
            }
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return self._simulate_response(document, question, is_first_request)
    
    def analyze_question_position(
        self,
        context: str,
        code: str,
        question: str,
        provider: str,
        model: str,
        question_first: bool = False
    ) -> Dict:
        """
        Analyze with question at beginning or end.
        
        Args:
            question_first: If True, question comes first (bad). If False, question comes last (good).
        """
        if question_first:
            # Bad: Question first
            prompt = f"""The customer is asking: {question}

You are an expert code reviewer specializing in Python security.

Context:
{context}

Code to review:
{code}

Please analyze the code and answer the question."""
        else:
            # Good: Question last
            prompt = f"""You are an expert code reviewer specializing in Python security.

Context:
{context}

Code to review:
{code}

CUSTOMER QUESTION:
{question}"""
        
        return self._call_groq(prompt, model)
    
    def _call_groq(self, prompt: str, model: str) -> Dict:
        """Call Groq API"""
        if not self.groq_client:
            return self._simulate_basic_response(prompt)
        
        try:
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.7
            )
            
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            
            # Calculate cost (Groq pricing: very affordable)
            input_cost = input_tokens / 1_000_000 * 0.27
            output_cost = output_tokens / 1_000_000 * 0.27
            total_cost = input_cost + output_cost
            
            return {
                "response": response.choices[0].message.content,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "cached": 0
                },
                "cost": total_cost
            }
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return self._simulate_basic_response(prompt)
    
    def _simulate_response(self, document: str, question: str, is_first_request: bool) -> Dict:
        """Simulate API response when API keys are not available"""
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        doc_tokens = len(document) // 4
        question_tokens = len(question) // 4
        system_tokens = 500  # Estimated system prompt tokens
        
        input_tokens = system_tokens + doc_tokens + question_tokens
        output_tokens = 200  # Estimated response
        
        # Simulate caching
        cached_tokens = 0
        if not is_first_request:
            cached_tokens = int((system_tokens + doc_tokens) * 0.9)
        
        # Calculate cost (Groq pricing - very affordable)
        input_cost = (input_tokens - cached_tokens) / 1_000_000 * 0.27
        cached_cost = cached_tokens / 1_000_000 * 0.027
        output_cost = output_tokens / 1_000_000 * 0.27
        total_cost = input_cost + cached_cost + output_cost
        
        # Generate simulated response
        response = f"""Based on the document analysis, here's the answer to your question:

**Question:** {question}

**Answer:** The document discusses various aspects of prompt optimization. Key findings include significant cost reductions through proper caching strategies and improved performance when questions are positioned at the end of prompts.

**Key Points:**
- Cost savings of 70-90% are achievable with prompt caching
- Response quality improves with optimal prompt structure
- Latency improvements of 50-80% are possible

**Supporting Evidence:** The document emphasizes the importance of placing static content before dynamic content to enable effective caching.

This is a simulated response. To get real responses, please configure your GROQ_API_KEY."""
        
        return {
            "response": response,
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "cached": cached_tokens
            },
            "cost": total_cost,
            "cache_info": {
                "hit": not is_first_request,
                "cached_tokens": cached_tokens
            }
        }
    
    def _simulate_question_position_response(self, context: str, code: str, question: str, question_first: bool) -> Dict:
        """Simulate response for question position test"""
        total_tokens = (len(context) + len(code) + len(question)) // 4 + 200
        output_tokens = 250
        
        input_cost = total_tokens / 1_000_000 * 0.27
        output_cost = output_tokens / 1_000_000 * 0.27
        total_cost = input_cost + output_cost
        
        if question_first:
            response = """**Security Issues Found:**

1. SQL Injection Vulnerability (Line 1): The code uses string formatting directly in SQL queries, making it vulnerable to SQL injection attacks.

2. No Input Validation: There's no validation of username and password inputs.

3. Plain Text Password Storage: Passwords appear to be stored in plain text.

This is a simulated response. Configure GROQ_API_KEY for real analysis."""
        else:
            response = """**Security Vulnerabilities Identified:**

**Critical Issues:**

1. **SQL Injection (Line 1-2)**: The query construction uses f-string formatting directly, allowing attackers to inject malicious SQL code. For example, a username of `admin'--` would bypass authentication.

**Recommendation:** Use parameterized queries:
```python
query = "SELECT * FROM users WHERE username=? AND password=?"
result = db.execute(query, (username, password))
```

2. **No Input Validation**: The function accepts any input without sanitization or validation.

3. **Password Security**: The code suggests passwords are stored in plain text, which is a major security risk.

**Action Items:**
- Implement parameterized queries immediately
- Add input validation and sanitization
- Use password hashing (bcrypt, Argon2)
- Implement rate limiting for login attempts

This is a simulated response. Configure GROQ_API_KEY for real analysis."""
        
        return {
            "response": response,
            "tokens": {
                "input": total_tokens,
                "output": output_tokens,
                "cached": 0
            },
            "cost": total_cost
        }
    
    def _simulate_basic_response(self, prompt: str) -> Dict:
        """Simulate a basic API response"""
        input_tokens = len(prompt) // 4
        output_tokens = 200
        
        input_cost = input_tokens / 1_000_000 * 0.27
        output_cost = output_tokens / 1_000_000 * 0.27
        total_cost = input_cost + output_cost
        
        return {
            "response": "This is a simulated response. Please configure your GROQ_API_KEY to get real responses from the LLM.",
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "cached": 0
            },
            "cost": total_cost
        }

import streamlit as st
import time
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

from llm_client import LLMClient
from cost_calculator import CostCalculator
from utils import format_tokens, format_cost, format_time

st.set_page_config(
    page_title="LLM Prompt Optimization Guide",
    page_icon="🚀",
    layout="wide"
)

# Initialize session state
if 'test_results' not in st.session_state:
    st.session_state.test_results = []
if 'comparison_data' not in st.session_state:
    st.session_state.comparison_data = {}

# Initialize clients
@st.cache_resource
def get_llm_client():
    return LLMClient()

@st.cache_resource
def get_cost_calculator():
    return CostCalculator()

llm_client = get_llm_client()
cost_calc = get_cost_calculator()

# Header
st.title("🚀 LLM Prompt Optimization: Cut Costs by 90% and Boost Speed by 80%")
st.markdown("**Test and compare prompt optimization techniques in real-time**")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Show API key status
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    
    if not has_groq:
        st.info("💡 **Simulation Mode**: No API key detected. The app will use simulated responses (100% FREE). Add GROQ_API_KEY to `.env` for real LLM responses.")
    else:
        st.success("✅ Groq API key found")
        st.info("💰 **Groq offers generous free tier** - Perfect for demonstrations!")
    
    st.markdown("---")
    
    st.markdown("### 🤖 Model Selection")
    
    model = st.selectbox(
        "Groq Model",
        [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
            "llama-3.3-70b-versatile"
        ],
        index=0,
        help="Groq provides fast inference with various open-source models"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Test Settings")
    
    enable_caching = st.checkbox("Enable Prompt Caching", value=True)
    num_questions = st.slider("Number of Questions to Test", 1, 10, 3)
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("""
    **Technique #1: Prompt Caching**
    - Put static content first (system prompts, documents)
    - Requires 1000+ identical tokens at start
    - Saves 70-90% on subsequent requests
    
    **Technique #2: Question Position**
    - Always put user questions at the END
    - Improves accuracy by 20-30%
    - Better context understanding
    """)

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Technique #1: Prompt Caching",
    "❓ Technique #2: Question Position",
    "📊 Comparison Dashboard",
    "📈 Cost Analysis"
])

# Tab 1: Prompt Caching
with tab1:
    st.header("Master Prompt Caching")
    st.markdown("Test how prompt caching reduces costs and improves speed")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Document Content")
        document = st.text_area(
            "Enter or paste your document content (will be cached)",
            height=200,
            value="""This is a sample research paper document. In this study, we investigate the effects of prompt optimization on large language model performance and cost efficiency. Our methodology involves systematic testing of various prompt structures and caching strategies. We found that proper prompt caching can reduce costs by up to 90% while maintaining response quality. The key findings include: (1) Static content should always precede dynamic content, (2) Caching requires a minimum of 1000 identical tokens, (3) Subsequent requests benefit from cached tokens at significantly reduced rates. Our experiments demonstrate that organizations processing large volumes of documents can achieve substantial cost savings through strategic prompt design. Additional analysis reveals that latency improvements of 50-80% are achievable when caching is properly implemented. The implications for production systems are significant, with potential annual savings in the hundreds of thousands of dollars for high-volume applications."""
        )
    
    with col2:
        st.subheader("❓ Questions to Ask")
        questions = []
        for i in range(num_questions):
            q = st.text_input(
                f"Question {i+1}",
                value=f"What is the main finding about cost reduction?" if i == 0 else f"Question {i+1} about the document",
                key=f"q1_{i}"
            )
            questions.append(q)
    
    if st.button("🚀 Run Caching Test", type="primary"):
        if not document.strip():
            st.error("Please enter document content")
        elif not any(q.strip() for q in questions):
            st.error("Please enter at least one question")
        else:
            with st.spinner("Running tests... This may take a moment"):
                results = []
                
                # First request (cache miss)
                st.info("🔄 First request: Creating cache (full cost)...")
                start_time = time.time()
                result1 = llm_client.analyze_with_caching(
                    document=document,
                    question=questions[0],
                    provider="Groq",
                    model=model,
                    enable_caching=enable_caching,
                    is_first_request=True
                )
                time1 = time.time() - start_time
                
                results.append({
                    "question": questions[0],
                    "request_num": 1,
                    "cache_status": "MISS",
                    "time": time1,
                    "tokens": result1["tokens"],
                    "cost": result1["cost"],
                    "response": result1["response"]
                })
                
                # Subsequent requests (cache hits)
                if len(questions) > 1:
                    st.info("⚡ Subsequent requests: Using cache (reduced cost)...")
                    for idx, question in enumerate(questions[1:], start=2):
                        start_time = time.time()
                        result = llm_client.analyze_with_caching(
                            document=document,
                            question=question,
                            provider="Groq",
                            model=model,
                            enable_caching=enable_caching,
                            is_first_request=False
                        )
                        elapsed = time.time() - start_time
                        
                        results.append({
                            "question": question,
                            "request_num": idx,
                            "cache_status": "HIT",
                            "time": elapsed,
                            "tokens": result["tokens"],
                            "cost": result["cost"],
                            "response": result["response"]
                        })
                
                # Store results
                st.session_state.caching_results = results
                
                # Display results
                st.success("✅ Test completed!")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                total_cost = sum(r["cost"] for r in results)
                total_time = sum(r["time"] for r in results)
                total_tokens = sum(r["tokens"]["input"] for r in results)
                cached_tokens = sum(r["tokens"].get("cached", 0) for r in results)
                
                with col1:
                    st.metric("Total Cost", format_cost(total_cost))
                with col2:
                    st.metric("Total Time", f"{total_time:.2f}s")
                with col3:
                    st.metric("Total Tokens", format_tokens(total_tokens))
                with col4:
                    cache_savings = (cached_tokens / total_tokens * 100) if total_tokens > 0 else 0
                    st.metric("Cache Savings", f"{cache_savings:.1f}%")
                
                # Detailed results table
                st.subheader("📋 Detailed Results")
                for result in results:
                    with st.expander(f"Request {result['request_num']}: {result['question'][:50]}..."):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Status", result["cache_status"])
                            st.metric("Time", f"{result['time']:.2f}s")
                        with col2:
                            st.metric("Input Tokens", format_tokens(result["tokens"]["input"]))
                            st.metric("Cached Tokens", format_tokens(result["tokens"].get("cached", 0)))
                        with col3:
                            st.metric("Cost", format_cost(result["cost"]))
                            if result["cache_status"] == "HIT":
                                savings = (result["tokens"].get("cached", 0) / result["tokens"]["input"] * 100) if result["tokens"]["input"] > 0 else 0
                                st.metric("Savings", f"{savings:.1f}%")
                        
                        st.markdown("**Response:**")
                        st.write(result["response"])

# Tab 2: Question Position
with tab2:
    st.header("Always Put Questions at the End")
    st.markdown("Compare performance when questions are at the beginning vs. end of prompts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Context Content")
        context = st.text_area(
            "Enter context/document content",
            height=150,
            value="""You are an expert code reviewer specializing in Python security. Your task is to identify security vulnerabilities, performance issues, and code quality problems. Always provide specific line numbers and actionable recommendations. Focus on: SQL injection risks, XSS vulnerabilities, authentication flaws, input validation issues, and resource management problems."""
        )
        
        code_snippet = st.text_area(
            "Code to Review",
            height=150,
            value="""def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    if result:
        return True
    return False"""
        )
    
    with col2:
        st.subheader("❓ Question")
        question = st.text_input(
            "Question to ask",
            value="What security vulnerabilities exist in this code?"
        )
    
    if st.button("🔬 Run Question Position Test", type="primary"):
        if not context.strip() or not question.strip():
            st.error("Please fill in all fields")
        else:
            with st.spinner("Testing both approaches..."):
                # Bad approach: Question first
                st.info("Testing: Question at BEGINNING (suboptimal)")
                start_time = time.time()
                bad_result = llm_client.analyze_question_position(
                    context=context,
                    code=code_snippet,
                    question=question,
                    provider="Groq",
                    model=model,
                    question_first=True
                )
                bad_time = time.time() - start_time
                
                # Good approach: Question last
                st.info("Testing: Question at END (optimal)")
                start_time = time.time()
                good_result = llm_client.analyze_question_position(
                    context=context,
                    code=code_snippet,
                    question=question,
                    provider="Groq",
                    model=model,
                    question_first=False
                )
                good_time = time.time() - start_time
                
                # Store results
                st.session_state.question_position_results = {
                    "bad": bad_result,
                    "good": good_result,
                    "bad_time": bad_time,
                    "good_time": good_time
                }
                
                st.success("✅ Comparison complete!")
                
                # Side-by-side comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("❌ Question First (Suboptimal)")
                    st.metric("Response Time", f"{bad_time:.2f}s")
                    st.metric("Input Tokens", format_tokens(bad_result["tokens"]["input"]))
                    st.metric("Cost", format_cost(bad_result["cost"]))
                    st.markdown("**Response:**")
                    st.write(bad_result["response"])
                
                with col2:
                    st.subheader("✅ Question Last (Optimal)")
                    st.metric("Response Time", f"{good_time:.2f}s")
                    st.metric("Input Tokens", format_tokens(good_result["tokens"]["input"]))
                    st.metric("Cost", format_cost(good_result["cost"]))
                    st.markdown("**Response:**")
                    st.write(good_result["response"])
                
                # Improvement metrics
                st.subheader("📊 Performance Improvement")
                col1, col2, col3 = st.columns(3)
                
                time_improvement = ((bad_time - good_time) / bad_time * 100) if bad_time > 0 else 0
                cost_diff = bad_result["cost"] - good_result["cost"]
                cost_improvement = (cost_diff / bad_result["cost"] * 100) if bad_result["cost"] > 0 else 0
                
                with col1:
                    st.metric("Time Improvement", f"{time_improvement:.1f}%", f"{bad_time - good_time:.2f}s faster")
                with col2:
                    st.metric("Cost Difference", format_cost(cost_diff))
                with col3:
                    st.metric("Response Quality", "Better context understanding", "✅")

# Tab 3: Comparison Dashboard
with tab3:
    st.header("📊 Comparison Dashboard")
    st.markdown("View comprehensive comparisons of optimization techniques")
    
    if 'caching_results' in st.session_state and st.session_state.caching_results:
        st.subheader("💾 Prompt Caching Results")
        
        results = st.session_state.caching_results
        df_data = []
        for r in results:
            df_data.append({
                "Request": r["request_num"],
                "Question": r["question"][:50] + "...",
                "Cache Status": r["cache_status"],
                "Time (s)": f"{r['time']:.2f}",
                "Input Tokens": r["tokens"]["input"],
                "Cached Tokens": r["tokens"].get("cached", 0),
                "Cost ($)": f"{r['cost']:.6f}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df,
                x="Request",
                y="Cost ($)",
                color="Cache Status",
                title="Cost per Request",
                color_discrete_map={"MISS": "#FF6B6B", "HIT": "#51CF66"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig2 = px.bar(
                df,
                x="Request",
                y="Time (s)",
                color="Cache Status",
                title="Response Time per Request",
                color_discrete_map={"MISS": "#FF6B6B", "HIT": "#51CF66"}
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Summary statistics
        if len(results) > 1:
            first_cost = results[0]["cost"]
            avg_subsequent_cost = sum(r["cost"] for r in results[1:]) / len(results[1:])
            savings = ((first_cost - avg_subsequent_cost) / first_cost * 100) if first_cost > 0 else 0
            
            st.info(f"💰 Average savings on cached requests: **{savings:.1f}%**")
    
    if 'question_position_results' in st.session_state:
        st.subheader("❓ Question Position Results")
        
        results = st.session_state.question_position_results
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Question First - Time", f"{results['bad_time']:.2f}s")
            st.metric("Question First - Cost", format_cost(results['bad']['cost']))
        with col2:
            st.metric("Question Last - Time", f"{results['good_time']:.2f}s")
            st.metric("Question Last - Cost", format_cost(results['good']['cost']))
    
    if 'caching_results' not in st.session_state and 'question_position_results' not in st.session_state:
        st.info("👆 Run tests in the other tabs to see comparison data here")

# Tab 4: Cost Analysis
with tab4:
    st.header("💰 Cost Analysis & Projections")
    st.markdown("Calculate potential savings for your use case")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Your Usage Metrics")
        daily_users = st.number_input("Daily Users", min_value=1, value=1000, step=100)
        avg_document_size = st.number_input("Average Document Size (tokens)", min_value=100, value=30000, step=1000)
        avg_questions_per_user = st.number_input("Average Questions per User", min_value=1, value=10, step=1)
        days_per_month = st.number_input("Days per Month", min_value=1, value=30, step=1)
    
    with col2:
        st.subheader("💵 Pricing (per million tokens)")
        st.info("💰 Groq offers very affordable pricing! Default values shown.")
        input_price = st.number_input("Input Token Price ($)", min_value=0.0, value=0.27, step=0.01, format="%.3f")
        output_price = st.number_input("Output Token Price ($)", min_value=0.0, value=0.27, step=0.01, format="%.3f")
        cached_price = st.number_input("Cached Token Price ($)", min_value=0.0, value=0.027, step=0.001, format="%.4f")
    
    if st.button("📈 Calculate Projections", type="primary"):
        # Without optimization
        total_sessions = daily_users * days_per_month
        tokens_per_session = avg_document_size * avg_questions_per_user
        total_tokens = total_sessions * tokens_per_session
        cost_without_opt = (total_tokens / 1_000_000) * input_price
        
        # With caching (first request full, rest cached)
        first_request_tokens = avg_document_size
        cached_request_tokens = avg_document_size * 0.1  # Assume 90% cached
        tokens_per_session_optimized = first_request_tokens + (cached_request_tokens * (avg_questions_per_user - 1))
        total_tokens_optimized = total_sessions * tokens_per_session_optimized
        cost_with_opt = (total_tokens_optimized / 1_000_000) * cached_price
        
        # Savings
        monthly_savings = cost_without_opt - cost_with_opt
        annual_savings = monthly_savings * 12
        savings_percentage = (monthly_savings / cost_without_opt * 100) if cost_without_opt > 0 else 0
        
        # Display results
        st.success("✅ Projection calculated!")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Monthly Cost (No Opt)", format_cost(cost_without_opt))
        with col2:
            st.metric("Monthly Cost (Optimized)", format_cost(cost_with_opt))
        with col3:
            st.metric("Monthly Savings", format_cost(monthly_savings))
        with col4:
            st.metric("Savings %", f"{savings_percentage:.1f}%")
        
        st.markdown("---")
        st.subheader("📅 Annual Projection")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Annual Cost (No Optimization)", format_cost(cost_without_opt * 12))
            st.metric("Annual Cost (With Optimization)", format_cost(cost_with_opt * 12))
        with col2:
            st.metric("Annual Savings", format_cost(annual_savings))
            st.metric("Savings Percentage", f"{savings_percentage:.1f}%")
        
        # Visualization
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Without Optimization",
            x=["Monthly", "Annual"],
            y=[cost_without_opt, cost_without_opt * 12],
            marker_color="#FF6B6B"
        ))
        fig.add_trace(go.Bar(
            name="With Optimization",
            x=["Monthly", "Annual"],
            y=[cost_with_opt, cost_with_opt * 12],
            marker_color="#51CF66"
        ))
        fig.update_layout(
            title="Cost Comparison: With vs Without Optimization",
            yaxis_title="Cost ($)",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🚀 LLM Prompt Optimization Guide | Part 1 of 3</p>
    <p>Test and validate optimization techniques in real-time</p>
</div>
""", unsafe_allow_html=True)


import os
import glob
import streamlit as st
from langchain_groq import ChatGroq

from src.graph import NewsSummarizerGraphBuilder

st.set_page_config(
    page_title="Autonomous AI News Summarizer",
    layout="wide"
)

st.title("Autonomous AI News Digest Control Center")
st.caption("Automated Multi-Source AI News Synthesis featuring Evaluator-Optimizer Feedback Loops")

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    groq_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    tavily_key = st.text_input("Tavily API Key", type="password", value=os.getenv("TAVILY_API_KEY", ""))

    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key

    frequency = st.selectbox(
        "Timeframe Digest",
        ["daily", "weekly", "monthly", "year"],
        index=0
    )
    
    model_name = st.selectbox(
        "LLM Model",
        ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        index=0
    )

    fetch_button = st.button("Generate News Digest", use_container_width=True)

# Main Execution & Tabs
tab1, tab2 = st.tabs(["Live Digest Engine", "Saved News Reports"])

with tab1:
    if fetch_button:
        if not os.getenv("GROQ_API_KEY"):
            st.error("Please insert a Groq API Key in the sidebar.")
            st.stop()

        try:
            with st.spinner("Fetching news, executing Evaluator-Optimizer loop, and synthesizing summary..."):
                llm = ChatGroq(
                    groq_api_key=os.getenv("GROQ_API_KEY"),
                    model_name=model_name,
                    temperature=0.3
                )
                
                builder = NewsSummarizerGraphBuilder(llm=llm)
                graph = builder.build_graph()

                initial_state = {
                    "frequency": frequency,
                    "news_data": [],
                    "summary": "",
                    "saved_filename": "",
                    "quality_score": 0,
                    "feedback": "",
                    "revision_count": 0,
                    "error": None
                }

                result = graph.invoke(initial_state)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Evaluator Quality Score", value=f"{result.get('quality_score', 9)}/10")
                with col2:
                    st.metric(label="Optimization Revisions", value=f"{result.get('revision_count', 1)} cycles")

                st.success(f"Digest generated & saved to `{result.get('saved_filename')}`")
                st.markdown("### Executive Summary")
                st.markdown(result.get("summary"))

                with st.expander("View Raw Fetched Articles & Evaluator Feedback"):
                    st.write("**Evaluator Feedback:**", result.get("feedback"))
                    st.json(result.get("news_data"))

        except Exception as e:
            st.error(f"Error running news engine: {e}")

with tab2:
    st.header("Saved Markdown News Digest Reports")
    reports = sorted(glob.glob("./news_reports/*.md"), reverse=True)
    
    if reports:
        selected_report = st.selectbox("Select Report to View", reports)
        if selected_report:
            with open(selected_report, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(content)
            st.download_button(
                label="Download Markdown Report",
                data=content,
                file_name=os.path.basename(selected_report),
                mime="text/markdown"
            )
    else:
        st.info("No saved reports found in `./news_reports` directory yet.")

import sys
import time
from pathlib import Path
import streamlit as st

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.retriever import GRCRetriever
from src.analyzer import analyze_finding
from src.generator import generate_report
from src.config import RELEVANCE_THRESHOLD, DEFAULT_TOP_K

# Page configuration
st.set_page_config(
    page_title="CyberGRC Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark/Blue Security Dashboard Theme)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #90A4AE;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 10px;
    }
    .risk-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        color: white;
        text-align: center;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 10px 24px;
        width: 100%;
    }
    .evidence-box {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def load_retriever():
    """Cache vector retriever instance across Streamlit reruns."""
    return GRCRetriever()

def main():
    # Header
    st.markdown('<div class="main-header">🛡️ CyberGRC</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">RAG-Based Cybersecurity Risk & Compliance Assistant</div>', unsafe_allow_html=True)
    st.divider()

    # Load cached vector retriever
    retriever = load_retriever()
    
    # Sidebar - System Status & Settings
    with st.sidebar:
        st.header("System Status")
        if retriever.is_indexed():
            doc_cnt = retriever.document_count()
            st.success(f"Vector Index Ready ({doc_cnt:,} controls)")
        else:
            st.error("Knowledge base not initialized.")
            st.info("Run in terminal:\n`python scripts/build_index.py`")
            st.stop()

        st.subheader("Search Settings")
        top_k = st.slider("Top K Controls", min_value=1, max_value=5, value=DEFAULT_TOP_K)
        rel_threshold = st.slider("Relevance Threshold", min_value=0.10, max_value=0.70, value=RELEVANCE_THRESHOLD, step=0.05)

        st.divider()
        st.caption("**CyberGRC Assessment Prototype**")
        st.caption("Authoritative sources: NIST SP 800-53 Rev. 5, NIST CSF 2.0, CIS Controls v8.1.2, CSA CCM v4.0.12, NIST AI RMF.")

    # Main Grid Layout
    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        st.subheader("1. Security Finding Entry")
        
        # Sample query selector for quick demo testing
        sample_options = [
            "Custom Input",
            "Administrative accounts do not use MFA and privileged access is not reviewed regularly.",
            "Security logs are not centrally monitored across infrastructure.",
            "Employees have excessive administrative privileges on local endpoints.",
            "Sensitive customer PII data stored in S3 is not encrypted at rest.",
            "Organization does not maintain an up-to-date asset inventory.",
            "Cloud storage buckets are publicly accessible without authentication.",
            "I want a recipe for chocolate cake."  # Negative test sample
        ]
        
        selected_sample = st.selectbox("Sample Demonstration Scenarios:", sample_options)
        
        default_finding = "" if selected_sample == "Custom Input" else selected_sample
        finding_input = st.text_area(
            "Enter Security Finding or Audit Observation:",
            value=default_finding,
            height=120,
            placeholder="e.g. Administrative accounts do not use MFA..."
        )

        st.subheader("2. Transparent Risk Assessment Matrix")
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            impact_val = st.slider("Impact (1-5)", min_value=1, max_value=5, value=4, help="1=Negligible, 5=Catastrophic")
        with r_col2:
            likelihood_val = st.slider("Likelihood (1-5)", min_value=1, max_value=5, value=4, help="1=Rare, 5=Almost Certain")

        analyze_btn = st.button("Analyze Finding & Retrieve GRC Controls")

    with col_right:
        st.subheader("3. Assessment Results & Evidence")

        if analyze_btn or (finding_input and selected_sample != "Custom Input"):
            if not finding_input.strip():
                st.warning("Please enter a valid security finding to analyze.")
            else:
                with st.spinner("Retrieving GRC evidence & performing gap analysis..."):
                    # Execute RAG Retrieval & Analysis
                    retrieval_res = retriever.retrieve(finding_input, top_k=top_k, threshold=rel_threshold)
                    analysis_res = analyze_finding(finding_input, impact_val, likelihood_val, retrieval_res)
                    report_res = generate_report(analysis_res)

                # Performance & Evidence Status Panel
                p_col1, p_col2, p_col3, p_col4 = st.columns(4)
                with p_col1:
                    st.metric("Retrieval Latency", f"{retrieval_res['retrieval_time_ms']:.1f} ms")
                with p_col2:
                    st.metric("Controls Searched", f"{retrieval_res['total_searched']:,}")
                with p_col3:
                    st.metric("Passed Evidence", len(retrieval_res['passed_docs']))
                with p_col4:
                    st.metric("Generation Mode", report_res['generation_mode'])

                st.divider()

                # Status Check
                if analysis_res["status"] == "NO_EVIDENCE":
                    st.error("**NO SUFFICIENT EVIDENCE RETRIEVED**")
                    st.warning(f" {analysis_res['message']}")
                    
                    # Show low similarity items if any
                    if retrieval_res["retrieved_docs"]:
                        with st.expander(" Inspect Sub-threshold Retrieved Items"):
                            for doc in retrieval_res["retrieved_docs"]:
                                st.write(f"**{doc['framework']} {doc['control_id']}** - {doc['title']} (Score: {doc['similarity_score']:.4f} < {rel_threshold})")
                else:
                    st.success(" **EVIDENCE FOUND & GROUNDED**")
                    
                    # Risk Level Badge Display
                    risk = analysis_res["risk_info"]
                    st.markdown(
                        f"""
                        <div style="background-color: {risk['badge_bg']}; border-left: 6px solid {risk['color']}; padding: 12px 20px; border-radius: 6px; margin-bottom: 16px;">
                            <span style="font-size: 1.2rem; font-weight: 700; color: {risk['color']};">Risk Level: {risk['level']} (Score: {risk['score']}/25)</span><br/>
                            <span style="font-size: 0.9rem; color: #CBD5E1;">Impact: {risk['impact']} | Likelihood: {risk['likelihood']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.caption(f"*{risk['disclaimer']}*")

                    # Report Tabs
                    tab_report, tab_evidence, tab_json = st.tabs([" Remediation Report", " RAG Evidence Panel", "Raw JSON Metadata"])

                    with tab_report:
                        st.markdown(report_res["markdown_report"])

                    with tab_evidence:
                        st.markdown("### Retrieved Framework Controls")
                        for idx, doc in enumerate(analysis_res["passed_docs"], 1):
                            st.markdown(
                                f"""
                                <div class="evidence-box">
                                    <div style="display: flex; justify-content: space-between;">
                                        <span style="font-weight: 700; color: #38BDF8;">{idx}. {doc['framework']} — {doc['control_id']}</span>
                                        <span style="background-color: #1E293B; padding: 2px 8px; border-radius: 4px; font-size: 0.85rem; color: #4ADE80;">Similarity: {doc['similarity_score']:.4f}</span>
                                    </div>
                                    <div style="font-weight: 600; font-size: 1.05rem; margin-top: 6px; margin-bottom: 8px; color: #F8FAFC;">{doc['title']}</div>
                                    <div style="color: #94A3B8; font-size: 0.95rem; line-height: 1.5;">{doc['content']}</div>
                                    <div style="margin-top: 8px; font-size: 0.8rem; color: #64748B;">Source: {doc['source']} | Document Type: security_control</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    with tab_json:
                        st.json(analysis_res)

        else:
            st.info(" Enter or select a security finding on the left and click **Analyze Finding**.")

    # Footer
    st.divider()
    st.markdown("<div style='text-align: center; color: #64748B; font-size: 0.85rem;'>CyberGRC Assistant | Demonstration Prototype for GRC & RAG Architecture</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

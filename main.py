from dotenv import load_dotenv
load_dotenv()
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import PyPDF2
from models.summarizer import generate_summary, translate_to_hindi
from models.simplifier import simplify_text, extract_key_points, detect_risks, score_contract, breakdown_clauses

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="LexSimple — Legal Document Simplifier",
    page_icon="⚖️",
    layout="centered"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        color: #f0ede8;
        margin-bottom: 0.2rem;
        line-height: 1.1;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #9e9a94;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .result-card {
        background: #1a1917;
        border: 1px solid #2e2c29;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .result-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #c9a84c;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .result-text { color: #e8e4dc; line-height: 1.7; font-size: 0.95rem; }

    .risk-high {
        background: #2d1515;
        border-left: 4px solid #e05252;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .risk-medium {
        background: #2d2215;
        border-left: 4px solid #e09a52;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .risk-low {
        background: #1a2d15;
        border-left: 4px solid #52a852;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .risk-title { font-weight: 600; font-size: 0.9rem; margin-bottom: 0.3rem; }
    .risk-high .risk-title { color: #e05252; }
    .risk-medium .risk-title { color: #e09a52; }
    .risk-low .risk-title { color: #52a852; }
    .risk-body { color: #d4cfc7; font-size: 0.85rem; line-height: 1.5; }

    .score-circle {
        text-align: center;
        padding: 1.5rem;
        background: #1a1917;
        border-radius: 12px;
        border: 1px solid #2e2c29;
        margin: 1rem 0;
    }
    .score-number { font-size: 4rem; font-weight: 700; line-height: 1; }
    .score-label { font-size: 0.8rem; color: #9e9a94; margin-top: 0.3rem; }
    .score-verdict { font-size: 1rem; color: #e8e4dc; margin-top: 0.8rem; }

    .clause-card {
        background: #1a1917;
        border: 1px solid #2e2c29;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.6rem 0;
    }
    .clause-title { color: #c9a84c; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.4rem; }
    .clause-original { color: #9e9a94; font-size: 0.82rem; margin-bottom: 0.4rem; font-style: italic; }
    .clause-simple { color: #e8e4dc; font-size: 0.9rem; line-height: 1.6; }

    .point-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 0.5rem 0;
        border-bottom: 1px solid #2e2c29;
        color: #d4cfc7;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .point-dot { color: #c9a84c; font-size: 1.2rem; margin-top: -2px; flex-shrink: 0; }

    .stButton > button {
        background: #c9a84c !important;
        color: #0f0e0d !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.95rem !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }
    .stTextArea textarea {
        background: #1a1917 !important;
        color: #f0ede8 !important;
        border: 1px solid #2e2c29 !important;
        border-radius: 10px !important;
    }
    .stDownloadButton > button {
        background: transparent !important;
        color: #c9a84c !important;
        border: 1px solid #c9a84c !important;
        border-radius: 8px !important;
    }
    .divider { border: none; border-top: 1px solid #2e2c29; margin: 1.5rem 0; }
    .hindi-text { font-size: 1.05rem; line-height: 1.9; color: #e8e4dc; }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<div class="hero-title">⚖️ LexSimple</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Paste any legal document — get a plain English explanation instantly.</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ------------------ PDF HELPER ------------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

# ------------------ INPUT ------------------
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("**📄 Upload a PDF**")
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")
with col2:
    st.markdown("**✍️ Or paste legal text**")
    manual_text = st.text_area("", height=150, placeholder="Paste your legal text here...", label_visibility="collapsed")

text = ""
if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    st.success(f"✅ PDF loaded — {len(text)} characters extracted")
elif manual_text.strip():
    text = manual_text.strip()

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ------------------ PROCESS ------------------
if st.button("⚡ Analyse Document"):
    if not text:
        st.warning("⚠️ Please paste some text or upload a PDF first.")
    else:
        # Run all analyses
        with st.spinner("📖 Reading document..."):
            try: summary = generate_summary(text)
            except Exception as e: summary = None; st.error(f"Summary error: {e}")

        with st.spinner("✍️ Simplifying language..."):
            try: simple = simplify_text(text)
            except Exception as e: simple = None; st.error(f"Simplify error: {e}")

        with st.spinner("📝 Extracting key points..."):
            try: points = extract_key_points(text)
            except Exception as e: points = []; st.error(f"Key points error: {e}")

        with st.spinner("⚠️ Detecting risks..."):
            try: risks = detect_risks(text)
            except Exception as e: risks = []; st.error(f"Risk error: {e}")

        with st.spinner("📊 Scoring contract fairness..."):
            try: score_data = score_contract(text)
            except Exception as e: score_data = None; st.error(f"Score error: {e}")

        with st.spinner("🔍 Breaking down clauses..."):
            try: clauses = breakdown_clauses(text)
            except Exception as e: clauses = []; st.error(f"Clause error: {e}")

        with st.spinner("🌐 Translating to Hindi..."):
            try: hindi = translate_to_hindi(simple or summary or text)
            except Exception as e: hindi = None; st.error(f"Hindi error: {e}")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ---- TABS ----
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📌 Summary", "⚠️ Risks", "📊 Score", "🔍 Clauses", "🌐 Hindi"
        ])

        # TAB 1 — Summary + Key Points
        with tab1:
            if summary:
                st.markdown(f'<div class="result-card"><div class="result-label">Summary</div><div class="result-text">{summary}</div></div>', unsafe_allow_html=True)
            if simple:
                st.markdown(f'<div class="result-card"><div class="result-label">Plain English Explanation</div><div class="result-text">{simple}</div></div>', unsafe_allow_html=True)
            if points:
                points_html = "".join([f'<div class="point-item"><span class="point-dot">›</span><span>{p}</span></div>' for p in points])
                st.markdown(f'<div class="result-card"><div class="result-label">Key Points</div>{points_html}</div>', unsafe_allow_html=True)

        # TAB 2 — Risk Detection
        with tab2:
            if not risks:
                st.info("No risks detected or could not analyze.")
            else:
                high = [r for r in risks if r.get("risk_level") == "HIGH"]
                medium = [r for r in risks if r.get("risk_level") == "MEDIUM"]
                low = [r for r in risks if r.get("risk_level") == "LOW"]

                if high:
                    st.markdown(f"**🔴 High Risk — {len(high)} found**")
                    for r in high:
                        st.markdown(f'<div class="risk-high"><div class="risk-title">🔴 {r.get("clause","")}</div><div class="risk-body">{r.get("explanation","")}</div></div>', unsafe_allow_html=True)
                if medium:
                    st.markdown(f"**🟠 Medium Risk — {len(medium)} found**")
                    for r in medium:
                        st.markdown(f'<div class="risk-medium"><div class="risk-title">🟠 {r.get("clause","")}</div><div class="risk-body">{r.get("explanation","")}</div></div>', unsafe_allow_html=True)
                if low:
                    st.markdown(f"**🟢 Low Risk — {len(low)} found**")
                    for r in low:
                        st.markdown(f'<div class="risk-low"><div class="risk-title">🟢 {r.get("clause","")}</div><div class="risk-body">{r.get("explanation","")}</div></div>', unsafe_allow_html=True)

        # TAB 3 — Contract Score
        with tab3:
            if score_data:
                score = score_data.get("score", 50)
                color = "#52a852" if score >= 70 else "#e09a52" if score >= 40 else "#e05252"
                st.markdown(f'''
                <div class="score-circle">
                    <div class="score-number" style="color:{color}">{score}</div>
                    <div class="score-label">FAIRNESS SCORE / 100</div>
                    <div class="score-verdict">{score_data.get("verdict","")}</div>
                </div>''', unsafe_allow_html=True)
                reasons = score_data.get("reasons", [])
                if reasons:
                    st.markdown("**Why this score?**")
                    for r in reasons:
                        st.markdown(f"› {r}")
            else:
                st.info("Could not generate score.")

        # TAB 4 — Clause Breakdown
        with tab4:
            if not clauses:
                st.info("Could not break down clauses.")
            else:
                for c in clauses:
                    st.markdown(f'''
                    <div class="clause-card">
                        <div class="clause-title">{c.get("title","")}</div>
                        <div class="clause-original">📜 {c.get("original","")}</div>
                        <div class="clause-simple">💬 {c.get("simple","")}</div>
                    </div>''', unsafe_allow_html=True)

        # TAB 5 — Hindi Translation
        with tab5:
            if hindi:
                st.markdown(f'<div class="result-card"><div class="result-label">हिंदी अनुवाद</div><div class="hindi-text">{hindi}</div></div>', unsafe_allow_html=True)
            else:
                st.info("Hindi translation not available.")

        # Download
        if simple:
            risks_text = "\n".join([f"[{r.get('risk_level')}] {r.get('clause')}: {r.get('explanation')}" for r in risks])
            clauses_text = "\n".join([f"{c.get('title')}: {c.get('simple')}" for c in clauses])
            full_output = f"SUMMARY\n{'='*40}\n{summary}\n\nSIMPLE EXPLANATION\n{'='*40}\n{simple}\n\nKEY POINTS\n{'='*40}\n" + "\n".join(f"• {p}" for p in points) + f"\n\nRISKS DETECTED\n{'='*40}\n{risks_text}\n\nCONTRACT SCORE\n{'='*40}\n{score_data.get('score','-')}/100 — {score_data.get('verdict','')}\n\nCLAUSE BREAKDOWN\n{'='*40}\n{clauses_text}"
            if hindi:
                full_output += f"\n\nHINDI TRANSLATION\n{'='*40}\n{hindi}"
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("⬇️ Download Full Report", data=full_output, file_name="legal_analysis_report.txt", mime="text/plain")
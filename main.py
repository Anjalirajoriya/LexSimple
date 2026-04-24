from dotenv import load_dotenv
load_dotenv()
import os

# Works locally (from .env) AND on Streamlit Cloud (from secrets)
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    
import streamlit as st
import PyPDF2
from models.summarizer import generate_summary, translate_to_hindi
from models.simplifier import simplify_text, extract_key_points, detect_risks, score_contract, breakdown_clauses

st.set_page_config(page_title="LexSimple", page_icon="⚖️", layout="centered")

st.markdown("""
<style>
.result-card { background:#f8f8f8; border-radius:10px; padding:1.2rem; margin:0.8rem 0; border:1px solid #e0e0e0; }
.result-label { font-size:0.72rem; text-transform:uppercase; letter-spacing:2px; color:#888; margin-bottom:0.5rem; font-weight:600; }
.result-text { color:#222; line-height:1.7; font-size:0.95rem; }
.risk-high { background:#fff0f0; border-left:4px solid #e24b4a; border-radius:8px; padding:1rem; margin:0.5rem 0; }
.risk-medium { background:#fffbf0; border-left:4px solid #ef9f27; border-radius:8px; padding:1rem; margin:0.5rem 0; }
.risk-low { background:#f0fff4; border-left:4px solid #52a852; border-radius:8px; padding:1rem; margin:0.5rem 0; }
.risk-title { font-weight:600; font-size:0.9rem; margin-bottom:0.3rem; }
.risk-high .risk-title { color:#c0392b; }
.risk-medium .risk-title { color:#e67e22; }
.risk-low .risk-title { color:#27ae60; }
.risk-body { color:#444; font-size:0.85rem; line-height:1.5; }
.score-box { text-align:center; padding:1.5rem; background:#f8f8f8; border-radius:12px; border:1px solid #e0e0e0; margin:1rem 0; }
.score-number { font-size:4rem; font-weight:700; line-height:1; }
.score-verdict { font-size:1rem; color:#555; margin-top:0.8rem; }
.clause-card { background:#f8f8f8; border:1px solid #e0e0e0; border-radius:10px; padding:1rem 1.2rem; margin:0.6rem 0; }
.clause-title { color:#c9a84c; font-size:0.75rem; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.4rem; font-weight:600; }
.clause-original { color:#888; font-size:0.82rem; margin-bottom:0.4rem; font-style:italic; }
.clause-simple { color:#222; font-size:0.9rem; line-height:1.6; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ LexSimple")
st.caption("Paste any legal document — get a plain English explanation instantly.")
st.divider()

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

col1, col2 = st.columns(2)
with col1:
    st.markdown("**📄 Upload a PDF**")
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")
with col2:
    st.markdown("**✍️ Or paste legal text**")
    manual_text = st.text_area("", height=150, placeholder="Paste your legal text here...", label_visibility="collapsed")

text = ""
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success(f"✅ PDF loaded — {len(text)} characters extracted")
elif manual_text.strip():
    text = manual_text.strip()

st.divider()

if st.button("⚡ Analyse Document", type="primary"):
    if not text:
        st.warning("Please paste some text or upload a PDF first.")
    else:
        with st.spinner("Reading document..."): summary = generate_summary(text)
        with st.spinner("Simplifying language..."): simple = simplify_text(text)
        with st.spinner("Extracting key points..."): points = extract_key_points(text)
        with st.spinner("Detecting risks..."): risks = detect_risks(text)
        with st.spinner("Scoring fairness..."): score_data = score_contract(text)
        with st.spinner("Breaking down clauses..."): clauses = breakdown_clauses(text)
        with st.spinner("Translating to Hindi..."): hindi = translate_to_hindi(simple or summary or text)

        st.divider()
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Summary", "⚠️ Risks", "📊 Score", "🔍 Clauses", "🌐 Hindi"])

        with tab1:
            if summary:
                st.markdown(f'<div class="result-card"><div class="result-label">Summary</div><div class="result-text">{summary}</div></div>', unsafe_allow_html=True)
            if simple:
                st.markdown(f'<div class="result-card"><div class="result-label">Plain English</div><div class="result-text">{simple}</div></div>', unsafe_allow_html=True)
            if points:
                pts = "".join([f"<li style='margin-bottom:6px'>{p}</li>" for p in points])
                st.markdown(f'<div class="result-card"><div class="result-label">Key Points</div><ul style="padding-left:1.2rem;color:#222">{pts}</ul></div>', unsafe_allow_html=True)

        with tab2:
            if not risks:
                st.info("No risks detected.")
            else:
                for lvl, label in [("HIGH","🔴 High Risk"), ("MEDIUM","🟠 Medium Risk"), ("LOW","🟢 Low Risk")]:
                    group = [r for r in risks if r.get("risk_level") == lvl]
                    if group:
                        st.markdown(f"**{label} — {len(group)} found**")
                        for r in group:
                            css = f"risk-{lvl.lower()}"
                            st.markdown(f'<div class="{css}"><div class="risk-title">{r.get("clause","")}</div><div class="risk-body">{r.get("explanation","")}</div></div>', unsafe_allow_html=True)

        with tab3:
            if score_data:
                score = score_data.get("score", 50)
                color = "#27ae60" if score >= 70 else "#e67e22" if score >= 40 else "#e74c3c"
                st.markdown(f'<div class="score-box"><div class="score-number" style="color:{color}">{score}</div><div style="font-size:13px;color:#999">out of 100</div><div class="score-verdict">{score_data.get("verdict","")}</div></div>', unsafe_allow_html=True)
                for r in score_data.get("reasons", []):
                    st.markdown(f"› {r}")

        with tab4:
            if not clauses:
                st.info("Could not break down clauses.")
            else:
                for c in clauses:
                    st.markdown(f'<div class="clause-card"><div class="clause-title">{c.get("title","")}</div><div class="clause-original">📜 {c.get("original","")}</div><div class="clause-simple">💬 {c.get("simple","")}</div></div>', unsafe_allow_html=True)

        with tab5:
            if hindi:
                st.markdown(f'<div class="result-card"><div class="result-label">हिंदी अनुवाद</div><div class="result-text" style="font-size:1.05rem;line-height:1.9">{hindi}</div></div>', unsafe_allow_html=True)
            else:
                st.info("Hindi translation not available.")

        if simple:
            risks_text = "\n".join([f"[{r.get('risk_level')}] {r.get('clause')}: {r.get('explanation')}" for r in risks])
            clauses_text = "\n".join([f"{c.get('title')}: {c.get('simple')}" for c in clauses])
            full_output = f"SUMMARY\n{'='*40}\n{summary}\n\nSIMPLE EXPLANATION\n{'='*40}\n{simple}\n\nKEY POINTS\n{'='*40}\n" + "\n".join(f"• {p}" for p in points) + f"\n\nRISKS\n{'='*40}\n{risks_text}\n\nSCORE\n{'='*40}\n{score_data.get('score','-')}/100 — {score_data.get('verdict','')}\n\nCLAUSES\n{'='*40}\n{clauses_text}"
            st.divider()
            st.download_button("⬇️ Download Full Report", data=full_output, file_name="legal_analysis.txt", mime="text/plain")
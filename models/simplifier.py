from groq import Groq
import os
import json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def simplify_text(text):
    text = text[:4000]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""Rewrite the following legal text in plain English so that a non-lawyer can easily understand it.
- Use short, clear sentences.
- Avoid legal jargon and technical words.
- Do not copy phrases from the original text.
- Focus on explaining the meaning and practical effect of each part.
- Write as if you are explaining it to a high school student.
- Keep the explanation concise but complete.

Legal Text:
{text}

Simple Explanation:"""}],
        max_tokens=500,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()


def extract_key_points(text):
    text = text[:4000]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""Extract the most important points from this legal text. Return ONLY a bullet list using "-" for each point. Max 8 points. Plain English only.

Legal Text:
{text}

Key Points:"""}],
        max_tokens=400,
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    points = [line.strip().lstrip("-").strip() for line in raw.split("\n") if line.strip().startswith("-")]
    return points


def detect_risks(text):
    text = text[:4000]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""You are a legal risk analyst. Read this legal document and find RISKY or UNFAIR clauses that could harm the signing party.

For each risk found, respond in this EXACT format (JSON array):
[
  {{
    "risk_level": "HIGH" or "MEDIUM" or "LOW",
    "clause": "short quote or title of the clause",
    "explanation": "why this is risky in simple English"
  }}
]

Return ONLY the JSON array. No extra text.

Legal Text:
{text}"""}],
        max_tokens=600,
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception:
        return []


def score_contract(text):
    text = text[:4000]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""You are a legal fairness expert. Analyze this legal document and give it a FAIRNESS SCORE from 0 to 100.

0 = Very unfair (heavily favors one party)
50 = Neutral
100 = Very fair (balanced for both parties)

Respond in this EXACT JSON format:
{{
  "score": <number 0-100>,
  "verdict": "one line verdict (e.g. Slightly unfair to the Receiving Party)",
  "reasons": ["reason 1", "reason 2", "reason 3"]
}}

Return ONLY the JSON. No extra text.

Legal Text:
{text}"""}],
        max_tokens=400,
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"score": 50, "verdict": "Could not analyze", "reasons": []}


def breakdown_clauses(text):
    text = text[:4000]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""Read this legal document and break it down clause by clause.

For each clause, respond in this EXACT JSON format:
[
  {{
    "title": "Clause name/number",
    "original": "one sentence summary of original clause",
    "simple": "what this means in plain English for a common person"
  }}
]

Return ONLY the JSON array. No extra text. Max 8 clauses.

Legal Text:
{text}"""}],
        max_tokens=800,
        temperature=0.4
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception:
        return []
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_summary(text):
    text = text[:4000]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""You are a legal document expert. Read the following legal text and write a SHORT, CLEAR summary in 3-5 sentences.

Rules:
- Use simple English
- No legal jargon
- Focus on what the agreement/document is about
- Who are the parties involved and what are their main obligations

Legal Text:
{text}

Summary:"""}],
        max_tokens=300,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def translate_to_hindi(text):
    text = text[:3000]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"""Translate the following English legal summary into simple, clear Hindi.
Use everyday Hindi words — avoid difficult legal Hindi terms.
Write in Devanagari script.

English Text:
{text}

Hindi Translation:"""}],
        max_tokens=600,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()
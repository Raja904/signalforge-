import os
from mistralai.client import Mistral
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def _get_api_key():
    try:
        return st.secrets["MISTRAL_API_KEY"]
    except Exception:
        return os.getenv("MISTRAL_API_KEY")

MISTRAL_API_KEY = _get_api_key()
client = Mistral(api_key=MISTRAL_API_KEY)

def call_mistral(prompt, model="mistral-large-latest", is_json=False):
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    if is_json:
        response = client.chat.complete(
            model=model,
            messages=messages,
            response_format={"type": "json_object"}
        )
    else:
        response = client.chat.complete(
            model=model,
            messages=messages
        )
    
    return response.choices[0].message.content

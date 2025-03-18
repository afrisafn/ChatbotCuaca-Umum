
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load variabel dari .env
load_dotenv()

# Ambil API key dari environment atau .env, gunakan None jika tidak ada
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BMKG_API_ENDPOINT = os.getenv("BMKG_API_ENDPOINT")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

DEEPSEEK_API_URL = "https://openrouter.ai/api/v1/chat/completions"


if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah diatur di .env")

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY tidak ditemukan! Pastikan sudah diatur di .env")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")


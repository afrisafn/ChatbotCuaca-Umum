# Modul untuk memproses teks input pengguna sebelum dikirim ke sistem
import re
from datetime import datetime
import json
import requests
from logger_config import logger
from config import gemini_model, DEEPSEEK_API_KEY


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api}"
DEEPSEEK_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def process_prompt_gemini(bmkg_data, user_input):
    """Memilih model AI untuk menjawab pertanyaan berdasarkan input pengguna."""

    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute
    formatted_time = current_time.strftime("%H:%M")
    
    # Tentukan waktu berdasarkan interval
    if 5 <= current_hour < 12:
        time_of_day = "Pagi"
    elif 12 <= current_hour < 15:
        time_of_day = "Siang"
    elif 15 <= current_hour < 18:
        time_of_day = "Sore"
    elif 19 <= current_hour < 22:
        time_of_day = "Malam"
    else:
        time_of_day = "Dini Hari"

    

    prompt = f"""
    
    {bmkg_data}  # Langsung masukkan data tanpa formatting tambahan


    Pertanyaan pengguna:
    {user_input}

    Waktu saat ini: {formatted_time} WIB ({time_of_day}).  
    Jawablah pertanyaan pengguna dengan jelas dan singkat. Sebutkan lokasi, serta berikan saran kegiatan atau pengingat sesuai dengan pertanyaan.  

    Jika pengguna bertanya lebih dari waktu yang ada dalam data BMKG, jawab dengan:  
    "Mohon maaf, data kami hanya menampilkan hingga 3 hari ke depan."  
    Jika pertanyaan tidak terkait BMKG atau wilayah tidak ditemukan, jawab dengan:  
    "Mohon maaf, pertanyaan tidak tersedia dalam data kami. Silakan tanyakan seputar cuaca di Jawa Timur dengan menyebutkan lokasi secara lengkap."
    """
    

    logger.info("Mengirim prompt ke model AI.")
    logger.info(f"Prompt yang dikirim ke Gemini:\n{prompt}")

    logger.info("Mengirim prompt ke model AI.")
    # response = model.generate_content(prompt)
    response = gemini_model.generate_content(prompt)
    # diletakkan debug
    text = response.candidates[0].content.parts[0].text.strip()

    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    return text


def process_prompt_deepseek(bmkg_data, user_message):
    # Konfigurasi API
    OPENROUTER_API_KEY = DEEPSEEK_API_KEY  # Ganti dengan API Key Anda
    # Prompt untuk DeepSeek
    prompt = f"""
    Data cuaca dari BMKG:
    {bmkg_data}

    Pertanyaan pengguna:
    {user_message}

    Jawablah pertanyaan pengguna dengan jelas, singkat, dan berikan saran yang sesuai.
    """
    
    try:
        # Kirim permintaan ke API DeepSeek via OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            })
        )
        
        # Pastikan permintaan berhasil
        response.raise_for_status()
        
        # Parsing respons JSON
        data = response.json()
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "Tidak ada respons.")
        
        answer = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", answer)
        
        return answer
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Gagal menghubungi OpenRouter API (DeepSeek): {e}")
        return f"Error: {str(e)}"
    except KeyError as e:
        logger.error(f"Kesalahan parsing respons OpenRouter API (DeepSeek): {e}")
        return "Kesalahan dalam memproses respons dari OpenRouter API."



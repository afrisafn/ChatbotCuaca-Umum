# Modul utama menangani request informasi cuaca
from utils.location import getName, get_wilayah_code, find_regency_code, format_adm_code
from utils.bmkg_api import getDataBmkg, build_bmkg_url
from utils.text_processing import process_prompt_deepseek, process_prompt_gemini
from logger_config import logger
from flask import jsonify
from datetime import datetime
import re
import json
from config import GEMINI_API_KEY, DEEPSEEK_API_KEY
import google.generativeai as genai
from config import gemini_model, DEEPSEEK_API_KEY
import requests
from flask import request


def process_prompt_gemini(bmkg_data, user_input):
    try:
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
        {bmkg_data}

        Pertanyaan pengguna:
        {user_input}

        Waktu saat ini adalah {formatted_time} WIB ({time_of_day}).
        Jawablah pertanyaan pengguna dengan jelas, singkat, tanpa huruf bold disemua text. sebutkan lokasi lengkap, serta berikan saran kegiatan atau pengingat sesuai keadaan yang terjadi pada pertanyaan.
        -Pukul 05.00-12.00 menunjukkan Pagi
        -Pukul 12.00-15.00 menunjukkan Siang
        -Pukul 15.00-18.00 menunjukkan Sore
        -Pukul 19.00-22.00 menunjukkan Malam
        -Pukul 01.00-05.00 menunjukkan Dini Hari
        Jika pengguna bertanya lebih dari waktu yang ada dalam data BMKG, jawablah dengan "Mohon maaf data kami hanya menampilkan hingga 3 hari kedepan"
        Jika pengguna bertanya terkait waktu jawablah dengan waktu sesuai permintaannya.
        Jika pertanyaan tidak terkait BMKG atau wilayah tidak ditemukan, balas dengan: "Mohon maaf Sobat, pertanyaan tidak tersedia dalam data kami. Silahkan berikan pertanyaan seputar cuaca di daerah Jawa Timur dan sertakan keterangan lokasi daerah lengkap (Desa/Kecamatan/Kabupaten/Kota)".
        Setiap di akhir jawaban tambahkan kata untuk mengakhiri pesan dan terima kasih telah bertanya, lalu sebutkan silahkan bertanya terkait cuaca daerah Jawa Timur kembali! (pisahlah paragrafnya)     
        """
        logger.info("Mengirim prompt ke model AI.")
        # response = model.generate_content(prompt)
        response = gemini_model.generate_content(prompt)
        
        if not response or not hasattr(response, 'candidates') or not response.candidates:
                logger.error("❌ Respons dari Gemini tidak valid atau kosong.")
                return "Mohon maaf, ada kesalahan dalam mendapatkan jawaban dari AI."

        text = response.candidates[0].content.parts[0].text.strip()
        
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        
        return text

    except Exception as e:
        logger.error(f"❌ ERROR saat memproses prompt Gemini: {e}")
        return "Terjadi kesalahan saat memproses AI."
    
def process_prompt_deepseek(bmkg_data, user_input):
    try:
        prompt = f"""
        Data cuaca dari BMKG:
        {bmkg_data}

        Pertanyaan pengguna:
        {user_input}

        Jawablah pertanyaan pengguna dengan jelas, singkat, dan berikan saran yang sesuai.
        """

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            })
        )

        response.raise_for_status()
        data = response.json()
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "Tidak ada respons.")

        answer = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", answer)

        return answer

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Gagal menghubungi OpenRouter API (DeepSeek): {e}")
        return f"Error: {str(e)}"
    except KeyError as e:
        logger.error(f"❌ Kesalahan parsing respons OpenRouter API (DeepSeek): {e}")
        return "Kesalahan dalam memproses respons dari OpenRouter API."


def chat(user_input, model="gemini"):
    try:
        
        # Validasi input model
        if model not in ["gemini", "deepseek", "gpt"]:
            logger.warning("Model tidak dikenali.")
            return {"error": "Model tidak dikenali. Pilih 'gemini', 'deepseek', atau 'gpt'."}
        
        if not user_input:
            logger.warning("Pesan tidak boleh kosong.")
            return jsonify({"error": "Pesan tidak boleh kosong."}), 400
        
        # Mengambil hierarki wilayah dari pesan pengguna
        wilayah_hierarchy = getName(user_input)
        if not wilayah_hierarchy:
            return jsonify({"error": "Wilayah tidak ditemukan dalam pesan Anda."}), 400

        wilayah_level = None
        wilayah_code = None
        

        if wilayah_hierarchy["desa"]:
            wilayah_level = "adm4"
            req_area = getName(user_input)
            logger.info(f"Wilayah yang diminta: {req_area}, file_type: villages")
            wilayah_code = get_wilayah_code("static/data/villages.json", wilayah_hierarchy, "villages")
            logger.info(f"Kode wilayah yang ditemukan: {wilayah_code}")
            bmkg_url = build_bmkg_url(wilayah_level, format_adm_code(wilayah_code))
            bmkg_data = getDataBmkg(bmkg_url)
            
        elif wilayah_hierarchy["kecamatan"]:
            wilayah_level = "adm3"
            req_area = getName(user_input)
            logger.info(f"Wilayah yang diminta: {req_area}, file_type: districts")
            wilayah_code = get_wilayah_code("static/data/districts.json", wilayah_hierarchy, "districts")
            logger.info(f"Kode wilayah yang ditemukan: {wilayah_code}")
            bmkg_url = build_bmkg_url(wilayah_level, format_adm_code(wilayah_code))
            bmkg_data = getDataBmkg(bmkg_url)
        
        elif wilayah_hierarchy["kabupaten"]:
            wilayah_level = "adm2"
            req_area = getName(user_input)
            logger.info(f"Wilayah yang diminta: {req_area}, file_type: regencies")
            wilayah_code = get_wilayah_code("static/data/regencies.json", wilayah_hierarchy, "regencies")
            logger.info(f"Kode wilayah yang ditemukan: {wilayah_code}")
            bmkg_url = build_bmkg_url(wilayah_level, format_adm_code(wilayah_code))
            bmkg_data = getDataBmkg(bmkg_url)
            
        else:
            return jsonify({"error": "Harap sebutkan dan cantumkan kata desa, kecamatan, atau kabupaten dalam pesan Anda."}), 400

        if not wilayah_code:
            return jsonify({"error": "Wilayah tidak ditemukan dalam database."}), 404
        
        if not bmkg_data:
            return jsonify({"error": "Gagal mengambil data dari BMKG."}), 500
        
        logger.info(f"✅ Model AI yang digunakan: {model}")



        # Format prompt sebelum dikirim ke AI
        prompt = f"""
        Data Cuaca dari BMKG:
        {bmkg_data}

        **Pertanyaan Pengguna:**  
        {user_input}

        Gunakan informasi di atas untuk menjawab pertanyaan pengguna secara langsung.
        """

        # Panggil model berdasarkan pilihan pengguna
        if model == "gemini":
            answer = process_prompt_gemini(bmkg_data, user_input)
        elif model == "deepseek":
            answer = process_prompt_deepseek(bmkg_data, user_input)
       
        else:
            logger.warning("Model tidak dikenali.")
            return jsonify({"error": "Model tidak dikenali."}), 400

        # Kembalikan respons
        return jsonify({"response": answer, "model": model})

    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}")
        return jsonify({"error":str(e)}),500
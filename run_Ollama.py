import ollama

MODEL_NAME = "deepseek-r1:1.5b"

chat_history = []

def ask_ollama(user_input):
    """Mengirim pertanyaan ke model Ollama dan menangani respons."""
    global chat_history  
    try:
        chat_history.append({"role": "user", "content": user_input})

        response = ollama.chat(model=MODEL_NAME, messages=chat_history)

        if "message" in response:
            ai_response = response["message"]["content"]
        else:
            ai_response = "⚠️ Tidak ada respons dari model."

        chat_history.append({"role": "assistant", "content": ai_response})

        return ai_response
    except Exception as e:
        return f"⚠️ Terjadi kesalahan: {str(e)}"

if __name__ == "__main__":
    print("🤖 Chatbot DeepSeek-R1:1.5B (Ketik 'exit' untuk keluar)")

    while True:
        user_input = input("\n📝 Masukkan pertanyaan ('exit' untuk keluar): ")

        if user_input.lower() == "exit":
            print("🚪 Keluar dari chatbot.")
            break  

        response = ask_ollama(user_input)
        print("\n🔹 Respon AI:\n")
        print(response)

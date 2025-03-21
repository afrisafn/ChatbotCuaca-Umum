document.addEventListener("DOMContentLoaded", () => {
    function getGreeting() {
        const hour = new Date().getHours();
        if (hour < 10) return "Selamat Pagi";
        if (hour < 14) return "Selamat Siang";
        if (hour < 18) return "Selamat Sore";
        return "Selamat Malam";
    }

    function getEmoji(greeting) {
        if (greeting === "Selamat Pagi") return "🌞";
        if (greeting === "Selamat Siang") return "☀️";
        if (greeting === "Selamat Sore") return "☀️";
        return "🌙";
    }

    const greetingTextElement = document.getElementById("greetingText");
    if (greetingTextElement) {
        const greeting = getGreeting();
        const emoji = getEmoji(greeting);
        greetingTextElement.textContent = `${greeting} ${emoji}`;
    }

    document.getElementById("closeChat").addEventListener("click", function () {
        if (document.referrer) {
            window.history.back();
        } else {
            window.location.href = "hal1.html";
        }
    });

    document.getElementById("send-btn").addEventListener("click", function (event) {
        event.preventDefault();
        sendMessage();
    });

    const chatInput = document.getElementById("chat-input");
    chatInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            document.getElementById("send-btn").click();
        }
    });

    async function sendMessage() {
        const userInput = chatInput.value.trim();
        if (!userInput) return;

        const chatMessages = document.getElementById("chatMessages");
        const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const userMessage = document.createElement("div");
        userMessage.className = "message user-message";
        userMessage.innerHTML = `${userInput} <span style="float: right; font-size: 0.8em; color: gray; margin-left: 8px;">${currentTime}</span>`;
        chatMessages.appendChild(userMessage);

        chatInput.value = "";

        const loadingMessage = document.createElement("div");
        loadingMessage.className = "message bot-message";
        loadingMessage.textContent = "Harap Tunggu...";
        loadingMessage.style.color = "gray";
        chatMessages.appendChild(loadingMessage);

        const modelSelect = document.getElementById("model-select");
        const selectedModel = modelSelect.value;

        try {
            const response = await fetch('/get_cuaca', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_input: userInput, model: selectedModel })
            });

            const data = await response.json();
            console.log("Full Response:", data);
            console.log("Model digunakan:", data?.model);
            chatMessages.removeChild(loadingMessage);

            const botMessage = document.createElement("div");
            botMessage.className = "message bot-message";
            const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            if (response.ok && data?.response) {
                let modelLabel = "";
                if (data?.model === "gemini") {
                    modelLabel = "";
                } else if (data?.model === "deepseek") {
                    modelLabel = "";
                }

                botMessage.innerHTML = `${modelLabel} ${data.response} <span style="float: right; font-size: 0.8em; color: gray; margin-left: 10px;">${botTime}</span>`;
                chatMessages.appendChild(botMessage);

                setTimeout(() => {
                    const autoMessage = document.createElement("div");
                    autoMessage.className = "message bot-message";
                    autoMessage.innerHTML = `Terima kasih, silahkan bertanya kembali terkait informasi cuaca di daerah Jawa Timur! <span style="float: right; font-size: 0.8em; color: gray; margin-left: 10px;">${botTime}</span>`;
                    chatMessages.appendChild(autoMessage);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }, 3000);
            } else {
                botMessage.textContent = "Tidak ada data yang tersedia untuk pertanyaan ini.";
                chatMessages.appendChild(botMessage);
            }
        } catch (error) {
            chatMessages.removeChild(loadingMessage);
            const errorMessage = document.createElement("div");
            errorMessage.className = "message bot-message";
            errorMessage.textContent = `Error: ${error.message}`;
            chatMessages.appendChild(errorMessage);
        }

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

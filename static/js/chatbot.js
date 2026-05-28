document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn   = document.getElementById("chatbot-toggle");
    const closeBtn    = document.getElementById("close-chatbot");
    const windowEl    = document.getElementById("chatbot-window");
    const inputEl     = document.getElementById("chatbot-input");
    const sendBtn     = document.getElementById("chatbot-send");
    const messagesEl  = document.getElementById("chatbot-messages");
    const iconOpen    = document.getElementById("chatbot-icon-open");
    const iconClose   = document.getElementById("chatbot-icon-close");

    const API_KEY     = "AIzaSyAPowpLvVfJW3UhcmHnW7iP4L54DxMDeu0";
    const SYSTEM_MSG  = "Ты дружелюбный ИИ-ассистент платформы Kuraton для университета. Отвечай кратко и понятно. Помогай студентам и кураторам с вопросами об учёбе, посещаемости и платформе.";

    // Conversational history (for context)
    const history = [];

    // ── Toggle ────────────────────────────────────────────────
    toggleBtn.addEventListener("click", () => {
        const isOpen = !windowEl.classList.contains("chat-hidden");
        if (isOpen) {
            windowEl.classList.add("chat-hidden");
            windowEl.classList.remove("chat-visible");
            iconOpen.classList.remove("hidden");
            iconClose.classList.add("hidden");
        } else {
            windowEl.classList.remove("chat-hidden");
            windowEl.classList.add("chat-visible");
            iconOpen.classList.add("hidden");
            iconClose.classList.remove("hidden");
            inputEl.focus();
        }
    });

    closeBtn.addEventListener("click", () => {
        windowEl.classList.add("chat-hidden");
        windowEl.classList.remove("chat-visible");
        iconOpen.classList.remove("hidden");
        iconClose.classList.add("hidden");
    });

    // ── Send ──────────────────────────────────────────────────
    sendBtn.addEventListener("click", sendMessage);
    inputEl.addEventListener("keypress", e => { if (e.key === "Enter") sendMessage(); });

    async function sendMessage() {
        const text = inputEl.value.trim();
        if (!text) return;

        appendMsg(text, "user");
        inputEl.value = "";

        const loadingId = "load-" + Date.now();
        appendMsg("...", "ai", loadingId);

        // Build contents with history
        history.push({ role: "user", parts: [{ text }] });

        try {
            const res = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        contents: [
                            { role: "user", parts: [{ text: SYSTEM_MSG }] },
                            ...history
                        ]
                    })
                }
            );

            const data = await res.json();
            const loader = document.getElementById(loadingId);
            if (loader) loader.remove();

            if (data.candidates?.[0]?.content?.parts?.[0]?.text) {
                const reply = data.candidates[0].content.parts[0].text;
                history.push({ role: "model", parts: [{ text: reply }] });
                appendMsg(reply, "ai");
            } else {
                appendMsg("Не удалось получить ответ. Попробуйте ещё раз.", "ai");
            }
        } catch (err) {
            const loader = document.getElementById(loadingId);
            if (loader) loader.remove();
            appendMsg("Ошибка соединения. Проверьте интернет.", "ai");
        }
    }

    function appendMsg(text, sender, id = null) {
        const div = document.createElement("div");
        if (id) div.id = id;

        if (sender === "user") {
            div.className = "self-end max-w-[80%] text-white text-sm px-3 py-2 rounded-2xl rounded-br-sm shadow-sm";
            div.style.background = "linear-gradient(135deg, #4F46E5, #6366f1)";
        } else {
            div.className = "self-start max-w-[85%] bg-white text-gray-700 text-sm px-3 py-2 rounded-2xl rounded-tl-sm shadow-sm border border-gray-100";
        }

        // Render simple markdown-like: bold, newlines
        div.innerHTML = text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");

        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }
});

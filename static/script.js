const socket = io();
const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const suggestionButtons = document.querySelectorAll(".suggestion-button");

// Thêm tin nhắn vào giao diện
function addMessage(message, sender) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender);
    messageElement.innerText = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Gửi tin nhắn
sendButton.addEventListener("click", () => {
    const message = messageInput.value.trim();
    if (message) {
        addMessage(message, "user");
        socket.emit("send_message", { message });
        messageInput.value = "";
    }
});

// Xử lý khi nhấn các nút gợi ý
suggestionButtons.forEach(button => {
    button.addEventListener("click", () => {
        const message = button.dataset.message;
        addMessage(message, "user");
        socket.emit("send_message", { message });
    });
});

// Nhận tin nhắn từ chatbot
socket.on("receive_message", (data) => {
    addMessage(data.message, "bot");
});

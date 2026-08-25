document.addEventListener("DOMContentLoaded", () => {

    const messageForm = document.getElementById("message-form");
    const messageInput = document.getElementById("message-input");
    const messagesContainer = document.getElementById("messages-container");
    const newChatButton = document.getElementById("new-chat-button");
    const chatTitle = document.getElementById("chat-title");

    const mobileMenuButton =
        document.getElementById("mobile-menu-button");

    const sidebar =
        document.getElementById("sidebar");


    /*
     * =========================================
     * MESSAGE INPUT
     * =========================================
     */

    messageInput.addEventListener("input", () => {

        messageInput.style.height = "auto";

        messageInput.style.height =
            Math.min(messageInput.scrollHeight, 150) + "px";
    });


    /*
     * =========================================
     * SEND MESSAGE
     * =========================================
     *
     * Phase 6:
     * This is mock UI behavior only.
     *
     * Gemini is NOT called.
     * Django API is NOT called.
     */

    messageForm.addEventListener("submit", (event) => {

        event.preventDefault();

        const message =
            messageInput.value.trim();

        if (!message) {
            return;
        }

        addMessage(
            "user",
            message
        );

        messageInput.value = "";

        messageInput.style.height = "auto";


        /*
         * Mock assistant response.
         */

        setTimeout(() => {

            addMessage(
                "assistant",
                "This is a mock response. Gemini will be connected in a later phase."
            );

        }, 500);

    });


    /*
     * =========================================
     * ADD MESSAGE TO UI
     * =========================================
     */

    function addMessage(role, text) {

        const messageElement =
            document.createElement("div");

        messageElement.className =
            role === "user"
                ? "message user-message"
                : "message assistant-message";


        const avatar =
            document.createElement("div");

        avatar.className =
            "message-avatar";

        avatar.textContent =
            role === "user"
                ? "You"
                : "AI";


        const content =
            document.createElement("div");

        content.className =
            "message-content";


        const roleElement =
            document.createElement("div");

        roleElement.className =
            "message-role";

        roleElement.textContent =
            role === "user"
                ? "You"
                : "Assistant";


        const textElement =
            document.createElement("div");

        textElement.className =
            "message-text";

        textElement.textContent =
            text;


        content.appendChild(roleElement);
        content.appendChild(textElement);

        messageElement.appendChild(avatar);
        messageElement.appendChild(content);

        messagesContainer.appendChild(messageElement);


        /*
         * Scroll to newest message.
         */

        messagesContainer.scrollTop =
            messagesContainer.scrollHeight;
    }


    /*
     * =========================================
     * NEW CHAT
     * =========================================
     */

    newChatButton.addEventListener("click", () => {

        messagesContainer.innerHTML = "";

        chatTitle.textContent = "New Chat";

        messageInput.value = "";

        messageInput.focus();

    });


    /*
     * =========================================
     * CHAT HISTORY
     * =========================================
     */

    const historyItems =
        document.querySelectorAll(".history-item");

    historyItems.forEach((item) => {

        item.addEventListener("click", () => {

            historyItems.forEach((historyItem) => {
                historyItem.classList.remove("active");
            });

            item.classList.add("active");

            chatTitle.textContent =
                item.textContent.trim();

            /*
             * Mock behavior only.
             *
             * Real ChatThread data will be
             * connected in a later phase.
             */
        });

    });


    /*
     * =========================================
     * MOBILE SIDEBAR
     * =========================================
     */

    mobileMenuButton.addEventListener("click", () => {

        sidebar.classList.toggle("open");

    });

});

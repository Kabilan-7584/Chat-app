document.addEventListener("DOMContentLoaded", () => {

    const app =
        document.getElementById("chat-app");

    const messageForm =
        document.getElementById("message-form");

    const messageInput =
        document.getElementById("message-input");

    const sendButton =
        document.getElementById("send-button");

    const messagesContainer =
        document.getElementById("messages-container");

    const newChatButton =
        document.getElementById("new-chat-button");

    const chatTitle =
        document.getElementById("chat-title");

    const chatHistoryList =
        document.getElementById("chat-history-list");

    const mobileMenuButton =
        document.getElementById("mobile-menu-button");

    const sidebar =
        document.getElementById("sidebar");

    const inputStatus =
        document.getElementById("input-status");


    let currentThreadId =
        app.dataset.currentThreadId;

    let sendUrlTemplate =
        app.dataset.sendUrlTemplate;

    const createThreadUrl =
        app.dataset.createThreadUrl;


    /*
     * =========================================
     * CSRF
     * =========================================
     */

    function getCsrfToken() {

        const csrfInput =
            messageForm.querySelector(
                'input[name="csrfmiddlewaretoken"]'
            );

        if (csrfInput) {
            return csrfInput.value;
        }

        return "";
    }


    /*
     * =========================================
     * AUTO RESIZE TEXTAREA
     * =========================================
     */

    messageInput.addEventListener(
        "input",
        () => {

            messageInput.style.height =
                "auto";

            messageInput.style.height =
                Math.min(
                    messageInput.scrollHeight,
                    150
                ) + "px";

        }
    );


    /*
     * =========================================
     * SEND MESSAGE
     * =========================================
     */

    messageForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const message =
                messageInput.value.trim();


            if (!message) {

                showStatus(
                    "Please enter a message.",
                    "error"
                );

                return;
            }


            if (message.length > 10000) {

                showStatus(
                    "Message cannot exceed 10,000 characters.",
                    "error"
                );

                return;
            }


            if (!currentThreadId) {

                showStatus(
                    "Please create a chat first.",
                    "error"
                );

                return;
            }


            addMessage(
                "user",
                message
            );


            messageInput.value = "";

            messageInput.style.height =
                "auto";


            setLoadingState(true);


            try {

                const response =
                    await fetch(
                        sendUrlTemplate,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "X-CSRFToken":
                                    getCsrfToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest",
                            },

                            body: JSON.stringify({
                                message: message,
                            }),
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        "Unable to send message."
                    );

                }


                if (!data.success) {

                    throw new Error(
                        data.error ||
                        "Unable to generate response."
                    );

                }


                addMessage(
                    "assistant",
                    data.message.content
                );


                showStatus(
                    "Powered by Google Gemini.",
                    "success"
                );


            } catch (error) {

                showStatus(
                    error.message ||
                    "Something went wrong.",
                    "error"
                );

            } finally {

                setLoadingState(false);

            }

        }
    );


    /*
     * =========================================
     * LOADING STATE
     * =========================================
     */

    function setLoadingState(isLoading) {

        sendButton.disabled =
            isLoading;

        messageInput.disabled =
            isLoading;


        if (isLoading) {

            sendButton.textContent =
                "Sending...";

            showStatus(
                "Gemini is generating a response...",
                "loading"
            );

        } else {

            sendButton.textContent =
                "Send";

        }

    }


    /*
     * =========================================
     * ADD MESSAGE
     * =========================================
     */

    function addMessage(
        role,
        text
    ) {

        const emptyMessage =
            document.getElementById(
                "empty-chat-message"
            );


        if (emptyMessage) {
            emptyMessage.remove();
        }


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

        /*
         * textContent is intentionally used.
         *
         * This prevents HTML injection.
         */

        textElement.textContent =
            text;


        content.appendChild(
            roleElement
        );

        content.appendChild(
            textElement
        );


        messageElement.appendChild(
            avatar
        );

        messageElement.appendChild(
            content
        );


        messagesContainer.appendChild(
            messageElement
        );


        messagesContainer.scrollTop =
            messagesContainer.scrollHeight;

    }


    /*
     * =========================================
     * NEW CHAT
     * =========================================
     */

    newChatButton.addEventListener(
        "click",
        async () => {

            try {

                newChatButton.disabled =
                    true;

                newChatButton.textContent =
                    "Creating...";


                const response =
                    await fetch(
                        createThreadUrl,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCsrfToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest",
                            },
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        "Unable to create chat."
                    );

                }


                currentThreadId =
                    data.thread.id;


                sendUrlTemplate =
                    `/chat/${currentThreadId}/message/`;


                chatTitle.textContent =
                    data.thread.title;


                messagesContainer.innerHTML = "";


                addEmptyChatMessage();


                addHistoryItem(
                    data.thread.id,
                    data.thread.title
                );


                messageInput.focus();


                showStatus(
                    "New chat created.",
                    "success"
                );


            } catch (error) {

                showStatus(
                    error.message ||
                    "Unable to create chat.",
                    "error"
                );

            } finally {

                newChatButton.disabled =
                    false;

                newChatButton.textContent =
                    "+ New Chat";

            }

        }
    );


    /*
     * =========================================
     * ADD HISTORY ITEM
     * =========================================
     */

    function addHistoryItem(
        threadId,
        title
    ) {

        const button =
            document.createElement("button");

        button.className =
            "history-item active";

        button.type =
            "button";

        button.dataset.threadId =
            threadId;

        button.dataset.threadTitle =
            title;

        button.textContent =
            title;


        const existingItems =
            document.querySelectorAll(
                ".history-item"
            );

        existingItems.forEach(
            (item) => {
                item.classList.remove(
                    "active"
                );
            }
        );


        button.addEventListener(
            "click",
            () => {
                switchThread(
                    threadId,
                    title
                );
            }
        );


        chatHistoryList.prepend(
            button
        );

    }


    /*
     * =========================================
     * HISTORY CLICK
     * =========================================
     */

    document
        .querySelectorAll(".history-item")
        .forEach(
            (item) => {

                item.addEventListener(
                    "click",
                    () => {

                        switchThread(
                            item.dataset.threadId,
                            item.dataset.threadTitle
                        );

                    }
                );

            }
        );


    /*
     * =========================================
     * SWITCH THREAD
     * =========================================
     *
     * Phase 7 deliberately does not load
     * previous messages yet.
     *
     * Conversation history API will be
     * implemented with conversation memory
     * in a later phase.
     */

    function switchThread(
        threadId,
        title
    ) {

        currentThreadId =
            threadId;

        sendUrlTemplate =
            `/chat/${threadId}/message/`;


        chatTitle.textContent =
            title;


        document
            .querySelectorAll(".history-item")
            .forEach(
                (item) => {

                    item.classList.remove(
                        "active"
                    );

                }
            );


        const selected =
            document.querySelector(
                `.history-item[data-thread-id="${threadId}"]`
            );


        if (selected) {

            selected.classList.add(
                "active"
            );

        }


        /*
         * We intentionally clear the visible
         * messages because message-history
         * loading is outside Phase 7.
         */

        messagesContainer.innerHTML = "";

        addEmptyChatMessage();


        if (window.innerWidth <= 768) {
            sidebar.classList.remove(
                "open"
            );
        }

    }


    /*
     * =========================================
     * EMPTY CHAT
     * =========================================
     */

    function addEmptyChatMessage() {

        const empty =
            document.createElement("div");

        empty.className =
            "empty-chat-message";

        empty.id =
            "empty-chat-message";


        empty.innerHTML = `
            <div class="empty-chat-icon">
                AI
            </div>

            <h3>
                How can I help you?
            </h3>

            <p>
                Ask me anything and Gemini will
                generate a response.
            </p>
        `;


        messagesContainer.appendChild(
            empty
        );

    }


    /*
     * =========================================
     * STATUS
     * =========================================
     */

    function showStatus(
        message,
        type
    ) {

        inputStatus.textContent =
            message;


        inputStatus.classList.remove(
            "status-error",
            "status-loading",
            "status-success"
        );


        if (type === "error") {

            inputStatus.classList.add(
                "status-error"
            );

        }

        if (type === "loading") {

            inputStatus.classList.add(
                "status-loading"
            );

        }

        if (type === "success") {

            inputStatus.classList.add(
                "status-success"
            );

        }

    }


    /*
     * =========================================
     * MOBILE SIDEBAR
     * =========================================
     */

    mobileMenuButton.addEventListener(
        "click",
        () => {

            sidebar.classList.toggle(
                "open"
            );

        }
    );

});

let controlSocket = null;

function connectControlWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.host}/ws/control`;

    controlSocket = new WebSocket(wsUrl);

    controlSocket.onopen = function () {
        console.log("Connected to control WebSocket");
        document.getElementById("ws-status").textContent = "WebSocket: connected";
    };

    controlSocket.onmessage = function (event) {
        console.log("Message from server:", event.data);
        document.getElementById("last-command").textContent = event.data;
    };

    controlSocket.onclose = function () {
        console.log("Control WebSocket disconnected");
        document.getElementById("ws-status").textContent = "WebSocket: disconnected";
    };

    controlSocket.onerror = function (error) {
        console.error("WebSocket error:", error);
        document.getElementById("ws-status").textContent = "WebSocket: error";
    };
}

function sendCommand(command) {
    if (!controlSocket || controlSocket.readyState !== WebSocket.OPEN) {
        document.getElementById("last-command").textContent =
            "WebSocket is not connected";
        return;
    }

    controlSocket.send(command);
}

async function loginUser() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password
            })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById("message").textContent =
                "Login successful";

            document.getElementById("login-card")
                .classList.add("hidden");

            document.getElementById("dashboard")
                .classList.remove("hidden");

            connectControlWebSocket();

        } else {
            document.getElementById("message").textContent =
                data.detail;
        }

    } catch (error) {
        console.error(error);

        document.getElementById("message").textContent =
            "Connection error";
    }
}

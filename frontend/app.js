let controlSocket = null;
let roverStatusInterval = null;

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

        try {
            const data = JSON.parse(event.data);
            document.getElementById("last-command").textContent =
                JSON.stringify(data, null, 2);
        } catch {
            document.getElementById("last-command").textContent = event.data;
        }
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

    controlSocket.send(JSON.stringify(command));
}
function moveForward() {
    sendCommand({
        type: "drive",
        roverX: 512,
        roverY: 1023,
        roverSW: false
    });
}

function moveBackward() {
    sendCommand({
        type: "drive",
        roverX: 512,
        roverY: 0,
        roverSW: false
    });
}

function turnLeft() {
    sendCommand({
        type: "drive",
        roverX: 0,
        roverY: 512,
        roverSW: false
    });
}

function turnRight() {
    sendCommand({
        type: "drive",
        roverX: 1023,
        roverY: 512,
        roverSW: false
    });
}

function stopRover() {
    sendCommand({
        type: "stop"
    });
}

function toggleAutonomous() {
    sendCommand({
        type: "drive",
        roverX: 512,
        roverY: 512,
        roverSW: true
    });
}

function moveArmLeft() {
    sendCommand({
        type: "arm",
        armX: 0,
        armY: 512,
        armSW: false
    });
}

function moveArmRight() {
    sendCommand({
        type: "arm",
        armX: 1023,
        armY: 512,
        armSW: false
    });
}

function moveArmForward() {
    sendCommand({
        type: "arm",
        armX: 512,
        armY: 1023,
        armSW: false
    });
}

function moveArmBackward() {
    sendCommand({
        type: "arm",
        armX: 512,
        armY: 0,
        armSW: false
    });
}

function toggleWrist() {
    sendCommand({
        type: "arm",
        armX: 512,
        armY: 512,
        armSW: true
    });
}

async function updateRoverStatus() {
    try {
        const response = await fetch("/api/rover/status");
        const data = await response.json();

        const statusText = data.connected
            ? `Rover: ONLINE (${data.status})`
            : "Rover: OFFLINE";

        document.getElementById("rover-status").textContent = statusText;
        document.getElementById("rover-device").textContent =
            `Device: ${data.device || "unknown"}`;

        document.getElementById("rover-last-seen").textContent =
            data.seconds_since_last_seen === null
                ? "Last seen: never"
                : `Last seen: ${data.seconds_since_last_seen}s ago`;

    } catch (error) {
        console.error(error);
        document.getElementById("rover-status").textContent =
            "Rover: status API error";
    }
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

            document.getElementById("login-card").classList.add("hidden");
            document.getElementById("dashboard").classList.remove("hidden");

            connectControlWebSocket();
            updateRoverStatus();

            roverStatusInterval = setInterval(updateRoverStatus, 3000);

        } else {
            document.getElementById("message").textContent = data.detail;
        }

    } catch (error) {
        console.error(error);
        document.getElementById("message").textContent =
            "Connection error";
    }
}

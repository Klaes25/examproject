async function loadBackendStatus() {
    try {
        const response = await fetch("http://localhost:18765");
        const data = await response.json();

        document.querySelector("h1").textContent = data.message;
    } catch (error) {
        console.error(error);

        document.querySelector("h1").textContent =
            "Could not connect to backend";
    }
}

loadBackendStatus();

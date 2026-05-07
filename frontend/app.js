async function registerUser() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/register", {
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

        document.getElementById("message").textContent =
            data.message || data.detail;

    } catch (error) {
        console.error(error);

        document.getElementById("message").textContent =
            "Register failed";
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
                data.message;

            document.getElementById("dashboard")
                .classList.remove("hidden");

        } else {
            document.getElementById("message").textContent =
                data.detail;
        }

    } catch (error) {
        console.error(error);

        document.getElementById("message").textContent =
            "Login failed";
    }
}

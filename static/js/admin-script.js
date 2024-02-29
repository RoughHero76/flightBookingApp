// Define the showMessage function
function showMessage(message, isError) {
    const messageElement = document.getElementById("message");
    messageElement.textContent = message;
    messageElement.style.color = isError ? "red" : "green";
    messageElement.style.display = "block"; // Ensure the message is visible
}

document.getElementById("loginForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/login/admin", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });

    const data = await response.json();
    if (response.ok) {
        // Authentication successful
        window.location.href = "/admin_dashboard?token=" + data.token;
        localStorage.setItem("token", data.token);
    } else {
        // Authentication failed
        if (data.error) {
            showMessage(data.error, true);
        } else {
            showMessage("An error occurred. Please try again later.", true);
        }
    }
});
function getCSRFToken() {
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith("csrftoken=")) {
            //Added by Matthew/Spooky: Return CSRF token for Django POST requests.
            return decodeURIComponent(cookie.substring("csrftoken=".length));
        }
    }
    //Added by Matthew/Spooky: CSRF token not found.
    return null;
}

async function apiRequest(url, method = "GET", data = null) {
    //Added by Matthew/Spooky: Generic API request with CSRF token.
    const options = {
        method: method,
        headers: {
            "X-CSRFToken": getCSRFToken()
        }
    };

    if (data instanceof FormData) {
        //Added by Matthew/Spooky: Send FormData as body without Content-Type header.
        options.body = data;
    }
    else if (data) {
        //Added by Matthew/Spooky: JSON data handling.
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
        //Added by Matthew/Spooky: Error if request failed.
        throw new Error("API request failed");
    }
    //Added by Matthew/Spooky: Parse JSON response.
    return response.json();
}

document.addEventListener("DOMContentLoaded", () => {
    const deleteButtons = document.querySelectorAll(".feedback-actions form button");

    deleteButtons.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const form = btn.closest("form");
            const action = form.getAttribute("action");

            if (!confirm("Are you sure you want to delete this feedback?")) return;

            try {
                await apiRequest(action, "POST", new FormData(form));
                form.closest(".feedback-item").remove();
            } catch (err) {
                alert("Failed to delete feedback.");
                console.error(err);
            }
        });
    });
});
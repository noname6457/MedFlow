
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    const message = document.getElementById("auth-message");
    const submitButton = form.querySelector(
        "button[type='submit']"
    );

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = form.elements["username"].value.trim();
        const password = form.elements["password"].value;

        message.textContent = "";
        message.className = "auth-message";

        submitButton.disabled = true;
        submitButton.textContent = "Выполняем вход...";

        try {
            const { response, data } = await MedFlowAPI.request(
                "/api/auth/login/",
                {
                    method: "POST",
                    body: JSON.stringify({
                        username,
                        password
                    })
                }
            );

            if (!response.ok) {
                throw new Error(
                    data?.error || "Не удалось выполнить вход."
                );
            }

            message.textContent = "Вход выполнен!";
            message.classList.add("success");

            // Возвращаемся на страницу, с которой
            // пользователь перешёл к авторизации.
            const params = new URLSearchParams(
                window.location.search
            );

            const next = params.get("next");

            const safeNext =
                next &&
                next.startsWith("/") &&
                !next.startsWith("//") &&
                !next.startsWith("/\\");

            window.location.assign(
                safeNext ? next : "/"
            );

        } catch (error) {
            message.textContent = error.message;
            message.classList.add("error");

            submitButton.disabled = false;
            submitButton.textContent = "Войти";
        }
    });
});

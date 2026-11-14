
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("register-form");
    const message = document.getElementById("auth-message");
    const submitButton = form.querySelector(
        "button[type='submit']"
    );

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const firstName = form.elements["first_name"].value.trim();
        const lastName = form.elements["last_name"].value.trim();
        const username = form.elements["username"].value.trim();
        const email = form.elements["email"].value.trim();

        const password = form.elements["password"].value;
        const passwordConfirm =
            form.elements["password_confirm"].value;

        message.textContent = "";
        message.className = "auth-message";

        if (password !== passwordConfirm) {
            message.textContent = "Пароли не совпадают.";
            message.classList.add("error");
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = "Создаём аккаунт...";

        try {
            const { response, data } = await MedFlowAPI.request(
                "/api/auth/register/",
                {
                    method: "POST",
                    body: JSON.stringify({
                        first_name: firstName,
                        last_name: lastName,
                        username,
                        email,
                        password
                    })
                }
            );

            if (!response.ok) {
                const errors = [];

                if (data && typeof data === "object") {
                    for (const [field, messages] of Object.entries(data)) {
                        const value = Array.isArray(messages)
                            ? messages.join(", ")
                            : String(messages);

                        errors.push(`${field}: ${value}`);
                    }
                }

                throw new Error(
                    errors.join("; ") ||
                    "Не удалось создать аккаунт."
                );
            }

            message.textContent =
                "Регистрация успешна! Переходим ко входу.";
            message.classList.add("success");

            window.location.assign("/login/");

        } catch (error) {
            message.textContent = error.message;
            message.classList.add("error");

            submitButton.disabled = false;
            submitButton.textContent = "Зарегистрироваться";
        }
    });
});

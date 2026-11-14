
document.addEventListener("DOMContentLoaded", async () => {
    const guestActions = document.getElementById("guest-actions");
    const userActions = document.getElementById("user-actions");
    const usernameElement = document.getElementById("header-username");
    const logoutButton = document.getElementById("logout-button");

    try {
        const { response, data } = await MedFlowAPI.request(
            "/api/auth/me/"
        );

        if (response.ok) {
            usernameElement.textContent =
                data.first_name || data.username;

            userActions.hidden = false;
            guestActions.hidden = true;
        } else {
            guestActions.hidden = false;
            userActions.hidden = true;
        }

    } catch (error) {
        console.error("Ошибка проверки авторизации:", error);
        guestActions.hidden = false;
        userActions.hidden = true;
    }

    logoutButton.addEventListener("click", async () => {
        logoutButton.disabled = true;

        try {
            const { response } = await MedFlowAPI.request(
                "/api/auth/logout/",
                {
                    method: "POST",
                    body: JSON.stringify({})
                }
            );

            if (!response.ok) {
                throw new Error("Не удалось выйти из аккаунта");
            }

            window.location.assign("/");

        } catch (error) {
            console.error(error);
            alert("Ошибка выхода. Попробуйте ещё раз.");
            logoutButton.disabled = false;
        }
    });
});

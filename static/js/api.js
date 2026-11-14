
const MedFlowAPI = {
    getCookie(name) {
        const cookies = document.cookie.split(";");

        for (const item of cookies) {
            const cookie = item.trim();
            const prefix = `${name}=`;

            if (cookie.startsWith(prefix)) {
                return decodeURIComponent(
                    cookie.slice(prefix.length)
                );
            }
        }

        return null;
    },

    async request(url, options = {}) {
        const method = (options.method || "GET").toUpperCase();
        const headers = new Headers(options.headers || {});

        // При необходимости инициализируем CSRF-cookie.
        if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
            if (!this.getCookie("csrftoken")) {
                await fetch("/api/auth/me/", {
                    credentials: "same-origin"
                });
            }

            const token = this.getCookie("csrftoken");

            if (token) {
                headers.set("X-CSRFToken", token);
            }
        }

        if (options.body && !headers.has("Content-Type")) {
            headers.set("Content-Type", "application/json");
        }

        const response = await fetch(url, {
            ...options,
            method,
            headers,
            credentials: "same-origin"
        });

        let data = null;

        if (response.status !== 204) {
            const contentType =
                response.headers.get("content-type") || "";

            if (contentType.includes("application/json")) {
                data = await response.json();
            }
        }

        return { response, data };
    }
};

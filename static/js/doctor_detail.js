
document.addEventListener("DOMContentLoaded", () => {
    const bookingApp = document.getElementById("booking-app");
    const doctorId = bookingApp.dataset.doctorId;

    const form = document.getElementById("booking-form");
    const dateInput = document.getElementById("appointment-date");
    const slotsContainer = document.getElementById("slots-container");
    const message = document.getElementById("booking-message");
    const bookButton = document.getElementById("book-button");

    const csrfToken = form.querySelector(
        "[name=csrfmiddlewaretoken]"
    ).value;

    let selectedSlot = null;
    let availableSlots = [];
    let loadingController = null;
    let bookingInProgress = false;

    // Получаем сегодняшнюю дату в часовом поясе браузера.
    function getToday() {
        const today = new Date();

        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    }

    function showMessage(text, type = "info") {
        message.textContent = text;
        message.className = `booking-message ${type}`;
    }

    function formatTime(dateString) {
        return new Intl.DateTimeFormat("ru-RU", {
            hour: "2-digit",
            minute: "2-digit"
        }).format(new Date(dateString));
    }

    function resetSelection() {
        selectedSlot = null;
        bookButton.disabled = true;
    }

    function renderSlots(slots) {
        slotsContainer.replaceChildren();
        resetSelection();

        if (slots.length === 0) {
            showMessage(
                "На выбранную дату свободного времени нет."
            );
            return;
        }

        showMessage("Выберите подходящее время.");

        slots.forEach((slot) => {
            const button = document.createElement("button");

            button.type = "button";
            button.className = "slot-button";

            button.textContent =
                `${formatTime(slot.start_at)} – ${formatTime(slot.end_at)}`;

            button.addEventListener("click", () => {
                if (bookingInProgress) {
                    return;
                }

                selectedSlot = slot;

                document
                    .querySelectorAll(".slot-button")
                    .forEach((item) => {
                        item.classList.remove("selected");
                    });

                button.classList.add("selected");
                bookButton.disabled = false;

                showMessage(
                    `Выбрано время: ${formatTime(slot.start_at)}`
                );
            });

            slotsContainer.appendChild(button);
        });
    }

    async function loadSlots() {
        if (loadingController) {
            loadingController.abort();
        }

        const controller = new AbortController();
        loadingController = controller;

        resetSelection();
        availableSlots = [];
        slotsContainer.replaceChildren();

        showMessage("Загружаем свободное время...");

        const date = dateInput.value;

        if (!date) {
            showMessage("Выберите дату.");
            return;
        }

        const url =
            `/api/doctors/${doctorId}/slots/` +
            `?date=${encodeURIComponent(date)}`;

        try {
            const response = await fetch(url, {
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (!Array.isArray(data)) {
                throw new Error("Неожиданный формат API");
            }

            availableSlots = data;
            renderSlots(availableSlots);

        } catch (error) {
            if (error.name === "AbortError") {
                return;
            }

            console.error("Ошибка загрузки:", error);

            showMessage(
                "Не удалось загрузить расписание.",
                "error"
            );

        } finally {
            if (loadingController === controller) {
                loadingController = null;
            }
        }
    }

    async function bookAppointment(event) {
        event.preventDefault();

        if (!selectedSlot || bookingInProgress) {
            return;
        }

        bookingInProgress = true;
        bookButton.disabled = true;

        const slotId = selectedSlot.id;

        showMessage("Записываем на приём...");

        try {
            const response = await fetch(
                `/api/doctors/${doctorId}/slots/${slotId}/book/`,
                {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-CSRFToken": csrfToken
                    }
                }
            );

            if (response.status === 401 ||
                response.status === 403) {

                showMessage(
                    "Для записи необходимо войти в аккаунт.",
                    "error"
                );
                return;
            }

            if (response.status === 409) {
                showMessage(
                    "К сожалению, это время уже занято. " +
                    "Выберите другое.",
                    "error"
                );

                await loadSlots();
                return;
            }

            if (!response.ok) {
                let errorText = "Не удалось создать запись.";

                try {
                    const data = await response.json();
                    errorText = data.error || errorText;
                } catch {
                    // Ответ сервера может не содержать JSON.
                }

                throw new Error(errorText);
            }

            showMessage(
                "Вы успешно записались на приём!",
                "success"
            );

            selectedSlot = null;

            // Убираем забронированный слот из списка.
            availableSlots = availableSlots.filter(
                (slot) => slot.id !== slotId
            );

            // Обновляем кнопки без дополнительного запроса.
            renderSlots(availableSlots);

            showMessage(
                "Запись подтверждена! " +
                "Посмотреть её можно в личном кабинете.",
                "success"
            );

        } catch (error) {
            console.error("Ошибка бронирования:", error);
            showMessage(error.message, "error");

        } finally {
            bookingInProgress = false;
            bookButton.disabled = selectedSlot === null;
        }
    }

    dateInput.min = getToday();
    dateInput.value = getToday();

    dateInput.addEventListener("change", loadSlots);
    form.addEventListener("submit", bookAppointment);

    loadSlots();
});

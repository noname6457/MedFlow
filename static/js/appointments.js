
document.addEventListener("DOMContentLoaded", () => {
    const upcomingContainer = document.getElementById(
        "upcoming-appointments"
    );
    const pastContainer = document.getElementById(
        "past-appointments"
    );
    const message = document.getElementById(
        "appointments-message"
    );

    function formatDate(value) {
        return new Intl.DateTimeFormat("ru-RU", {
            day: "numeric",
            month: "long",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        }).format(new Date(value));
    }

    function createAppointmentCard(appointment, isUpcoming) {
        const card = document.createElement("article");
        card.className = "appointment-card";

        const badge = document.createElement("span");
        badge.className = isUpcoming
            ? "appointment-status upcoming"
            : "appointment-status completed";

        badge.textContent = isUpcoming
            ? "Предстоящий приём"
            : "Прошедший приём";

        const doctor = document.createElement("h3");
        doctor.textContent = appointment.doctor_name;

        const date = document.createElement("p");
        date.className = "appointment-date";
        date.textContent =
            `Дата и время: ${formatDate(appointment.start_at)}`;

        const link = document.createElement("a");
        link.href = `/doctors/${appointment.doctor_id}/`;
        link.className = "btn btn-outline";
        link.textContent = "Страница врача";

        card.append(badge, doctor, date, link);

        if (isUpcoming) {
            const cancelButton = document.createElement("button");

            cancelButton.type = "button";
            cancelButton.className = "btn btn-danger";
            cancelButton.textContent = "Отменить запись";

            cancelButton.addEventListener("click", async () => {
                const confirmed = window.confirm(
                    "Вы уверены, что хотите отменить запись?"
                );

                if (!confirmed) {
                    return;
                }

                cancelButton.disabled = true;

                try {
                    const { response, data } =
                        await MedFlowAPI.request(
                            `/api/appointments/${appointment.id}/`,
                            { method: "DELETE" }
                        );

                    if (!response.ok) {
                        throw new Error(
                            data?.error || "Ошибка отмены записи."
                        );
                    }

                    await loadAppointments();

                } catch (error) {
                    message.textContent = error.message;
                    cancelButton.disabled = false;
                }
            });

            card.appendChild(cancelButton);
        }

        return card;
    }

    function renderAppointments(appointments) {
        upcomingContainer.replaceChildren();
        pastContainer.replaceChildren();

        const now = new Date();

        const upcoming = appointments.filter(
            (item) => new Date(item.start_at) > now
        );

        const past = appointments.filter(
            (item) => new Date(item.start_at) <= now
        );

        upcoming.sort(
            (a, b) =>
                new Date(a.start_at) - new Date(b.start_at)
        );

        past.sort(
            (a, b) =>
                new Date(b.start_at) - new Date(a.start_at)
        );

        upcoming.forEach((appointment) => {
            upcomingContainer.appendChild(
                createAppointmentCard(appointment, true)
            );
        });

        past.forEach((appointment) => {
            pastContainer.appendChild(
                createAppointmentCard(appointment, false)
            );
        });

        if (upcoming.length === 0) {
            const empty = document.createElement("p");
            empty.className = "appointments-empty";
            empty.textContent =
                "У вас пока нет предстоящих приёмов.";

            upcomingContainer.appendChild(empty);
        }

        if (past.length === 0) {
            const empty = document.createElement("p");
            empty.className = "appointments-empty";
            empty.textContent =
                "История приёмов пока пуста.";

            pastContainer.appendChild(empty);
        }

        message.textContent = "";
    }

    async function loadAppointments() {
        message.textContent = "Загружаем записи...";

        try {
            const { response, data } =
                await MedFlowAPI.request(
                    "/api/appointments/"
                );

            if (!response.ok) {
                throw new Error(
                    "Не удалось получить список записей."
                );
            }

            const appointments = Array.isArray(data)
                ? data
                : data?.results;

            if (!Array.isArray(appointments)) {
                throw new Error(
                    "Некорректный формат ответа сервера."
                );
            }

            renderAppointments(appointments);

        } catch (error) {
            console.error(error);
            message.textContent = error.message;
        }
    }

    loadAppointments();
});

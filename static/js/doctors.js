
document.addEventListener("DOMContentLoaded", () => {
    const doctorsGrid = document.getElementById("doctors-grid");
    const doctorsCount = document.getElementById("doctors-count");
    const catalogMessage = document.getElementById("catalog-message");

    const searchInput = document.getElementById("doctor-search");
    const specializationFilter = document.getElementById(
        "specialization-filter"
    );
    const experienceFilter = document.getElementById(
        "experience-filter"
    );
    const resetButton = document.getElementById("reset-filters");

    let searchTimeout;
    let currentController = null;

    function createDoctorCard(doctor) {
        const card = document.createElement("article");
        card.className = "doctor-card";

        const avatar = document.createElement("div");
        avatar.className = "doctor-avatar";

        const initials = `${doctor.first_name?.[0] || ""}${
            doctor.last_name?.[0] || ""
        }`;

        avatar.textContent = initials.toUpperCase();

        const information = document.createElement("div");
        information.className = "doctor-information";

        const specialization = document.createElement("span");
        specialization.className = "doctor-specialization";
        specialization.textContent =
            doctor.specialization_name || "Специалист";

        const name = document.createElement("h3");
        name.textContent = doctor.full_name;

        const experience = document.createElement("p");
        experience.className = "doctor-experience";
        experience.textContent =
            `Стаж работы: ${doctor.experience_years} лет`;

        const description = document.createElement("p");
        description.className = "doctor-description";
        description.textContent =
            doctor.description || "Информация о враче уточняется.";

        const link = document.createElement("a");
        link.className = "btn btn-primary doctor-link";
        link.href = `/doctors/${doctor.id}/`;
        link.textContent = "Подробнее и запись";

        information.append(
            specialization,
            name,
            experience,
            description,
            link
        );

        card.append(avatar, information);

        return card;
    }

    function renderDoctors(doctors) {
        doctorsGrid.replaceChildren();
        catalogMessage.textContent = "";

        doctorsCount.textContent = `Найдено: ${doctors.length}`;

        if (doctors.length === 0) {
            catalogMessage.textContent =
                "По вашему запросу врачи не найдены. " +
                "Попробуйте изменить фильтры.";
            return;
        }

        const fragment = document.createDocumentFragment();

        doctors.forEach((doctor) => {
            fragment.appendChild(createDoctorCard(doctor));
        });

        doctorsGrid.appendChild(fragment);
    }

    function extractDoctors(data) {
        if (Array.isArray(data)) {
            return data;
        }

        if (data && Array.isArray(data.results)) {
            return data.results;
        }

        throw new Error("Неожиданный формат ответа API");
    }

    async function populateSpecializations() {
        try {
            const response = await fetch("/api/doctors/");

            if (!response.ok) {
                throw new Error("Не удалось получить специализации");
            }

            const data = await response.json();
            const doctors = extractDoctors(data);

            const names = [
                ...new Set(
                    doctors
                        .map((doctor) => doctor.specialization_name)
                        .filter(Boolean)
                )
            ].sort((a, b) => a.localeCompare(b, "ru"));

            names.forEach((name) => {
                const option = document.createElement("option");
                option.value = name;
                option.textContent = name;

                specializationFilter.appendChild(option);
            });

        } catch (error) {
            console.error("Ошибка специализаций:", error);
        }
    }

    async function loadDoctors() {
        if (currentController) {
            currentController.abort();
        }

        const controller = new AbortController();
        currentController = controller;

        const params = new URLSearchParams();

        const search = searchInput.value.trim();
        const specialization = specializationFilter.value;
        const experience = experienceFilter.value;

        if (search) {
            params.set("search", search);
        }

        if (specialization) {
            params.set("specialization", specialization);
        }

        if (experience) {
            params.set("min_experience", experience);
        }

        const query = params.toString();
        const url = `/api/doctors/${query ? `?${query}` : ""}`;

        doctorsCount.textContent = "Загрузка...";
        catalogMessage.textContent = "";

        try {
            const response = await fetch(url, {
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            const doctors = extractDoctors(data);

            renderDoctors(doctors);

        } catch (error) {
            if (error.name === "AbortError") {
                return;
            }

            console.error("Ошибка загрузки врачей:", error);

            doctorsGrid.replaceChildren();
            doctorsCount.textContent = "Ошибка";

            catalogMessage.textContent =
                "Не удалось загрузить список врачей. " +
                "Попробуйте обновить страницу.";

        } finally {
            if (currentController === controller) {
                currentController = null;
            }
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(searchTimeout);

        searchTimeout = setTimeout(() => {
            loadDoctors();
        }, 350);
    });

    specializationFilter.addEventListener("change", loadDoctors);
    experienceFilter.addEventListener("change", loadDoctors);

    resetButton.addEventListener("click", () => {
        clearTimeout(searchTimeout);

        searchInput.value = "";
        specializationFilter.value = "";
        experienceFilter.value = "";

        loadDoctors();
    });

    populateSpecializations();
    loadDoctors();
});

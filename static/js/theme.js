(() => {
    const root = document.documentElement;
    const toggle = document.getElementById("themeToggle");
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");

    function applyTheme(theme, save = true) {
        const selectedTheme = theme === "dark" ? "dark" : "light";

        root.setAttribute("data-bs-theme", selectedTheme);

        if (toggle) {
            toggle.textContent = selectedTheme === "dark" ? "☀" : "☾";
            toggle.setAttribute(
                "aria-label",
                selectedTheme === "dark"
                    ? "Switch to light theme"
                    : "Switch to dark theme"
            );
            toggle.setAttribute("aria-pressed", String(selectedTheme === "dark"));
        }

        if (save) {
            try {
                localStorage.setItem("taskflow-theme", selectedTheme);
            } catch (error) {
                // The theme still works for this page if storage is unavailable.
            }
        }
    }

    applyTheme(root.getAttribute("data-bs-theme") || "light", false);

    toggle?.addEventListener("click", () => {
        const currentTheme = root.getAttribute("data-bs-theme");
        applyTheme(currentTheme === "dark" ? "light" : "dark");
    });

    sidebarToggle?.addEventListener("click", () => {
        if (!sidebar) return;

        const isOpen = sidebar.classList.toggle("is-open");
        sidebarToggle.setAttribute("aria-expanded", String(isOpen));
    });

    document.addEventListener("click", (event) => {
        if (!sidebar || !sidebarToggle || window.innerWidth > 900) return;

        const clickedInsideSidebar = sidebar.contains(event.target);
        const clickedToggle = sidebarToggle.contains(event.target);

        if (!clickedInsideSidebar && !clickedToggle) {
            sidebar.classList.remove("is-open");
            sidebarToggle.setAttribute("aria-expanded", "false");
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 900 && sidebar) {
            sidebar.classList.remove("is-open");
            sidebarToggle?.setAttribute("aria-expanded", "false");
        }
    });
})();
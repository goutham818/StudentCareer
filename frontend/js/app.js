// SPA Hash Router
const appRouter = {
    routes: {
        "dashboard": { viewId: "view-dashboard", title: "Dashboard", subtitle: "System Overview", init: () => dashboardModule.loadDashboard() },
        "analytics": { viewId: "view-analytics", title: "Performance Analytics", subtitle: "Detailed Visualization Charts", init: () => analyticsModule.loadAnalytics() },
        "guidance": { viewId: "view-guidance", title: "Career & AI Guidance", subtitle: "Predictive Analytics & Personalized Roadmaps", init: () => careerModule.init() },
        "students": { viewId: "view-students", title: "Student Profiles", subtitle: "Manage Campus Student Directory", init: () => studentsModule.init() },
        "upload": { viewId: "view-upload", title: "Dataset Upload", subtitle: "Admin Dataset Importer & Retraining Controller", init: () => appRouter.resetUploadZone() }
    },

    route() {
        const hash = window.location.hash.replace(/^#\/?/, "") || "dashboard";
        
        // Auth check before displaying
        if (!authService.isAuthenticated()) {
            document.getElementById("app-wrapper").classList.add("hidden");
            document.getElementById("login-wrapper").classList.remove("hidden");
            window.location.hash = "/login";
            return;
        }

        if (hash === "login") {
            // Already logged in, redirect to dashboard
            window.location.hash = "/dashboard";
            return;
        }

        const currentRoute = this.routes[hash];
        if (!currentRoute) {
            window.location.hash = "/dashboard";
            return;
        }

        // Check permissions: Admin only routes
        const role = authService.getUserRole();
        if (role !== "admin" && (hash === "students" || hash === "upload")) {
            showToast("Unauthorized. Administrators only.", "error");
            window.location.hash = "/dashboard";
            return;
        }

        // Hide all views, display the selected one
        document.querySelectorAll(".page-view").forEach(view => view.classList.add("hidden"));
        const targetView = document.getElementById(currentRoute.viewId);
        if (targetView) targetView.classList.remove("hidden");

        // Update Nav Menu highlight
        document.querySelectorAll(".sidebar-nav li").forEach(li => {
            li.classList.remove("active");
            if (li.getAttribute("data-target") === hash) {
                li.classList.add("active");
            }
        });

        // Update Page Headers
        document.getElementById("page-title").textContent = currentRoute.title;
        document.getElementById("page-subtitle").textContent = currentRoute.subtitle;

        // Initialize view component
        if (typeof currentRoute.init === "function") {
            currentRoute.init();
        }
    },

    resetUploadZone() {
        document.getElementById("form-csv-upload").reset();
        document.getElementById("selected-file-badge").classList.add("hidden");
        document.getElementById("btn-upload-submit").disabled = true;
    }
};

// Theme Toggle logic
const themeService = {
    init() {
        const theme = localStorage.getItem("theme") || "dark";
        document.documentElement.setAttribute("data-theme", theme);
        this.updateToggleIcon(theme);
    },

    toggle() {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
        this.updateToggleIcon(next);
        
        // Redraw charts if we are on the analytics page to update colors
        if (window.location.hash.includes("analytics")) {
            analyticsModule.loadAnalytics();
        }
    },

    updateToggleIcon(theme) {
        const btn = document.getElementById("btn-theme-toggle");
        if (!btn) return;
        
        if (theme === "dark") {
            btn.innerHTML = `<i class="fa-solid fa-sun text-amber"></i>`;
        } else {
            btn.innerHTML = `<i class="fa-solid fa-moon"></i>`;
        }
    }
};

// Drag and drop CSV upload zone logic
const uploadZoneService = {
    init() {
        const dropZone = document.getElementById("csv-drag-zone");
        const fileInput = document.getElementById("csv-file-input");
        const form = document.getElementById("form-csv-upload");
        const clearBtn = document.getElementById("btn-clear-file");
        const fileBadge = document.getElementById("selected-file-badge");
        const fileNameSpan = document.getElementById("selected-file-name");
        const submitBtn = document.getElementById("btn-upload-submit");

        if (!dropZone || !fileInput) return;

        // Clicking zone triggers input click
        dropZone.addEventListener("click", () => fileInput.click());

        // Drag events
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropZone.classList.add("dragover");
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropZone.classList.remove("dragover");
            }, false);
        });

        dropZone.addEventListener("drop", (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                this.updateFileSelection(files[0]);
            }
        });

        fileInput.addEventListener("change", (e) => {
            if (fileInput.files.length) {
                this.updateFileSelection(fileInput.files[0]);
            }
        });

        clearBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.value = "";
            fileBadge.classList.add("hidden");
            submitBtn.disabled = true;
        });

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const file = fileInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append("file", file);

            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Uploading & Retraining model...`;

            try {
                const response = await api.post("api/upload-dataset", formData);
                if (response) {
                    showToast(response.message || "CSV dataset uploaded and AI model retrained!", "success");
                    fileInput.value = "";
                    fileBadge.classList.add("hidden");
                }
            } catch (error) {
                console.error("Upload failed:", error);
            } finally {
                submitBtn.disabled = true; // Wait for next file selection
                submitBtn.innerHTML = `<i class="fa-solid fa-upload"></i> Upload & Retrain AI Models`;
            }
        });
    },

    updateFileSelection(file) {
        const fileBadge = document.getElementById("selected-file-badge");
        const fileNameSpan = document.getElementById("selected-file-name");
        const submitBtn = document.getElementById("btn-upload-submit");

        if (file && file.name.endsWith('.csv')) {
            fileNameSpan.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            fileBadge.classList.remove("hidden");
            submitBtn.disabled = false;
        } else {
            showToast("Please select a valid CSV file.", "error");
            fileBadge.classList.add("hidden");
            submitBtn.disabled = true;
        }
    }
};

// Date display
function initDateDisplay() {
    const badge = document.getElementById("current-date-badge");
    if (badge) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        badge.textContent = new Date().toLocaleDateString('en-US', options);
    }
}

// Secret settings to change API Base URL (double click on logo)
function initLogoSettings() {
    const logo = document.querySelector(".sidebar-logo");
    if (logo) {
        logo.addEventListener("dblclick", () => {
            const current = localStorage.getItem("API_BASE_URL") || "http://127.0.0.1:8000";
            const input = prompt("Settings: Edit Backend API URL:", current);
            if (input !== null) {
                const trimmed = input.trim();
                if (trimmed) {
                    localStorage.setItem("API_BASE_URL", trimmed);
                    showToast(`Backend URL set to: ${trimmed}. Page reloading...`, "success");
                    setTimeout(() => window.location.reload(), 1500);
                }
            }
        });
    }
}

// Bootstrapping App
document.addEventListener("DOMContentLoaded", () => {
    themeService.init();
    initDateDisplay();
    uploadZoneService.init();
    initLogoSettings();

    // Bind theme toggle button
    document.getElementById("btn-theme-toggle").addEventListener("click", () => {
        themeService.toggle();
    });

    // Listen to hash change router triggers
    window.addEventListener("hashchange", () => appRouter.route());

    // Navigation links binding
    document.querySelectorAll(".sidebar-nav li").forEach(li => {
        li.addEventListener("click", function() {
            document.querySelectorAll(".sidebar-nav li").forEach(item => item.classList.remove("active"));
            this.classList.add("active");
        });
    });

    // Load initial user session on startup
    authService.initSession();
});

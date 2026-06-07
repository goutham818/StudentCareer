// Dynamic backend URL resolver
let API_BASE_URL = localStorage.getItem("API_BASE_URL");

if (!API_BASE_URL) {
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        API_BASE_URL = "http://127.0.0.1:8000";
    } else {
        // Fallback for production. Users can update this by clicking the logo in the sidebar
        API_BASE_URL = "https://goutham818-studentcareer-backend.hf.space"; 
    }
    localStorage.setItem("API_BASE_URL", API_BASE_URL);
}

// Toast Notifications Helper
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let iconClass = "fa-circle-info";
    if (type === "success") iconClass = "fa-circle-check";
    if (type === "error") iconClass = "fa-triangle-exclamation";

    toast.innerHTML = `
        <i class="fa-solid ${iconClass} toast-icon"></i>
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
    `;

    container.appendChild(toast);

    // Slide in
    setTimeout(() => {
        toast.classList.add("show");
    }, 10);

    // Auto remove
    const autoClose = setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 350);
    }, 4000);

    // Close on click
    toast.querySelector(".toast-close").addEventListener("click", () => {
        clearTimeout(autoClose);
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 350);
    });
}

// Global API Fetch wrapper
const api = {
    async request(endpoint, options = {}) {
        const token = localStorage.getItem("access_token");
        const headers = {
            ...(options.headers || {})
        };

        if (token && !options.noAuth) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        // Handle JSON payloads
        if (options.body && !(options.body instanceof FormData) && typeof options.body === "object") {
            headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(options.body);
        }

        const url = `${API_BASE_URL.replace(/\/$/, "")}/${endpoint.replace(/^\//, "")}`;
        
        try {
            const response = await fetch(url, { ...options, headers });
            
            if (response.status === 401) {
                // Auto logout on unauthorized token expiration
                localStorage.removeItem("access_token");
                localStorage.removeItem("user_role");
                localStorage.removeItem("username");
                showToast("Session expired. Please log in again.", "error");
                
                // Show login view
                document.getElementById("app-wrapper").classList.add("hidden");
                document.getElementById("login-wrapper").classList.remove("hidden");
                return null;
            }

            if (response.status === 204) {
                return true;
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `Request failed with status ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error("API Request Error:", error);
            showToast(error.message || "Network connection failure. Verify backend status.", "error");
            throw error;
        }
    },

    get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: "GET" });
    },

    post(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: "POST", body });
    },

    put(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: "PUT", body });
    },

    delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: "DELETE" });
    }
};

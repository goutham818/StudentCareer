const authService = {
    isAuthenticated() {
        return !!localStorage.getItem("access_token");
    },

    getUserRole() {
        return localStorage.getItem("user_role");
    },

    getUsername() {
        return localStorage.getItem("username");
    },

    async login(username, password) {
        try {
            const data = await api.post("api/auth/login", { username, password }, { noAuth: true });
            if (data && data.access_token) {
                localStorage.setItem("access_token", data.access_token);
                localStorage.setItem("user_role", data.role);
                localStorage.setItem("username", data.username);
                
                showToast(`Logged in successfully as ${data.username}`, "success");
                
                // Transition to dashboard view
                await this.initSession();
                return true;
            }
        } catch (error) {
            console.error("Login failed:", error);
        }
        return false;
    },

    logout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_role");
        localStorage.removeItem("username");
        
        showToast("Logged out successfully.", "info");
        
        document.getElementById("app-wrapper").classList.add("hidden");
        document.getElementById("login-wrapper").classList.remove("hidden");
        
        // Reset URL hash to login
        window.location.hash = "/login";
    },

    async initSession() {
        if (!this.isAuthenticated()) {
            document.getElementById("app-wrapper").classList.add("hidden");
            document.getElementById("login-wrapper").classList.remove("hidden");
            return;
        }

        const username = this.getUsername();
        const role = this.getUserRole();

        // Update UI displays
        document.getElementById("user-display-name").textContent = username.toUpperCase();
        document.getElementById("user-display-role").textContent = role === "admin" ? "Administrator" : "Student Profile";
        document.getElementById("user-avatar-initials").textContent = username.substring(0, 2).toUpperCase();

        // Show/hide menu items based on role
        const adminElements = document.querySelectorAll(".admin-only");
        const studentElements = document.querySelectorAll(".student-only");

        if (role === "admin") {
            adminElements.forEach(el => el.classList.remove("hidden"));
            studentElements.forEach(el => el.classList.add("hidden"));
        } else {
            adminElements.forEach(el => el.classList.add("hidden"));
            studentElements.forEach(el => el.classList.remove("hidden"));
        }

        document.getElementById("login-wrapper").classList.add("hidden");
        document.getElementById("app-wrapper").classList.remove("hidden");

        // Dynamically initialize routing
        appRouter.route();
    }
};

// Bind login form
document.getElementById("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const user = document.getElementById("login-username").value.trim();
    const pass = document.getElementById("login-password").value;
    
    if (user && pass) {
        const success = await authService.login(user, pass);
        if (success) {
            // Clear inputs
            document.getElementById("login-username").value = "";
            document.getElementById("login-password").value = "";
        }
    }
});

// Bind logout button
document.getElementById("btn-logout").addEventListener("click", () => {
    authService.logout();
});

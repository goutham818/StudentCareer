const dashboardModule = {
    async loadDashboard() {
        try {
            // 1. Fetch overview stats
            const stats = await api.get("api/analytics/overview");
            if (stats) {
                document.getElementById("stat-total-students").textContent = stats.total_students;
                document.getElementById("stat-average-cgpa").textContent = stats.average_cgpa.toFixed(2);
                document.getElementById("stat-average-attendance").textContent = `${stats.average_attendance.toFixed(1)}%`;
                document.getElementById("stat-placement-readiness").textContent = `${stats.placement_readiness_score.toFixed(1)}%`;
            }

            // 2. Fetch lists for tables (top performers & at-risk)
            const chartsData = await api.get("api/analytics/performance");
            if (chartsData) {
                this.renderTopPerformers(chartsData.top_performers);
                this.renderAtRiskStudents(chartsData.at_risk_students);
            }
        } catch (error) {
            console.error("Error loading dashboard metrics:", error);
            showToast("Failed to load dashboard KPIs", "error");
        }
    },

    renderTopPerformers(performers) {
        const tbody = document.getElementById("top-performers-tbody");
        if (!tbody) return;

        if (!performers || performers.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center">No students found.</td></tr>`;
            return;
        }

        tbody.innerHTML = performers.map(s => `
            <tr>
                <td><strong>${s.roll_number}</strong></td>
                <td>${s.name}</td>
                <td>${s.department_name}</td>
                <td><span class="text-emerald font-bold">${s.cgpa.toFixed(2)}</span></td>
            </tr>
        `).join("");
    },

    renderAtRiskStudents(atRisk) {
        const tbody = document.getElementById("at-risk-tbody");
        if (!tbody) return;

        if (!atRisk || atRisk.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-emerald">No at-risk students found! All systems nominal.</td></tr>`;
            return;
        }

        tbody.innerHTML = atRisk.map(s => `
            <tr>
                <td><strong>${s.roll_number}</strong></td>
                <td>${s.name}</td>
                <td>
                    <span class="badge ${s.cgpa < 6.0 ? 'text-rose' : 'text-primary'} font-bold">
                        ${s.cgpa.toFixed(2)} (Att: ${s.attendance.toFixed(0)}%)
                    </span>
                </td>
                <td>
                    <span class="type-badge" style="background: var(--color-rose-glow); color: var(--color-rose); border-color: rgba(244, 63, 94, 0.2)">
                        ${s.risk_factors}
                    </span>
                </td>
            </tr>
        `).join("");
    }
};

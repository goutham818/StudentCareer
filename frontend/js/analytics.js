const analyticsModule = {
    chartInstances: {},

    getThemeColors() {
        const isDark = document.documentElement.getAttribute("data-theme") === "dark";
        return {
            textColor: isDark ? "#94a3b8" : "#475569",
            gridColor: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(15, 23, 42, 0.06)",
            accentColor: "#8b5cf6",
            emerald: "#10b981",
            blue: "#0ea5e9",
            amber: "#f59e0b",
            rose: "#f43f5e"
        };
    },

    async loadAnalytics() {
        try {
            const data = await api.get("api/analytics/performance");
            if (data) {
                const colors = this.getThemeColors();
                
                this.renderCGPADistribution(data.cgpa_distribution, colors);
                this.renderAttendanceDistribution(data.attendance_distribution, colors);
                this.renderDepartmentAnalytics(data.department_analytics, colors);
                this.renderSemesterAnalytics(data.semester_analytics, colors);
            }
        } catch (error) {
            console.error("Error loading analytics data:", error);
            showToast("Failed to load analytics details", "error");
        }
    },

    renderCGPADistribution(dist, colors) {
        const ctx = document.getElementById("chart-cgpa-dist");
        if (!ctx) return;

        if (this.chartInstances.cgpa) this.chartInstances.cgpa.destroy();

        const labels = Object.keys(dist);
        const values = Object.values(dist);

        this.chartInstances.cgpa = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Students',
                    data: values,
                    backgroundColor: colors.accentColor,
                    borderRadius: 6,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { padding: 12, cornerRadius: 8 }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: colors.textColor }
                    },
                    y: {
                        grid: { color: colors.gridColor },
                        ticks: { color: colors.textColor, stepSize: 1 }
                    }
                }
            }
        });
    },

    renderAttendanceDistribution(dist, colors) {
        const ctx = document.getElementById("chart-attendance-dist");
        if (!ctx) return;

        if (this.chartInstances.attendance) this.chartInstances.attendance.destroy();

        const labels = Object.keys(dist);
        const values = Object.values(dist);

        this.chartInstances.attendance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        colors.rose,     // <75%
                        colors.amber,    // 75-85%
                        colors.blue,     // 85-95%
                        colors.emerald   // >95%
                    ],
                    borderWidth: 2,
                    borderColor: 'rgba(0,0,0,0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: colors.textColor, boxWidth: 12, padding: 15 }
                    },
                    tooltip: { padding: 12, cornerRadius: 8 }
                },
                cutout: '60%'
            }
        });
    },

    renderDepartmentAnalytics(depts, colors) {
        const ctx = document.getElementById("chart-department-analysis");
        if (!ctx) return;

        if (this.chartInstances.department) this.chartInstances.department.destroy();

        // Shorten long department names for display
        const labels = depts.map(d => {
            const name = d.department_name;
            if (name.includes("Computer Science")) return "CSE";
            if (name.includes("Information Technology")) return "IT";
            if (name.includes("Electronics & Communication")) return "ECE";
            if (name.includes("Electrical & Electronics")) return "EEE";
            if (name.includes("Mechanical")) return "MECH";
            return name;
        });
        const cgpaValues = depts.map(d => d.average_cgpa);
        const attendanceValues = depts.map(d => d.average_attendance);

        this.chartInstances.department = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Avg CGPA',
                        data: cgpaValues,
                        backgroundColor: colors.accentColor,
                        borderRadius: 6,
                        yAxisID: 'y_cgpa'
                    },
                    {
                        label: 'Avg Attendance (%)',
                        data: attendanceValues,
                        backgroundColor: colors.blue,
                        borderRadius: 6,
                        yAxisID: 'y_attendance'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: colors.textColor } },
                    tooltip: { padding: 12, cornerRadius: 8 }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: colors.textColor }
                    },
                    y_cgpa: {
                        type: 'linear',
                        position: 'left',
                        min: 0,
                        max: 10,
                        grid: { color: colors.gridColor },
                        ticks: { color: colors.textColor },
                        title: { display: true, text: 'CGPA', color: colors.textColor }
                    },
                    y_attendance: {
                        type: 'linear',
                        position: 'right',
                        min: 0,
                        max: 100,
                        grid: { drawOnChartArea: false },
                        ticks: { color: colors.textColor },
                        title: { display: true, text: 'Attendance (%)', color: colors.textColor }
                    }
                }
            }
        });
    },

    renderSemesterAnalytics(sems, colors) {
        const ctx = document.getElementById("chart-semester-analysis");
        if (!ctx) return;

        if (this.chartInstances.semester) this.chartInstances.semester.destroy();

        const labels = sems.map(s => `Sem ${s.semester}`);
        const cgpaValues = sems.map(s => s.average_cgpa);
        const attendanceValues = sems.map(s => s.average_attendance);

        this.chartInstances.semester = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Avg CGPA',
                        data: cgpaValues,
                        borderColor: colors.accentColor,
                        backgroundColor: 'transparent',
                        tension: 0.3,
                        pointRadius: 5,
                        yAxisID: 'y_cgpa'
                    },
                    {
                        label: 'Avg Attendance (%)',
                        data: attendanceValues,
                        borderColor: colors.emerald,
                        backgroundColor: 'transparent',
                        tension: 0.3,
                        pointRadius: 5,
                        yAxisID: 'y_attendance'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: colors.textColor } },
                    tooltip: { padding: 12, cornerRadius: 8 }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: colors.textColor }
                    },
                    y_cgpa: {
                        type: 'linear',
                        position: 'left',
                        min: 4,
                        max: 10,
                        grid: { color: colors.gridColor },
                        ticks: { color: colors.textColor },
                        title: { display: true, text: 'CGPA', color: colors.textColor }
                    },
                    y_attendance: {
                        type: 'linear',
                        position: 'right',
                        min: 50,
                        max: 100,
                        grid: { drawOnChartArea: false },
                        ticks: { color: colors.textColor },
                        title: { display: true, text: 'Attendance (%)', color: colors.textColor }
                    }
                }
            }
        });
    }
};

// Bind Export PDF Button
document.getElementById("btn-export-pdf").addEventListener("click", () => {
    window.print();
});

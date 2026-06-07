const studentsModule = {
    allStudents: [],
    departments: [],

    async init() {
        await this.loadDepartments();
        await this.loadStudentsList();
    },

    async loadDepartments() {
        try {
            const depts = await api.get("api/departments");
            if (depts) {
                this.departments = depts;
                
                // Populate filters and forms select lists
                const filterSelect = document.getElementById("student-dept-filter");
                const formSelect = document.getElementById("student-dept");
                
                if (filterSelect && formSelect) {
                    const optionsHtml = depts.map(d => `<option value="${d.id}">${d.name}</option>`).join("");
                    filterSelect.innerHTML = `<option value="">All Departments</option>` + optionsHtml;
                    formSelect.innerHTML = `<option value="">Select Department</option>` + optionsHtml;
                }
            }
        } catch (error) {
            console.error("Error loading departments:", error);
        }
    },

    async loadStudentsList() {
        try {
            const list = await api.get("api/students");
            if (list) {
                this.allStudents = list;
                this.renderStudentsTable();
            }
        } catch (error) {
            console.error("Error loading students list:", error);
            showToast("Failed to retrieve student profiles", "error");
        }
    },

    renderStudentsTable() {
        const tbody = document.getElementById("students-table-tbody");
        if (!tbody) return;

        const searchQuery = document.getElementById("student-search-input").value.toLowerCase().trim();
        const deptFilter = document.getElementById("student-dept-filter").value;

        // Apply local filtering
        const filtered = this.allStudents.filter(s => {
            const matchesSearch = s.name.toLowerCase().includes(searchQuery) || 
                                  s.roll_number.toLowerCase().includes(searchQuery);
            const matchesDept = !deptFilter || s.department_id == deptFilter;
            return matchesSearch && matchesDept;
        });

        if (filtered.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center">No student records found matching filters.</td></tr>`;
            return;
        }

        tbody.innerHTML = filtered.map(s => {
            const skillsSnippet = s.skills ? s.skills.split(",").slice(0, 3).map(sk => `<span class="type-badge" style="margin-right: 4px; margin-bottom: 4px; display: inline-block;">${sk.trim()}</span>`).join("") : "N/A";
            
            return `
                <tr>
                    <td><strong>${s.roll_number}</strong></td>
                    <td>${s.name}</td>
                    <td>${s.department_name || 'N/A'}</td>
                    <td>Sem ${s.semester}</td>
                    <td><span class="text-emerald font-bold">${s.cgpa.toFixed(2)}</span></td>
                    <td>${s.attendance.toFixed(1)}%</td>
                    <td style="max-width: 200px;">${skillsSnippet}</td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn-action btn-action-edit" onclick="studentsModule.openEditModal(${s.id})" title="Edit Profile">
                                <i class="fa-solid fa-pen"></i>
                            </button>
                            <button class="btn-action btn-action-delete" onclick="studentsModule.deleteStudentProfile(${s.id})" title="Delete Profile">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("");
    },

    openAddModal() {
        document.getElementById("student-modal-title").textContent = "Add Student Profile";
        document.getElementById("student-modal-id").value = "";
        document.getElementById("form-student-save").reset();
        
        // Enable roll number edit for new students
        document.getElementById("student-roll").removeAttribute("readonly");
        
        document.getElementById("student-modal").classList.remove("hidden");
    },

    async openEditModal(id) {
        try {
            const s = await api.get(`api/students/${id}`);
            if (s) {
                document.getElementById("student-modal-title").textContent = "Edit Student Profile";
                document.getElementById("student-modal-id").value = s.id;
                document.getElementById("student-name").value = s.name;
                document.getElementById("student-roll").value = s.roll_number;
                
                // Roll number should be read-only on edit to prevent identity mismatch
                document.getElementById("student-roll").setAttribute("readonly", true);
                
                document.getElementById("student-dept").value = s.department_id;
                document.getElementById("student-semester").value = s.semester;
                document.getElementById("student-cgpa").value = s.cgpa;
                document.getElementById("student-attendance").value = s.attendance;
                document.getElementById("student-skills").value = s.skills || "";
                document.getElementById("student-interests").value = s.interests || "";
                
                document.getElementById("student-modal").classList.remove("hidden");
            }
        } catch (error) {
            console.error("Error fetching student profile:", error);
            showToast("Failed to fetch student details", "error");
        }
    },

    closeModal() {
        document.getElementById("student-modal").classList.add("hidden");
    },

    async saveStudent(e) {
        e.preventDefault();
        
        const id = document.getElementById("student-modal-id").value;
        const studentData = {
            name: document.getElementById("student-name").value.trim(),
            roll_number: document.getElementById("student-roll").value.trim(),
            department_id: parseInt(document.getElementById("student-dept").value),
            semester: parseInt(document.getElementById("student-semester").value),
            cgpa: parseFloat(document.getElementById("student-cgpa").value),
            attendance: parseFloat(document.getElementById("student-attendance").value),
            skills: document.getElementById("student-skills").value.trim(),
            interests: document.getElementById("student-interests").value.trim()
        };

        try {
            let result;
            if (id) {
                // Update
                result = await api.put(`api/students/${id}`, studentData);
                showToast("Student profile updated successfully", "success");
            } else {
                // Create
                result = await api.post("api/students", studentData);
                showToast("Student profile created successfully", "success");
            }
            
            if (result) {
                this.closeModal();
                await this.loadStudentsList();
            }
        } catch (error) {
            console.error("Error saving student:", error);
        }
    },

    async deleteStudentProfile(id) {
        if (!confirm("Are you sure you want to delete this student profile? This will also delete their login credentials.")) return;

        try {
            const success = await api.delete(`api/students/${id}`);
            if (success) {
                showToast("Student profile deleted successfully", "success");
                await this.loadStudentsList();
            }
        } catch (error) {
            console.error("Error deleting student:", error);
        }
    }
};

// Bind UI actions
document.getElementById("btn-add-student-modal").addEventListener("click", () => {
    studentsModule.openAddModal();
});

document.getElementById("btn-close-student-modal").addEventListener("click", () => {
    studentsModule.closeModal();
});

document.getElementById("btn-cancel-student-modal").addEventListener("click", () => {
    studentsModule.closeModal();
});

document.getElementById("form-student-save").addEventListener("submit", (e) => {
    studentsModule.saveStudent(e);
});

// Bind filters
document.getElementById("student-search-input").addEventListener("keyup", () => {
    studentsModule.renderStudentsTable();
});

document.getElementById("student-dept-filter").addEventListener("change", () => {
    studentsModule.renderStudentsTable();
});

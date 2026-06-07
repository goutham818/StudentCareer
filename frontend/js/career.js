const careerModule = {
    async init() {
        this.resetPrediction();
        this.resetCareerList();
    },

    resetPrediction() {
        document.getElementById("form-performance-predict").reset();
        document.getElementById("prediction-result").classList.add("hidden");
    },

    resetCareerList() {
        const container = document.getElementById("career-recommendations-list");
        if (!container) return;
        
        container.innerHTML = `
            <div class="no-data-placeholder">
                <i class="fa-solid fa-road"></i>
                <p>Click "Calculate Career Match Scores" to analyze recommendation profiles.</p>
            </div>
        `;
    },

    async predictPerformance(e) {
        e.preventDefault();

        const payload = {
            attendance: parseFloat(document.getElementById("predict-attendance").value),
            internal_marks: parseFloat(document.getElementById("predict-internal-marks").value),
            previous_cgpa: parseFloat(document.getElementById("predict-previous-cgpa").value),
            assignment_score: parseFloat(document.getElementById("predict-assignment-score").value)
        };

        try {
            const data = await api.post("api/predict", payload);
            if (data && data.predicted_category) {
                this.renderPredictionResult(data.predicted_category);
                showToast("Performance prediction completed!", "success");
            }
        } catch (error) {
            console.error("Prediction failed:", error);
        }
    },

    renderPredictionResult(category) {
        const resultBox = document.getElementById("prediction-result");
        const badge = document.getElementById("predicted-badge");
        const explainer = document.getElementById("prediction-explainer");

        if (!resultBox || !badge || !explainer) return;

        // Strip and clean classnames
        badge.className = "badge-prediction";
        
        // Match first word if multi-word (e.g. Needs Improvement)
        const classKeyword = category.split(" ")[0]; 
        badge.classList.add(classKeyword);
        badge.textContent = category;

        let explanation = "";
        switch (category) {
            case "Excellent":
                explanation = "🚀 The AI model projects outstanding performance! Highly recommended for high-performing engineering and research domains.";
                break;
            case "Good":
                explanation = "📈 The AI model projects a stable, strong performance. Recommended for advanced engineering roles and corporate training.";
                break;
            case "Average":
                explanation = "⚖️ The AI model projects an average outcome. Academic coaching and targeted micro-credentials are recommended.";
                break;
            case "Needs Improvement":
                explanation = "⚠️ The AI model warns of risk! Suggested action: regular class attendance monitoring, remedial training, and close faculty mentoring.";
                break;
            default:
                explanation = "Performance prediction finalized.";
        }

        explainer.textContent = explanation;
        resultBox.classList.remove("hidden");
    },

    async generateCareerGuidance() {
        const btn = document.getElementById("btn-generate-guidance");
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Calculating scores...`;

        try {
            const list = await api.post("api/career-guidance", {});
            if (list) {
                this.renderCareerRecommendations(list);
                showToast("Career guidance calculated!", "success");
            }
        } catch (error) {
            console.error("Career guidance failed:", error);
            this.resetCareerList();
        } finally {
            btn.disabled = false;
            btn.innerHTML = `<i class="fa-solid fa-compass"></i> Calculate Career Match Scores & Roadmaps`;
        }
    },

    renderCareerRecommendations(list) {
        const container = document.getElementById("career-recommendations-list");
        if (!container) return;

        if (!list || list.length === 0) {
            container.innerHTML = `
                <div class="no-data-placeholder">
                    <i class="fa-solid fa-road"></i>
                    <p>No profile details found. Verify student profile details are populated.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = list.map((item, idx) => {
            const cardId = `career-card-${idx}`;
            const roadmapId = `roadmap-content-${idx}`;
            const toggleId = `roadmap-toggle-${idx}`;
            
            return `
                <div class="career-card" id="${cardId}">
                    <div class="career-card-top">
                        <span class="career-title">${item.career_path}</span>
                        <span class="match-score-badge">${item.match_score.toFixed(1)}% Match</span>
                    </div>
                    
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: 0%" id="progress-fill-${idx}"></div>
                    </div>

                    <div class="career-skills-rec">
                        <strong>Recommended focus:</strong> ${item.recommended_skills}
                    </div>

                    <button class="roadmap-toggle-btn" id="${toggleId}" onclick="careerModule.toggleRoadmap('${roadmapId}', '${toggleId}')">
                        <i class="fa-solid fa-chevron-down"></i> View Learning Roadmap
                    </button>

                    <div class="roadmap-content hidden" id="${roadmapId}">${item.roadmap}</div>
                </div>
            `;
        }).join("");

        // Trigger animations for progress bars
        setTimeout(() => {
            list.forEach((item, idx) => {
                const fill = document.getElementById(`progress-fill-${idx}`);
                if (fill) fill.style.width = `${item.match_score}%`;
            });
        }, 150);
    },

    toggleRoadmap(roadmapId, toggleId) {
        const content = document.getElementById(roadmapId);
        const toggle = document.getElementById(toggleId);
        
        if (!content || !toggle) return;

        const isHidden = content.classList.contains("hidden");
        
        if (isHidden) {
            content.classList.remove("hidden");
            toggle.innerHTML = `<i class="fa-solid fa-chevron-up"></i> Hide Learning Roadmap`;
        } else {
            content.classList.add("hidden");
            toggle.innerHTML = `<i class="fa-solid fa-chevron-down"></i> View Learning Roadmap`;
        }
    }
};

// Bind actions
document.getElementById("form-performance-predict").addEventListener("submit", (e) => {
    careerModule.predictPerformance(e);
});

document.getElementById("btn-generate-guidance").addEventListener("click", () => {
    careerModule.generateCareerGuidance();
});

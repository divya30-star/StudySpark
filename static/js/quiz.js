const quizApp = document.getElementById("quiz-app");

if (quizApp) {
    const quizId = quizApp.dataset.quizId;
    const loading = document.getElementById("quiz-loading");
    const form = document.getElementById("quiz-form");
    const questionContainer = document.getElementById("questions-container");
    const errorBox = document.getElementById("quiz-error");

    async function loadQuestions() {
        try {
            const response = await fetch(`/api/quiz/${quizId}`);
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Could not load quiz.");

            questionContainer.innerHTML = "";
            data.questions.forEach((question, index) => {
                const block = document.createElement("section");
                block.className = "quiz-question";

                const heading = document.createElement("h3");
                heading.textContent = `${index + 1}. ${question.question_text}`;
                block.appendChild(heading);

                ["A", "B", "C", "D"].forEach(letter => {
                    const option = document.createElement("label");
                    option.className = "option";
                    const radio = document.createElement("input");
                    radio.type = "radio";
                    radio.name = `question-${question.id}`;
                    radio.value = letter;
                    radio.required = true;

                    const optionText = document.createElement("span");
                    optionText.textContent = question[`option_${letter.toLowerCase()}`];

                    option.appendChild(radio);
                    option.appendChild(optionText);
                    block.appendChild(option);
                });

                questionContainer.appendChild(block);
            });

            loading.classList.add("hidden");
            form.classList.remove("hidden");
        } catch (error) {
            loading.textContent = "";
            errorBox.textContent = error.message;
        }
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        errorBox.textContent = "";

        const answers = {};
        const questionBlocks = form.querySelectorAll(".quiz-question");
        questionBlocks.forEach(block => {
            const selected = block.querySelector("input:checked");
            if (selected) {
                const questionId = selected.name.replace("question-", "");
                answers[questionId] = selected.value;
            }
        });

        try {
            const response = await fetch("/api/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ quiz_id: Number(quizId), answers })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || "Could not submit quiz.");

            sessionStorage.setItem("lastQuizResult", JSON.stringify(result));
            window.location.href = "/result";
        } catch (error) {
            errorBox.textContent = error.message;
        }
    });

    loadQuestions();
}

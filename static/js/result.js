const scoreElement = document.getElementById("result-score");
if (scoreElement) {
    const savedResult = sessionStorage.getItem("lastQuizResult");
    if (savedResult) {
        const result = JSON.parse(savedResult);
        scoreElement.textContent = `${result.score} / ${result.total}`;
        document.getElementById("result-percentage").textContent =
            `You scored ${result.percentage}%. Keep practising!`;
        sessionStorage.removeItem("lastQuizResult");
    } else {
        scoreElement.textContent = "No result";
        document.getElementById("result-percentage").textContent =
            "Attempt a quiz first to see your result.";
    }
}

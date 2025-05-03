document.addEventListener("DOMContentLoaded", () => {
    const scoreElement = document.getElementById("score");

    scoreElement.textContent = "???";

    const averageBlock = document.getElementById("average-block");

    const targetScore = parseFloat("{{ score }}");
    let currentScore = 0.9;
    let currentScoreAfr = 1.0;
    let animationSpeed = 35;
    let speedIncreased = false;
    let clickCount = 0;

    function animateScore() {
        if (isNaN(targetScore)) {
            scoreElement.textContent = "{{ score }}";

            averageBlock.style.opacity = "1";
        } else if (currentScore < targetScore) {
            currentScore += 0.05;
            scoreElement.textContent = currentScore.toFixed(1);

            setTimeout(animateScore, animationSpeed);
        } else {
            scoreElement.textContent = targetScore.toFixed(1);

            averageBlock.style.opacity = "1";
        }
    }

    document.addEventListener("click", () => {
        clickCount++;

        if (clickCount === 2) {
            animationSpeed = 10;
            speedIncreased = true;
        }

        setTimeout(() => {
            clickCount = 0;
        }, 500);
    });

    setTimeout(() => {
        animateScore();
    }, 1000);
});

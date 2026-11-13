let cards = [];
let currentIndex = 0;
let showingAnswer = false;

const cardElement = document.getElementById("flashcard");
if (cardElement) {
    const cardSubject = document.getElementById("card-subject");
    const cardText = document.getElementById("card-text");
    const counter = document.getElementById("card-counter");
    const emptyMessage = document.getElementById("cards-empty");
    const message = document.getElementById("card-message");

    function renderCard() {
        if (cards.length === 0) {
            cardText.textContent = "No cards yet";
            cardSubject.textContent = "FLASHCARDS";
            counter.textContent = "0 / 0";
            emptyMessage.classList.remove("hidden");
            return;
        }
        emptyMessage.classList.add("hidden");
        const card = cards[currentIndex];
        cardSubject.textContent = card.subject;
        cardText.textContent = showingAnswer ? card.back : card.front;
        counter.textContent = `${currentIndex + 1} / ${cards.length}`;
        cardElement.classList.toggle("flipped", showingAnswer);
    }

    async function loadCards() {
        try {
            const response = await fetch("/api/flashcards");
            cards = await response.json();
            currentIndex = 0;
            showingAnswer = false;
            renderCard();
        } catch (error) {
            cardText.textContent = "Could not load flashcards.";
        }
    }

    function flipCard() {
        if (!cards.length) return;
        showingAnswer = !showingAnswer;
        renderCard();
    }

    cardElement.addEventListener("click", flipCard);
    cardElement.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            flipCard();
        }
    });

    document.getElementById("previous-card").addEventListener("click", () => {
        if (!cards.length) return;
        currentIndex = (currentIndex - 1 + cards.length) % cards.length;
        showingAnswer = false;
        renderCard();
    });

    document.getElementById("next-card").addEventListener("click", () => {
        if (!cards.length) return;
        currentIndex = (currentIndex + 1) % cards.length;
        showingAnswer = false;
        renderCard();
    });

    document.getElementById("add-card-form").addEventListener("submit", async event => {
        event.preventDefault();
        message.textContent = "";

        const payload = {
            subject: document.getElementById("new-subject").value.trim(),
            front: document.getElementById("new-front").value.trim(),
            back: document.getElementById("new-back").value.trim()
        };

        try {
            const response = await fetch("/api/flashcards", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Could not add card.");

            cards.push(data);
            currentIndex = cards.length - 1;
            showingAnswer = false;
            renderCard();
            event.target.reset();
            message.textContent = "Flashcard added successfully!";
        } catch (error) {
            message.textContent = error.message;
        }
    });

    loadCards();
}

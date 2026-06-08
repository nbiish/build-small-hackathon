/**
 * TinyBard — Frontend Client
 * Connects to the gr.Server backend via @gradio/client.
 * All game state is managed client-side and passed to the API.
 */

const GRADIO_CLIENT_URL = window.location.origin;

// ---------------------------------------------------------------------------
// Game State
// ---------------------------------------------------------------------------
let gameState = {
    genre: "",
    step: 0,
    health: 100,
    history: [],
    gameActive: false
};

// ---------------------------------------------------------------------------
// DOM refs
// ---------------------------------------------------------------------------
const output = document.getElementById("output");
const choicesEl = document.getElementById("choices");
const genreSelector = document.getElementById("genre-selector");
const inputLine = document.getElementById("input-line");
const cmdInput = document.getElementById("cmd-input");
const healthVal = document.getElementById("health-val");
const modelStatus = document.getElementById("model-status");
const boot = document.getElementById("boot");

// ---------------------------------------------------------------------------
// Gradio Client
// ---------------------------------------------------------------------------
let gradioClient = null;
const GRADIO_PATH = "/gradio";

async function initClient() {
    try {
        const { Client } = await import(
            "https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js"
        );
        gradioClient = await Client.connect(GRADIO_CLIENT_URL + GRADIO_PATH);
        modelStatus.textContent = "MODEL: CONNECTED";
        modelStatus.style.color = "#00ff41";
    } catch (e) {
        console.warn("Gradio client init failed, using fetch fallback:", e);
        gradioClient = null;
        modelStatus.textContent = "MODEL: FETCH MODE";
        modelStatus.style.color = "#ffb000";
    }
}

async function apiCall(endpoint, payload) {
    if (gradioClient) {
        try {
            const result = await gradioClient.predict(endpoint, payload);
            return result.data;
        } catch (e) {
            console.warn("Gradio client call failed, falling back to fetch:", e);
        }
    }
    // Fallback: direct fetch to gradio API
    const resp = await fetch(`${GRADIO_CLIENT_URL}${GRADIO_PATH}/api/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: Object.values(payload) })
    });
    const json = await resp.json();
    return json.data;
}

// ---------------------------------------------------------------------------
// UI Helpers
// ---------------------------------------------------------------------------
function scrollToBottom() {
    output.scrollTop = output.scrollHeight;
}

function appendOutput(html, className = "") {
    const el = document.createElement("div");
    el.className = className;
    el.innerHTML = html;
    output.appendChild(el);
    scrollToBottom();
}

function clearBoot() {
    if (boot) boot.remove();
}

function updateHealth(hp) {
    gameState.health = hp;
    healthVal.textContent = hp;
    if (hp <= 25) healthVal.style.color = "#ff0040";
    else if (hp <= 50) healthVal.style.color = "#ffb000";
    else healthVal.style.color = "#00ff41";
}

function showChoices(choices) {
    choicesEl.innerHTML = "";
    choicesEl.style.display = "flex";

    choices.forEach((choice, i) => {
        const btn = document.createElement("button");
        btn.className = "choice-btn";
        btn.textContent = choice;
        btn.addEventListener("click", () => handleChoice(choice));
        choicesEl.appendChild(btn);
    });
}

function hideChoices() {
    choicesEl.style.display = "none";
    choicesEl.innerHTML = "";
}

function showInput() {
    inputLine.style.display = "flex";
    cmdInput.focus();
}

function hideInput() {
    inputLine.style.display = "none";
}

// ---------------------------------------------------------------------------
// Game Logic
// ---------------------------------------------------------------------------
async function startGame(genre) {
    gameState = { genre, step: 0, health: 100, history: [], gameActive: true };
    genreSelector.style.display = "none";
    clearBoot();

    appendOutput(`<span class="narrator-prefix">> STARTING ${genre.toUpperCase()} ADVENTURE...</span>`, "line amber");
    updateHealth(100);

    try {
        const data = await apiCall("/start_game", { genre });

        gameState.step = data.step || 1;
        gameState.history = data.history || [];

        const storyEl = document.createElement("div");
        storyEl.className = "story-text";
        storyEl.textContent = data.story;
        output.appendChild(storyEl);

        if (data.game_over) {
            endGame(data);
        } else {
            showChoices(data.choices);
        }
    } catch (e) {
        appendOutput(`<span class="error">ERROR: ${e.message}</span>`, "line error");
        console.error(e);
    }
    scrollToBottom();
}

async function handleChoice(choice) {
    if (!gameState.gameActive) return;

    hideChoices();
    appendOutput(`<span class="player-action">> You chose: ${choice}</span>`, "player-action");

    try {
        const data = await apiCall("/make_choice", {
            choice,
            genre: gameState.genre,
            step: gameState.step,
            health: gameState.health,
            history_json: JSON.stringify(gameState.history)
        });

        gameState.step = data.step || gameState.step + 1;
        gameState.history = data.history || gameState.history;
        updateHealth(data.health ?? gameState.health);

        const storyEl = document.createElement("div");
        storyEl.className = "story-text";
        storyEl.textContent = data.story;
        output.appendChild(storyEl);

        if (data.game_over) {
            endGame(data);
        } else {
            showChoices(data.choices);
        }
    } catch (e) {
        appendOutput(`<span class="error">ERROR: ${e.message}</span>`, "line error");
        console.error(e);
    }
    scrollToBottom();
}

function endGame(data) {
    gameState.gameActive = false;
    hideChoices();

    const isWin = data.health > 0;
    const className = isWin ? "game-over-win" : "game-over-lose";
    const label = isWin ? "★ VICTORY ★" : "☠ GAME OVER ☠";

    appendOutput(`<div class="${className}">${label}<br><small>Final Health: ${data.health}</small></div>`, "");

    // New game button
    const btn = document.createElement("button");
    btn.className = "new-game-btn";
    btn.textContent = "[ NEW ADVENTURE ]";
    btn.addEventListener("click", resetGame);
    choicesEl.style.display = "flex";
    choicesEl.appendChild(btn);
}

function resetGame() {
    output.innerHTML = "";
    hideChoices();
    gameState = { genre: "", step: 0, health: 100, history: [], gameActive: false };
    healthVal.textContent = "100";
    healthVal.style.color = "#00ff41";
    genreSelector.style.display = "flex";
}

// ---------------------------------------------------------------------------
// Event Listeners
// ---------------------------------------------------------------------------
document.querySelectorAll(".genre-option").forEach(el => {
    el.addEventListener("click", () => {
        const genre = el.dataset.genre;
        startGame(genre);
    });
});

cmdInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && cmdInput.value.trim()) {
        handleChoice(cmdInput.value.trim());
        cmdInput.value = "";
    }
});

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
(async () => {
    await initClient();

    // Check model status
    try {
        const resp = await fetch(`${GRADIO_CLIENT_URL}/api/model_status`);
        const status = await resp.json();
        if (status.available) {
            modelStatus.textContent = "MODEL: READY";
            modelStatus.style.color = "#00ff41";
        } else {
            modelStatus.textContent = "MODEL: FALLBACK";
            modelStatus.style.color = "#ffb000";
        }
    } catch {
        modelStatus.textContent = "MODEL: UNKNOWN";
        modelStatus.style.color = "#666";
    }
})();

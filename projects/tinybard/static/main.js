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
    gameActive: false,
    saveSlot: null
};

let currentAudio = null;

function playTtsAudio(url) {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    currentAudio = new Audio(url);
    currentAudio.play().catch(e => console.log("Audio play failed or interrupted:", e));
}

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
// API client — uses FastAPI clean-JSON endpoints
// ---------------------------------------------------------------------------
async function checkModelStatus() {
    try {
        const resp = await fetch(`${GRADIO_CLIENT_URL}/api/model_status`);
        if (!resp.ok) return;
        const s = await resp.json();
        const model = s.model || "inference";
        const cd = s.cooldown || { active: false, remaining_seconds: 0, window_seconds: 0 };
        if (cd.active) {
            modelStatus.textContent = `☘ ${model} / COOLDOWN ${cd.remaining_seconds.toFixed(1)}s`;
            modelStatus.style.color = "var(--asp-ember)";
        } else if (model) {
            modelStatus.textContent = `☘ ${model} / READY`;
            modelStatus.style.color = "var(--asp-sun)";
        } else {
            modelStatus.textContent = "☘ NO MODEL / FALLBACK";
            modelStatus.style.color = "var(--asp-frost)";
        }
    } catch {
        modelStatus.textContent = "☘ MODEL: ?";
    }
}

setInterval(checkModelStatus, 2000);

async function apiCall(endpoint, payload) {
    const path = endpoint === "/start_game"
        ? "/api/game/start"
        : "/api/game/choice";
    const resp = await fetch(`${GRADIO_CLIENT_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
    }
    return await resp.json();
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

    choices.forEach((choice) => {
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
    gameState = { genre, step: 0, health: 100, history: [], gameActive: true, saveSlot: null };
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

        if (data.audio_url) {
            playTtsAudio(data.audio_url);
        }

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

        if (data.audio_url) {
            playTtsAudio(data.audio_url);
        }

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
    gameState = { genre: "", step: 0, health: 100, history: [], gameActive: false, saveSlot: null };
    healthVal.textContent = "100";
    healthVal.style.color = "#00ff41";
    genreSelector.style.display = "flex";
    loadResumeButtons();
}

// ---------------------------------------------------------------------------
// Save / Load System
// ---------------------------------------------------------------------------
const LS_KEY = "tinybard_saves";

function getLocalSaves() {
    try {
        return JSON.parse(localStorage.getItem(LS_KEY) || "[]");
    } catch {
        return [];
    }
}

function setLocalSaves(saves) {
    localStorage.setItem(LS_KEY, JSON.stringify(saves));
}

function saveToLocal(slotName, data) {
    const saves = getLocalSaves();
    const idx = saves.findIndex(s => s.slot_name === slotName);
    const entry = {
        slot_name: slotName,
        genre: data.genre,
        step: data.step,
        health: data.health,
        history: data.history,
        game_over: data.game_over || false,
        timestamp: Date.now() / 1000
    };
    if (idx >= 0) saves[idx] = entry;
    else saves.push(entry);
    setLocalSaves(saves);
}

function deleteLocalSave(slotName) {
    const saves = getLocalSaves().filter(s => s.slot_name !== slotName);
    setLocalSaves(saves);
}

async function saveToServer(slotName, data) {
    try {
        const resp = await fetch(`${GRADIO_CLIENT_URL}/api/game/save`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                slot_name: slotName,
                genre: data.genre,
                step: data.step,
                health: data.health,
                history: data.history,
                game_over: data.game_over || false
            })
        });
        return await resp.json();
    } catch {
        return { status: "error" };
    }
}

async function fetchSaves() {
    let serverSaves = [];
    try {
        const resp = await fetch(`${GRADIO_CLIENT_URL}/api/game/saves`);
        const data = await resp.json();
        serverSaves = data.saves || [];
    } catch {}

    const localSaves = getLocalSaves();
    const merged = new Map();
    for (const s of localSaves) merged.set(s.slot_name, s);
    for (const s of serverSaves) {
        if (!merged.has(s.slot_name) || s.timestamp > (merged.get(s.slot_name).timestamp || 0)) {
            merged.set(s.slot_name, s);
        }
    }
    return Array.from(merged.values()).sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
}

async function loadSaveFromServer(slotName) {
    try {
        const resp = await fetch(`${GRADIO_CLIENT_URL}/api/game/load`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ slot_name: slotName })
        });
        return await resp.json();
    } catch {
        return null;
    }
}

async function deleteSaveFromServer(slotName) {
    try {
        await fetch(`${GRADIO_CLIENT_URL}/api/game/save/${encodeURIComponent(slotName)}`, {
            method: "DELETE"
        });
    } catch {}
}

// ---------------------------------------------------------------------------
// Save Dialog
// ---------------------------------------------------------------------------
const saveModal = document.getElementById("tb-save-modal");
const saveNameInput = document.getElementById("tb-save-name");
const saveAndExitBtn = document.getElementById("tb-save-and-exit");
const exitNoSaveBtn = document.getElementById("tb-exit-no-save");
const saveCancelBtn = document.getElementById("tb-save-cancel");
const saveStatus = document.getElementById("tb-save-status");

function showSaveDialog() {
    if (!gameState.gameActive || gameState.game_over) {
        resetGame();
        return;
    }
    const defaultName = `${gameState.genre}-step${gameState.step}`;
    saveNameInput.value = gameState.saveSlot || defaultName;
    saveStatus.textContent = "";
    saveModal.style.display = "flex";
    saveNameInput.focus();
}

function hideSaveDialog() {
    saveModal.style.display = "none";
}

if (saveModal) {
    saveCancelBtn.addEventListener("click", hideSaveDialog);

    saveModal.addEventListener("click", (e) => {
        if (e.target === saveModal) hideSaveDialog();
    });

    exitNoSaveBtn.addEventListener("click", () => {
        hideSaveDialog();
        resetGame();
    });

    saveAndExitBtn.addEventListener("click", async () => {
        const slotName = saveNameInput.value.trim() || `${gameState.genre}-step${gameState.step}`;
        saveAndExitBtn.disabled = true;
        saveStatus.textContent = "Saving...";

        const saveData = {
            genre: gameState.genre,
            step: gameState.step,
            health: gameState.health,
            history: gameState.history,
            game_over: !gameState.gameActive
        };

        saveToLocal(slotName, saveData);
        const serverResult = await saveToServer(slotName, saveData);

        saveStatus.textContent = serverResult.status === "ok"
            ? `✓ Saved to "${slotName}"`
            : `✓ Saved locally as "${slotName}"`;
        saveStatus.style.color = "var(--asp-sun)";

        setTimeout(() => {
            hideSaveDialog();
            resetGame();
        }, 600);
    });
}

// ---------------------------------------------------------------------------
// Saves Dropdown
// ---------------------------------------------------------------------------
const savesBtn = document.getElementById("saves-btn");
const savesDropdown = document.getElementById("saves-dropdown");
const savesList = document.getElementById("saves-list");

function toggleSavesDropdown() {
    if (savesDropdown.style.display === "none") {
        refreshSavesList();
        savesDropdown.style.display = "block";
    } else {
        savesDropdown.style.display = "none";
    }
}

async function refreshSavesList() {
    const saves = await fetchSaves();
    savesList.innerHTML = "";

    if (saves.length === 0) {
        savesList.innerHTML = '<div class="saves-empty">No saved journeys yet.</div>';
        return;
    }

    for (const save of saves) {
        const item = document.createElement("div");
        item.className = "save-item";

        const ts = save.timestamp ? new Date(save.timestamp * 1000).toLocaleDateString() : "";
        const genreLabel = (save.genre || "unknown").toUpperCase();
        const statusIcon = save.game_over ? "☠" : "◈";

        item.innerHTML = `
            <div class="save-info" data-slot="${save.slot_name}">
                <span class="save-genre">${genreLabel}</span>
                <span class="save-name">${save.slot_name}</span>
                <span class="save-meta">Step ${save.step} · HP ${save.health} ${ts ? "· " + ts : ""}</span>
            </div>
            <button class="save-delete-btn" data-slot="${save.slot_name}" title="Delete">✕</button>
        `;

        item.querySelector(".save-info").addEventListener("click", () => {
            loadSavedGame(save.slot_name);
        });

        item.querySelector(".save-delete-btn").addEventListener("click", async (e) => {
            e.stopPropagation();
            await deleteSaveFromServer(save.slot_name);
            deleteLocalSave(save.slot_name);
            refreshSavesList();
        });

        savesList.appendChild(item);
    }
}

async function loadSavedGame(slotName) {
    savesDropdown.style.display = "none";

    let saveData = null;

    const localSaves = getLocalSaves();
    const localMatch = localSaves.find(s => s.slot_name === slotName);
    if (localMatch && localMatch.history && localMatch.history.length > 0) {
        saveData = localMatch;
    }

    if (!saveData) {
        const serverResult = await loadSaveFromServer(slotName);
        if (serverResult && serverResult.status === "ok") {
            saveData = serverResult;
            saveToLocal(slotName, saveData);
        }
    }

    if (!saveData) {
        appendOutput(`<span class="error">ERROR: Could not load save "${slotName}"</span>`, "line error");
        return;
    }

    output.innerHTML = "";
    hideChoices();
    genreSelector.style.display = "none";
    clearBoot();

    gameState = {
        genre: saveData.genre || "fantasy",
        step: saveData.step || 0,
        health: saveData.health || 100,
        history: saveData.history || [],
        gameActive: !saveData.game_over,
        saveSlot: slotName
    };

    updateHealth(gameState.health);

    appendOutput(
        `<span class="narrator-prefix">> RESUMING: ${slotName} (${gameState.genre.toUpperCase()}, Step ${gameState.step})</span>`,
        "line amber"
    );

    if (gameState.history.length > 0) {
        const lastNarrator = [...gameState.history].reverse().find(h => h.role === "narrator");
        if (lastNarrator) {
            const storyEl = document.createElement("div");
            storyEl.className = "story-text";
            storyEl.textContent = lastNarrator.text;
            output.appendChild(storyEl);
        }
    }

    if (saveData.game_over) {
        endGame({ health: gameState.health });
    } else {
        const lastNode = gameState.history.length > 0
            ? gameState.history[gameState.history.length - 1]
            : null;

        try {
            const resp = await fetch(`${GRADIO_CLIENT_URL}/api/game/choice`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    choice: "(resuming journey)",
                    genre: gameState.genre,
                    step: gameState.step,
                    health: gameState.health,
                    history: gameState.history
                })
            });
            const data = await resp.json();

            gameState.step = data.step || gameState.step;
            gameState.history = data.history || gameState.history;
            updateHealth(data.health ?? gameState.health);

            if (data.story && data.story !== lastNarrator?.text) {
                const storyEl = document.createElement("div");
                storyEl.className = "story-text";
                storyEl.textContent = data.story;
                output.appendChild(storyEl);
            }

            if (data.audio_url) {
                playTtsAudio(data.audio_url);
            }

            if (data.game_over) {
                endGame(data);
            } else if (data.choices && data.choices.length > 0) {
                showChoices(data.choices);
            }
        } catch {
            showChoices(["Continue onward", "Look around", "Rest"]);
        }
    }

    scrollToBottom();
}

// ---------------------------------------------------------------------------
// Resume Buttons on Genre Selector
// ---------------------------------------------------------------------------
async function loadResumeButtons() {
    const existing = genreSelector.querySelector(".resume-section");
    if (existing) existing.remove();

    const saves = await fetchSaves();
    if (saves.length === 0) return;

    const section = document.createElement("div");
    section.className = "resume-section";
    section.innerHTML = '<div class="resume-header">◈ RESUME JOURNEY</div>';

    for (const save of saves.slice(0, 3)) {
        const btn = document.createElement("div");
        btn.className = "genre-option resume-option";
        const genreIcon = save.genre === "fantasy" ? "☼" : save.genre === "scifi" ? "◈" : "◆";
        const genreLabel = (save.genre || "").toUpperCase();
        btn.innerHTML = `
            <span class="icon">${genreIcon}</span>
            RESUME: ${save.slot_name}
            <span class="resume-meta">${genreLabel} · Step ${save.step} · HP ${save.health}</span>
        `;
        btn.addEventListener("click", () => loadSavedGame(save.slot_name));
        section.appendChild(btn);
    }

    genreSelector.appendChild(section);
}

// ---------------------------------------------------------------------------
// Exit Button
// ---------------------------------------------------------------------------
const exitBtn = document.getElementById("exit-btn");
if (exitBtn) {
    exitBtn.addEventListener("click", showSaveDialog);
}

if (savesBtn) {
    savesBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleSavesDropdown();
    });
}

document.addEventListener("click", (e) => {
    if (savesDropdown && !savesDropdown.contains(e.target) && e.target !== savesBtn) {
        savesDropdown.style.display = "none";
    }
});

// ---------------------------------------------------------------------------
// Event Listeners
// ---------------------------------------------------------------------------
document.querySelectorAll(".genre-option").forEach(el => {
    el.addEventListener("click", () => {
        if (el.classList.contains("resume-option")) return;
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
// User Config Modal
// ---------------------------------------------------------------------------
const configBtn = document.getElementById('config-btn');
const configModal = document.getElementById('tb-config-modal');
const configClose = document.getElementById('tb-config-close');
const configSave = document.getElementById('tb-config-save');
const modelInput = document.getElementById('tb-model-input');
const tokenInput = document.getElementById('tb-token-input');
const endpointInput = document.getElementById('tb-endpoint-input');
const configStatus = document.getElementById('tb-config-status');

if (configBtn && configModal) {
    configBtn.addEventListener('click', async () => {
        const cfg = await fetch('/api/config').then(r => r.json());
        modelInput.value = cfg.model || '';
        tokenInput.value = '';
        if (endpointInput) {
            endpointInput.value = cfg.custom_endpoint || '';
        }
        configStatus.textContent = '';
        configModal.style.display = 'flex';
    });

    configClose.addEventListener('click', () => {
        configModal.style.display = 'none';
    });

    configModal.addEventListener('click', (e) => {
        if (e.target === configModal) configModal.style.display = 'none';
    });

    configSave.addEventListener('click', async () => {
        const body = {};
        // We always pass these fields to let user clear them (by passing empty strings or letting backend handle them)
        body.model = modelInput.value.trim() || "";
        body.hf_token = tokenInput.value.trim() || "";
        if (endpointInput) {
            body.custom_endpoint = endpointInput.value.trim() || "";
        }

        const resp = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await resp.json();
        configStatus.textContent = data.status === 'ok' ? '✓ Saved' : '✗ Failed';
        configStatus.style.color = data.status === 'ok' ? 'var(--asp-sun)' : 'var(--asp-ember)';
        setTimeout(() => { configModal.style.display = 'none'; }, 800);
    });
}

// Boot
(async () => {
    await checkModelStatus();
    await loadResumeButtons();
})();

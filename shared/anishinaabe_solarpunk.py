"""
ᐴ ANISHINAABE-SOLARPUNK DESIGN TOKENS ᔔ
═════════════════════════════════════════════════════════════════════════════════
Shared aesthetic module for the build-small-hackathon monorepo.

Combines:
- Anishinaabe cultural elements (Canadian Aboriginal Syllabics, medicine wheel
  motifs, natural color references from Anishinaabe Aki / land)
- Solarpunk visual language (warm sun tones, biophilic greens, sky blues,
  hope, low-tech, regenerative)

Each project imports PALETTE / SYMBOLS / HEADER / FOOTER to render a consistent
aesthetic across TinyBard, FocusFriend, and CritterCalm.
"""

# ── CANADIAN ABORIGINAL SYLLABICS ──────────────────────────────────────────────
PUU = "\u1438"   # ᐸ CANADIAN SYLLABICS PUU (left frame)
SHOO = "\u1514"  # ᔔ CANADIAN SYLLABICS SHOO (right frame)
BII = "\u142A"   # ᐪ CANADIAN SYLLABICS BII
MII = "\u14A1"   # ᑡ CANADIAN SYLLABICS MII (sometimes used in greetings)
WA = "\u1418"    # ᐘ CANADIAN SYLLABICS WA
GO = "\u1472"    # ᑲ CANADIAN SYLLABICS KA
AN = "\u14B0"    # ᒐ CANADIAN SYLLABICS AN (short)
KITA = "\u13E3"  # Ꮳ CANADIAN SYLLABICS C — used in "Anishinaabe"

# ── SOLARPUNK / NATURE MOTIFS ──────────────────────────────────────────────────
SUN_RAY = "\u263C"   # ☼ WHITE SUN WITH RAYS
SUN_BLACK = "\u2600" # ☀ BLACK SUN WITH RAYS
LEAF = "\u2618"      # ☘ SHAMROCK (biophilic stand-in)
FLOWER = "\u2740"    # ❀ WHITE FLORETTE
MEDICINE_WHEEL = "\u2697" # ⚗ alembic; rotated medicine wheel feel
ARROW_UP = "\u21B3"  # ↳ arrow (solarpunk hope = rising)
CIRCUIT = "\u25C8"   # ◈ WHITE DIAMOND CONTAINING BLACK SMALL DIAMOND
DIAMOND = "\u25C6"   # ◆ BLACK DIAMOND
DIAMOND_O = "\u25C7" # ◇ WHITE DIAMOND

# ── COLOR PALETTE ──────────────────────────────────────────────────────────────
PALETTE = {
    # Sky and water
    "sky":       "#5BA4D9",  # light Anishinaabe sky (morning)
    "water":     "#1B4965",  # deep lake water (Gichigami)
    "ice":       "#BEE9E8",  # spring thaw
    "frost":     "#CAF0F8",  # winter light
    # Sun
    "sun":       "#F2A93B",  # rising sun amber
    "sunlight":  "#FFB347",  # warm ray
    "ember":     "#E76F51",  # dusk ember
    # Earth
    "birch":     "#F5F1E8",  # birchbark white
    "terracotta":"#C8553D",  # clay / medicine wheel red
    "earth":     "#8B3A1F",  # deep earth / copper
    "moss":      "#588157",  # forest moss
    "forest":    "#3D6A4A",  # cedar forest
    "spruce":    "#1B4332",  # deep spruce (night)
    # Contrast
    "night":     "#0F1A2C",  # deep night sky
    "ash":       "#3A2E2A",  # woodsmoke
    "stone":     "#A89F91",  # river stone
    "ink":       "#1A1F2E",  # deep ink
}

# ── PROJECT FRAMING ───────────────────────────────────────────────────────────
def header(title: str, en: str) -> str:
    """Solarpunk + Anishinaabe banner header for a project.

    Usage:
        header("TinyBard", "MICRO TEXT ADVENTURE")
    """
    line = f"{DIAMOND}{CIRCUIT}{DIAMOND_O}"
    return (
        f"\n{line}{CIRCUIT}{PUU} {title} {SHOO} [{en.upper()}] "
        f"{CIRCUIT}{line}\n"
    )


def footer() -> str:
    """Closing banner."""
    return f"\n{DIAMOND_O}{CIRCUIT}{DIAMOND} {SUN_RAY} \u00b7 {LEAF} \u00b7 {WATER_ICON()} \u00b7 {SUN_BLACK} {CIRCUIT}{DIAMOND}{DIAMOND_O}\n"


def WATER_ICON() -> str:
    # wave-like water (using box-drawing)
    return "\u2248"  # ≈ (approx, like a wave)


# ── THEME CONSTANTS (CSS variables) ──────────────────────────────────────────
CSS_VARS = f"""
:root {{
  --asp-sky:       {PALETTE['sky']};
  --asp-water:     {PALETTE['water']};
  --asp-ice:       {PALETTE['ice']};
  --asp-sun:       {PALETTE['sun']};
  --asp-sunlight:  {PALETTE['sunlight']};
  --asp-ember:     {PALETTE['ember']};
  --asp-birch:     {PALETTE['birch']};
  --asp-terra:     {PALETTE['terracotta']};
  --asp-earth:     {PALETTE['earth']};
  --asp-moss:      {PALETTE['moss']};
  --asp-forest:    {PALETTE['forest']};
  --asp-spruce:    {PALETTE['spruce']};
  --asp-night:     {PALETTE['night']};
  --asp-ash:       {PALETTE['ash']};
  --asp-stone:     {PALETTE['stone']};
  --asp-ink:       {PALETTE['ink']};
}}
"""


# ── SHARED CSS SNIPPETS ───────────────────────────────────────────────────────
def style_banner() -> str:
    """A standard top-of-app banner with Anishinaabe + Solarpunk styling."""
    return """
/* === ANISHINAABE-SOLARPUNK BANNER =================================== */
.asp-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6em;
  padding: 14px 18px;
  background: linear-gradient(95deg, var(--asp-sky) 0%, var(--asp-water) 100%);
  color: var(--asp-birch);
  border-bottom: 1px solid rgba(255, 179, 71, 0.35);
  font-family: Georgia, 'Iowan Old Style', serif;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(15, 26, 44, 0.35);
}
.asp-banner .syll { font-size: 1.4em; opacity: 0.85; }
.asp-banner .title { font-size: 1.05em; font-weight: 600; }
.asp-banner .glyph {
  display: inline-block;
  transform: translateY(-1px);
  font-size: 1.1em;
  color: var(--asp-sunlight);
}
/* ===================================================================== */
"""


# ── WELCOME TEXT ──────────────────────────────────────────────────────────────
WELCOME = (
    f"{PUU} Aaniin {SHOO} \u2014 Welcome. The land remembers you. "
    f"{SUN_RAY} {LEAF} {WATER_ICON()}"
)


# ── CHARACTER (TinyBard, FocusFriend) ────────────────────────────────────────
PIP_GREETING_SOLARPUNK = (
    f"{PUU} Aaniin, amiikwens {SHOO} \u2014 I am Pip, the friend of the moss "
    f"and the small winds. Sit. Breathe. The sun is in no hurry. {SUN_BLACK}"
)


if __name__ == "__main__":
    print(header("Build Small Hackathon", "AINISH CODER SANCTUARY"))
    print(WELCOME)
    print(PIP_GREETING_SOLARPUNK)
    print(footer())

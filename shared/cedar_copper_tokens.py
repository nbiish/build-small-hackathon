"""
Cedar-Copper Design Tokens
============================
Shared palette + decorative-glyph module for the build-small-hackathon monorepo.

Each project's own CSS/UI embeds the tokens it needs (this file is a
reference, not imported at runtime).

Decorative Unicode glyphs in this file are intentionally NOT used in HF
Spaces metadata — see llms.txt "HF Agents CLI" notes.
"""

# ── DECORATIVE GLYPHS (in-app banners, not HF metadata) ───────────────────────
PUU = "\u1438"   # ᐸ — left frame character
SHOO = "\u1514"  # ᔔ — right frame character
BII = "\u142A"   # ᐪ
MII = "\u14A1"   # ᑡ
WA = "\u1418"    # ᐘ
GO = "\u1472"    # ᑲ
AN = "\u14B0"    # ᒐ

SUN_RAY = "\u263C"   # ☼
SUN_BLACK = "\u2600" # ☀
LEAF = "\u2618"      # ☘
FLOWER = "\u2740"    # ❀
MEDICINE_WHEEL = "\u2697" # ⚗
ARROW_UP = "\u21B3"  # ↳
CIRCUIT = "\u25C8"   # ◈
DIAMOND = "\u25C6"   # ◆
DIAMOND_O = "\u25C7" # ◇

# ── COLOR PALETTE ──────────────────────────────────────────────────────────────
PALETTE = {
    # Sky and water
    "sky":       "#5BA4D9",  # light morning sky
    "water":     "#1B4965",  # deep lake water
    "ice":       "#BEE9E8",  # spring thaw
    "frost":     "#CAF0F8",  # winter light
    # Sun
    "sun":       "#F2A93B",  # rising sun amber
    "sunlight":  "#FFB347",  # warm ray
    "ember":     "#E76F51",  # dusk ember
    # Earth
    "birch":     "#F5F1E8",  # birchbark white
    "terracotta":"#C8553D",  # clay red
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
    """Cedar-copper banner header for a project.

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
    return "\u2248"  # ≈ (approx, like a wave)


# ── THEME CONSTANTS (CSS variables) ──────────────────────────────────────────
CSS_VARS = f"""
:root {{
  --cc-sky:       {PALETTE['sky']};
  --cc-water:     {PALETTE['water']};
  --cc-ice:       {PALETTE['ice']};
  --cc-sun:       {PALETTE['sun']};
  --cc-sunlight:  {PALETTE['sunlight']};
  --cc-ember:     {PALETTE['ember']};
  --cc-birch:     {PALETTE['birch']};
  --cc-terra:     {PALETTE['terracotta']};
  --cc-earth:     {PALETTE['earth']};
  --cc-moss:      {PALETTE['moss']};
  --cc-forest:    {PALETTE['forest']};
  --cc-spruce:    {PALETTE['spruce']};
  --cc-night:     {PALETTE['night']};
  --cc-ash:       {PALETTE['ash']};
  --cc-stone:     {PALETTE['stone']};
  --cc-ink:       {PALETTE['ink']};
}}
"""


# ── SHARED CSS SNIPPETS ───────────────────────────────────────────────────────
def style_banner() -> str:
    """A standard top-of-app banner with cedar-copper styling."""
    return """
/* === CEDAR-COPPER BANNER ============================================== */
.cc-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6em;
  padding: 14px 18px;
  background: linear-gradient(95deg, var(--cc-sky) 0%, var(--cc-water) 100%);
  color: var(--cc-birch);
  border-bottom: 1px solid rgba(255, 179, 71, 0.35);
  font-family: Georgia, 'Iowan Old Style', serif;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(15, 26, 44, 0.35);
}
.cc-banner .syll { font-size: 1.4em; opacity: 0.85; }
.cc-banner .title { font-size: 1.05em; font-weight: 600; }
.cc-banner .glyph {
  display: inline-block;
  transform: translateY(-1px);
  font-size: 1.1em;
  color: var(--cc-sunlight);
}
/* ===================================================================== */
"""


# ── WELCOME TEXT ──────────────────────────────────────────────────────────────
WELCOME = (
    f"{PUU} Welcome {SHOO} \u2014 The land remembers you. "
    f"{SUN_RAY} {LEAF} {WATER_ICON()}"
)


# ── CHARACTER (TinyBard, FocusFriend) ────────────────────────────────────────
PIP_GREETING_CEDAR_COPPER = (
    f"{PUU} Hello, friend {SHOO} \u2014 I am Pip, the friend of the moss "
    f"and the small winds. Sit. Breathe. The sun is in no hurry. {SUN_BLACK}"
)


if __name__ == "__main__":
    print(header("Build Small Hackathon", "CODER SANCTUARY"))
    print(WELCOME)
    print(PIP_GREETING_CEDAR_COPPER)
    print(footer())

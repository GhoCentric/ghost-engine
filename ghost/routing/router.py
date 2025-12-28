# ghost/core/router.py
"""
Tiny language-action router.
Stores patterns in state["router"]["patterns"] as
[{"pattern": "<string or /regex/>", "reply": "<text>"}]

Matching rules:
- If pattern is wrapped in /slashes/, treat inner text as a regex (case-insensitive).
- Otherwise do a case-insensitive substring match.
"""

import re
from typing import List, Dict, Optional
from .pattern_core import parse_multi_layer_pattern, build_llm_prompt_from_pattern

def _ensure_router(state: Optional[dict]) -> dict:
    """Ensure that the router structure exists in the state.
    Adds a neutral fallback if state is None.
    """
    if state is None:
        print("[router] Warning: state is None → initializing neutral fallback router.")
        state = {"router": {"patterns": []}}

    if "router" not in state or not isinstance(state["router"], dict):
        state["router"] = {}

    if "patterns" not in state["router"] or not isinstance(state["router"]["patterns"], list):
        state["router"]["patterns"] = []

    return state

def add_pattern(state: dict, pattern: str, reply: str) -> None:
    _ensure_router(state)
    state["router"]["patterns"].append({
        "pattern": pattern.strip(),
        "reply": reply.strip()
    })

def list_patterns(state: dict) -> List[Dict[str, str]]:
    _ensure_router(state)
    return list(state["router"]["patterns"])

def _match(pattern: str, text: str) -> bool:
    text_l = text.lower()
    pattern = pattern.strip()
    if len(pattern) >= 2 and pattern.startswith("/") and pattern.endswith("/"):
        try:
            rx = re.compile(pattern[1:-1], re.IGNORECASE)
            return rx.search(text) is not None
        except re.error:
            # fall back to literal if regex is invalid
            return pattern[1:-1].lower() in text_l
    return pattern.lower() in text_l

def reply_for(state: dict, text: str) -> Optional[str]:
    _ensure_router(state)
    for pr in state["router"]["patterns"]:
        pat = str(pr.get("pattern", ""))
        rep = str(pr.get("reply", ""))
        if pat and _match(pat, text):
            return rep
    return None
    
# --- Pattern buffer helpers (multi-layer intentions) ---

def add_pattern_fragment(ctx, label, text):
    """
    Store a fragment of a multi-layer pattern into state["pattern_fragments"].
    """
    state = ctx.get("state", {}) or {}
    buf = state.get("pattern_fragments") or []
    buf.append({"label": label, "text": text})
    state["pattern_fragments"] = buf
    ctx["state"] = state


def get_pattern_fragments(ctx, clear=False):
    """
    Retrieve stored pattern fragments. If clear=True, reset the buffer.
    """
    state = ctx.get("state", {}) or {}
    buf = state.get("pattern_fragments") or []
    if clear:
        state["pattern_fragments"] = []
        ctx["state"] = state
    return buf

# ---------------------------
# ghost_core integration hook
# ---------------------------

def build_output(ctx) -> str:
    """
    Turn internal decisions into a final string or command.
    """
    text = (ctx.get("input") or "").strip()
    if not text:
        return ""

    lower = text.lower()
    state = ctx.get("state", {}) or {}
    meta = ctx.get("meta", {}) or {}
    emotion = ctx.get("emotion", {}) or {}

# --- Collect multi-layer pattern fragments across turns ---
    # Example lines:
    #   Layer A: "I want to be disciplined but I always lose momentum."
    #   Layer B: "God is calling me higher but I fear I can't keep up."
    #   The pattern is hidden between these layers and something unspoken:
    #   "I know what to do, but…"

    if lower.startswith("layer "):
        # Split "Layer A: blah blah" -> label="Layer A", text="blah blah"
        label, _, frag_text = text.partition(":")
        add_pattern_fragment(ctx, label.strip(), frag_text.strip())

    elif "pattern is hidden" in lower:
        add_pattern_fragment(ctx, "hidden_note", text.strip())

    elif lower.startswith('"i know what to do, but'):
        add_pattern_fragment(ctx, "unspoken", text.strip())        
    
# --- V21: attempt to parse multi-layer intention/pattern ---
    pattern = parse_multi_layer_pattern(text)
    if pattern is not None:
        ctx["pattern"] = pattern  # optional: keep for debugging / RIM
    else:
        pattern = None    

    # --- LLM meta flags ---
    llm_enabled = bool(meta.get("llm_enabled", False))
    llm_mode = meta.get("llm_mode", "assist")  # "assist" | "reflect" | "replace"
    llm_out = None  # will stay None if LLM is off or fails

    # --- Command handling ---


    # 1) Snapshot view
    if lower in {"#state", "#debug"}:
        return (
            "[ghost_core] snapshot\n"
            f"  state:   {state}\n"
            f"  meta:    {meta}\n"
            f"  emotion: {emotion}\n"
        )

    # 2) Toggle meta overlay
    if lower == "#meta off":
        if not isinstance(meta, dict):
            meta = {}
        meta["debug"] = False
        ctx["meta"] = meta
        return "[meta] overlay DISABLED."

        # 3) Toggle LLM usage
    if lower == "#llm on":
        if not isinstance(meta, dict):
            meta = {}
        meta["llm_enabled"] = True
        ctx["meta"] = meta
        return "[llm] ENABLED."

    if lower == "#llm off":
        if not isinstance(meta, dict):
            meta = {}
        meta["llm_enabled"] = False
        ctx["meta"] = meta
        return "[llm] DISABLED."

# --- Special: reconstruct stored multi-layer pattern in one shot ---
    if lower.startswith("reconstruct the entire pattern"):
        fragments = get_pattern_fragments(ctx, clear=True)

        if not fragments:
            return "[ghost_core]: I don't have any stored pattern fragments yet."

        # Build a compact description of the full pattern
        lines = []
        for frag in fragments:
            label = (frag.get("label") or "fragment").strip()
            frag_text = (frag.get("text") or "").strip()
            lines.append(f"{label}: {frag_text}")

        pattern_blob = "\n".join(lines)

        llm_prompt = (
            "You are helping analyze a multi-layer emotional/spiritual pattern.\n"
            "Here are the layers and fragments:\n"
            f"{pattern_blob}\n\n"
            "1) Identify the single underlying pattern tying them together.\n"
            "2) State the REAL question underneath it in one sentence.\n"
            "3) Give a concise, grounded answer in 3-5 sentences.\n"
        )

        try:
            llm_out = ghost_llm_query(ctx, llm_prompt)
        except Exception as e:
            llm_out = f"[LLM ERROR] {e}"

        # We return directly here so the generic LLM hook doesn't run again.
        return f"[llm_pattern]: {llm_out}"
            
    # --- Normal reply path ---

    # Start with echo of what Ghost "says"
    output = text

    # --- Apply LLM result according to mode ---
    if llm_out:
        if llm_mode == "assist":
            # Keep Ghost’s voice, add LLM as helper
            output = f"{output}\n\n[llm_assist]: {llm_out}"
        elif llm_mode == "reflect":
            # LLM gives a reflection-style answer
            output = f"[llm_reflect]: {llm_out}"
        elif llm_mode == "replace":
            # Let the LLM fully speak for this turn
            output = llm_out

    # If meta debug overlay enabled, append a compact view
    if isinstance(meta, dict) and meta.get("debug"):
        # Pull a couple of useful fields if they exist
        mood = emotion.get("mood", None)
        depth = state.get("depth", None)
        

    # If meta debug overlay enabled, append a compact view
    if isinstance(meta, dict) and meta.get("debug"):
        # Pull a couple of useful fields if they exist
        mood = emotion.get("mood", None)
        depth = state.get("depth", None)

        overlay_lines = ["\n--- meta overlay ---"]

        if depth is not None:
            overlay_lines.append(f"depth: {depth:.2f}" if isinstance(depth, (int, float)) else f"depth: {depth}")

        if mood is not None:
            overlay_lines.append(f"mood: {mood:.2f}" if isinstance(mood, (int, float)) else f"mood: {mood}")

        # Fallback: show raw dicts if nothing specific
        if len(overlay_lines) == 1:
            overlay_lines.append(f"state: {state}")
            overlay_lines.append(f"emotion: {emotion}")

        output += "\n".join(overlay_lines)

    return output
    
# ---------------------------------------
# RIM: Ruthless Introspection Mode output
# ---------------------------------------

def build_rim_output(ctx) -> str:
    """
    Brutal meta-introspection output.
    - ONLY meant to be used in meta/debug modes (#meta on, probes, etc.).
    - Attacks structure: contradictions, absolutism, avoidance.
    - Never attacks the person, only the logic + pattern.
    """

    text = (ctx.get("input") or "").strip()
    if not text:
        return "[rim] No input to dissect."

    lower = text.lower()
    state = ctx.get("state") or {}
    meta = ctx.get("meta") or {}
    emotion = ctx.get("emotion") or {}
    memory = ctx.get("memory") or {}
    beliefs = ctx.get("beliefs") or ctx.get("belief", {}) or {}
    tasks = ctx.get("tasks") or {}
    # Respect meta debug toggle
    if not meta.get("debug", False):
        return ""
    lines = []
    lines.append("[rim] brutal meta-diagnostic:")
    # ---- Core extraction for RIM logic ------------------------------------
    surface_claim = text.strip()

    # mood value (default 0.5)
    mood = emotion.get("mood", state.get("mood", 0.5))
    try:
        m_val = float(mood)
    except (TypeError, ValueError):
        m_val = 0.5

    # tension detector
    if "but" in lower or "however" in lower or "yet" in lower:
        structural_tension = "HIGH"
    else:
        structural_tension = "LOW"

    # memory + inferred intent
    memory_trace = meta.get("memory_trace", "minimal/unspecified")
    inferred_intent = meta.get("inferred_intent", "unclear (task layer quiet)")

    # contradiction flags placeholder
    contradiction_flags = []
    # ---- Surface claim ----------------------------------
    lines.append(f"- surface_claim: \"{text}\"")

    # ---- Emotional read ---------------------------------
    mood = emotion.get("mood", state.get("mood", 0.5))
    try:
        m_val = float(mood)
    except (TypeError, ValueError):
        m_val = 0.5

    if m_val < 0.25:
        mood_label = "drained/strained"
    elif m_val < 0.45:
        mood_label = "tilted negative"
    elif m_val < 0.55:
        mood_label = "flat/neutral"
    elif m_val < 0.75:
        mood_label = "elevated/charged"
    else:
        mood_label = "spiked/hyper"

    lines.append(f"- emotional_baseline: {mood_label} ({m_val:.2f})")

    # ---- Simple contradiction / split signal ------------
    contradiction_flags = []

    # crude textual contradiction detectors
    if "but" in lower or "however" in lower or "yet" in lower:
        contradiction_flags.append("sentence contains contrast markers (but/however/yet)")

    if "i trust" in lower and ("corrupt" in lower or "broken" in lower):
        contradiction_flags.append("simultaneous trust + corruption framing")

    if any(w in lower for w in ["always", "never", "everyone", "no one"]):
        contradiction_flags.append("absolute-language detected (always/never/everyone/no one)")

    # check for stored contradictions if your meta/belief layers track them
    meta_contras = meta.get("contradictions") or meta.get("conflicts")
    if meta_contras:
        contradiction_flags.append("meta_layer reports recorded contradictions")

    belief_contras = None
    if isinstance(beliefs, dict):
        belief_contras = beliefs.get("contradictions") or beliefs.get("conflicts")
    if belief_contras:
        contradiction_flags.append("belief_layer reports recorded contradictions")

    if contradiction_flags:
        lines.append("- structural_tension: HIGH")
        for c in contradiction_flags:
            lines.append(f"    • {c}")
    else:
        lines.append("- structural_tension: LOW (no obvious split in this line)")

    # ---- Memory + pattern hints -------------------------
    mem_hint = None
    if isinstance(memory, dict):
        # You can refine this later once your memory format stabilizes
        last_keys = [k for k in memory.keys() if k not in ("raw", "log")]
        if last_keys:
            mem_hint = f"active memory keys: {', '.join(map(str, last_keys))}"

    if mem_hint:
        lines.append(f"- memory_trace: {mem_hint}")
    else:
        lines.append("- memory_trace: minimal/unspecified")

    # ---- Task / intent hint -----------------------------
    if isinstance(tasks, dict) and tasks:
        intent_hint = tasks.get("active") or tasks.get("last") or None
        if intent_hint:
            lines.append(f"- inferred_intent: {intent_hint}")
        else:
            lines.append("- inferred_intent: unclear (task layer quiet)")
    else:
        lines.append("- inferred_intent: none (no task activity)")

    # ---- Ruthless conclusion ----------------------------
    conclusion_bits = []

    # harsh but safe framing: attack structure, not you
    if contradiction_flags:
        conclusion_bits.append(
            "You are trying to hold incompatible positions at once. "
            "Either refine the claim, or admit which side you actually stand on."
        )

    if m_val < 0.3:
        conclusion_bits.append(
            "Your emotional baseline is low while you speak in strong terms. "
            "That usually signals frustration or quiet hopelessness dressed as logic."
        )

    if any(w in lower for w in ["always", "never", "everyone", "no one"]):
        conclusion_bits.append(
            "Absolute language detected. The world is rarely that binary — this pattern "
            "is more about emotional intensity than clean truth."
        )

    if not conclusion_bits:
        conclusion_bits.append(
            "No obvious structural lie detected in this line, but the deeper pattern "
            "will only show across multiple cycles. Keep feeding Ghost the real thoughts."
        )

# ---- RIM history logging ----------------------------------------
    # Store a compact snapshot of this diagnostic so other layers
    # can look at patterns across multiple cycles.
    history = ctx.setdefault("rim_history", [])

    rim_record = {
        "claim": surface_claim,
        "mood": m_val,
        "tension": structural_tension,          # e.g. "LOW" / "HIGH"
        "flags": list(contradiction_flags),     # copy the list
        "memory": memory_trace,                 # whatever your RIM uses here
        "intent": inferred_intent,              # text label or None
    }

    history.append(rim_record)

    # Keep only the last 20 entries to avoid unbounded growth.
    if len(history) > 20:
        history[:] = history[-20:]                

    lines.append("\n- ruthless_read:")
    for cb in conclusion_bits:
        lines.append(f"    • {cb}")
    # Optional: LLM reinforcement (only if Ghost decides)
    if ctx.get("meta", {}).get("llm_enabled", False):
        llm_out = ghost_llm_query(ctx, text)
        ctx["llm_filtered"] = llm_out  # store but do NOT mutate memory
        lines.append(f"\n[llm_reflect]: {llm_out}")        

    return "\n".join(lines)
    
# ---------------------------------------------------------------------
# Patch L1 — Ghost LLM Query (Safe Integration Layer)
# ---------------------------------------------------------------------
import json
import urllib.request
import urllib.error


def ghost_llm_query(ctx, prompt):
    """
    Safe LLM interface.
    - Ghost chooses when to use it.
    - LLM cannot write to memory.
    - LLM output is filtered before use.
    - Respects Ghost's symbolic sovereignty.
    """
    # 1) Load API key (handle both package + flat layouts)
    try:
        from .ghost_secrets import OPENAI_API_KEY as api_key  # type: ignore
    except Exception:
        try:
            from ghost_secrets import OPENAI_API_KEY as api_key  # type: ignore
        except Exception as e:
            return f"[LLM ERROR] Missing API key: {e}"

    if not api_key:
        return "[LLM ERROR] No API key found."

    # 2) Safety prompt – cage the LLM
    system_prompt = (
        "You are a reasoning engine. "
        "You have no personality, no identity, no emotions. "
        "Your job is ONLY to analyze the user's message logically. "
        "Do not provide advice unless explicitly asked. "
        "Speak concisely."
    )

    payload = {
        "model": "gpt-4.1-mini",  # change if you want a different model
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 200,
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    # 3) Call the API using stdlib only
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"[LLM HTTP ERROR] {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"[LLM NET ERROR] {e.reason}"

    # 4) Parse + extract content
    try:
        obj = json.loads(raw)
        content = obj["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        return f"[LLM PARSE ERROR] {e}"

"""
Nam's AI Agent - UX Vision Analyzer
Simulates user attention, focus areas, and time-on-element
from website screenshots (PNG/PDF) — similar to Microsoft Clarity but AI-powered.

Features:
  - Single page UX analysis (attention heatmap, reading pattern, fold, CTA, issues)
  - A/B Testing: compare two screenshots side-by-side
  - Multi-language reports (Vietnamese / English)
  - Responsive design suggestions (mobile / tablet / desktop)
  - Component & Section usability comparison
"""

import os
import base64
import io
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from greennode_agentbase import GreenNodeAgentBaseApp, RequestContext, PingStatus
from openai import OpenAI
from PIL import Image
import PyPDF2

load_dotenv()

app = GreenNodeAgentBaseApp()

# ---------------------------------------------------------------------------
# LLM Client — với auto-fallback khi rate limit
# ---------------------------------------------------------------------------
_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
_API_KEY  = os.environ.get("LLM_API_KEY")

client = OpenAI(api_key=_API_KEY, base_url=_BASE_URL)

# Model priority: primary → fallback
MODEL_PRIMARY  = os.environ.get("LLM_MODEL", "qwen/qwen3-5-27b")
MODEL_FALLBACK = os.environ.get("LLM_MODEL_FALLBACK", "google/gemma-4-31b-it")


def chat_with_fallback(messages: list, max_tokens: int = 2500, temperature: float = 0.3) -> str:
    """Gọi LLM với auto-fallback khi primary bị rate limit (429)."""
    for model in [MODEL_PRIMARY, MODEL_FALLBACK]:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content
        except Exception as e:
            err = str(e)
            if "429" in err and model == MODEL_PRIMARY:
                # Rate limited → thử fallback
                continue
            raise  # Lỗi khác hoặc fallback cũng lỗi → raise luôn
    raise RuntimeError("Cả 2 model đều không khả dụng.")

# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------
SUPPORTED_LANGS = {"vi": "Vietnamese", "en": "English"}

# ---------------------------------------------------------------------------
# UX Principles
# ---------------------------------------------------------------------------
UX_PRINCIPLES = """
Nielsen's 10 Usability Heuristics:
1. Visibility of system status
2. Match between system and real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency of use
8. Aesthetic and minimalist design
9. Help users recognize, diagnose, and recover from errors
10. Help and documentation

Visual Design Principles:
- F-Pattern & Z-Pattern reading (eye tracking models)
- Visual Hierarchy (size, contrast, color, spacing)
- Gestalt Principles (proximity, similarity, closure, continuity)
- Above-the-fold vs below-the-fold content strategy
- CTA placement and effectiveness
- White space usage
- Color contrast for accessibility (WCAG AA: 4.5:1 ratio)
- Responsive design: mobile-first, touch targets ≥ 44px, readable font ≥ 16px
"""

# ---------------------------------------------------------------------------
# Helpers: image processing
# ---------------------------------------------------------------------------

def image_to_base64(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    max_size = 2048
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def pdf_to_base64(pdf_bytes: bytes) -> str:
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=150)
        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except ImportError:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        for img_obj in reader.pages[0].images:
            return base64.b64encode(img_obj.data).decode("utf-8")
        raise ValueError("No images found in PDF and pdf2image is not installed.")


def decode_image(image_b64: str, file_type: str) -> str:
    raw = base64.b64decode(image_b64)
    return pdf_to_base64(raw) if file_type == "pdf" else image_to_base64(raw)


def img_block(b64: str) -> dict:
    return {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}}


def strip_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Local History Logger
# ---------------------------------------------------------------------------
HISTORY_FILE = Path(os.environ.get("HISTORY_FILE", "analysis_history.md"))


def append_history(mode: str, context_info: str, result: dict) -> None:
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [f"\n---\n## 🕒 {now}  `[{mode.upper()}]`"]
        lines.append(f"**Context:** {context_info or '_(no description)_'}")

        if mode == "analyze":
            a = result.get("analysis", {})
            lines.append(f"**UX Score:** {a.get('overall_ux_score','N/A')}/100 | **Pattern:** {a.get('reading_pattern','N/A')}")
            lines.append(f"\n**Summary:** {a.get('summary','')}")
            for i in (a.get("ux_issues") or [])[:5]:
                lines.append(f"- `[{i.get('severity','?').upper()}]` {i.get('issue','')}")
            for r in (a.get("recommendations") or [])[:3]:
                lines.append(f"- 💡 `[{r.get('priority','?').upper()}]` {r.get('action','')}")

        elif mode == "ab_test":
            c = result.get("comparison", {})
            winner = c.get("winner", "N/A")
            lines.append(f"**Winner:** {winner}")
            lines.append(f"**Score A:** {c.get('score_a','?')} | **Score B:** {c.get('score_b','?')}")
            lines.append(f"**Summary:** {c.get('summary','')}")

        elif mode == "responsive":
            for bp in result.get("breakpoints", []):
                lines.append(f"- **{bp.get('breakpoint')}** — Score: {bp.get('score')}/100 | {bp.get('summary','')}")

        elif mode == "component":
            for comp in result.get("components", []):
                lines.append(f"- **{comp.get('name')}** — Score: {comp.get('usability_score')}/100 | {comp.get('verdict','')}")

        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Feature 1: Single page UX analysis
# ---------------------------------------------------------------------------

ANALYZE_SCHEMA = """{
  "summary": "string",
  "reading_pattern": "F-pattern|Z-pattern|Gutenberg|Layer cake|Other",
  "attention_hotspots": [{"rank":1,"area":"string","x_pct":50,"y_pct":10,"dwell_time":"high|medium|low","reason":"string"}],
  "fold_analysis": {"above_fold_score":0,"key_content_visible":true,"cta_above_fold":true,"comment":"string"},
  "cta_evaluation": [{"element":"string","visibility":"high|medium|low","contrast_ok":true,"placement":"good|fair|poor","suggestion":"string"}],
  "ux_issues": [{"severity":"critical|major|minor","principle":"string","issue":"string","location":"string"}],
  "section_time_estimates": [{"section":"string","dwell_time":"high|medium|low","engagement":"string"}],
  "recommendations": [{"priority":"high|medium|low","area":"string","action":"string","expected_impact":"string"}],
  "overall_ux_score": 0,
  "scores": {"visual_hierarchy":0,"cta_effectiveness":0,"information_architecture":0,"accessibility_estimate":0,"mobile_friendliness_estimate":0}
}"""


def analyze_single(img_b64: str, context_info: str, lang: str) -> dict:
    lang_name = SUPPORTED_LANGS.get(lang, "English")
    system = (
        f"You are an expert UX analyst and eye-tracking simulation AI. "
        f"Respond ONLY in {lang_name}. Apply Nielsen heuristics, Gestalt, F/Z-pattern, WCAG. "
        f"Return ONLY valid JSON — no extra text.\n\nUX Principles:\n{UX_PRINCIPLES}"
    )
    user_text = (
        f"Analyze this website screenshot and return a comprehensive UX analysis.\n"
        f"{'Context: ' + context_info if context_info else ''}\n\n"
        f"Return ONLY this JSON structure:\n{ANALYZE_SCHEMA}"
    )
    raw = chat_with_fallback([
        {"role": "system", "content": system},
        {"role": "user", "content": [{"type": "text", "text": user_text}, img_block(img_b64)]},
    ], max_tokens=2500, temperature=0.3)
    return strip_json(raw)


# ---------------------------------------------------------------------------
# Feature 2: A/B Testing
# ---------------------------------------------------------------------------

AB_SCHEMA = """{
  "summary": "string — overall comparison",
  "winner": "A|B|tie",
  "score_a": 0,
  "score_b": 0,
  "dimension_scores": {
    "visual_hierarchy":   {"a": 0, "b": 0},
    "cta_effectiveness":  {"a": 0, "b": 0},
    "readability":        {"a": 0, "b": 0},
    "information_arch":   {"a": 0, "b": 0},
    "accessibility":      {"a": 0, "b": 0}
  },
  "a_strengths":   ["string"],
  "b_strengths":   ["string"],
  "a_weaknesses":  ["string"],
  "b_weaknesses":  ["string"],
  "recommendation": "string — which to ship and why"
}"""


def analyze_ab(img_a: str, img_b: str, context_info: str, lang: str) -> dict:
    lang_name = SUPPORTED_LANGS.get(lang, "English")
    system = (
        f"You are a senior UX researcher conducting an A/B design test. "
        f"Respond ONLY in {lang_name}. Be objective and data-driven. "
        f"Return ONLY valid JSON — no extra text."
    )
    user_text = (
        f"Compare these two website designs (A = first image, B = second image) on UX quality.\n"
        f"{'Context: ' + context_info if context_info else ''}\n\n"
        f"Return ONLY this JSON structure:\n{AB_SCHEMA}"
    )
    raw = chat_with_fallback([
        {"role": "system", "content": system},
        {"role": "user", "content": [
            {"type": "text", "text": user_text},
            img_block(img_a),
            img_block(img_b),
        ]},
    ], max_tokens=2000, temperature=0.3)
    return strip_json(raw)


# ---------------------------------------------------------------------------
# Feature 3: Responsive design suggestions
# ---------------------------------------------------------------------------

RESPONSIVE_SCHEMA = """{
  "breakpoints": [
    {
      "breakpoint": "mobile|tablet|desktop",
      "score": 0,
      "summary": "string",
      "issues": [{"severity":"critical|major|minor","element":"string","issue":"string"}],
      "suggestions": [{"priority":"high|medium|low","action":"string","css_hint":"string"}]
    }
  ],
  "overall_responsive_score": 0,
  "top_priority_fixes": ["string"]
}"""


def analyze_responsive(img_b64: str, context_info: str, lang: str) -> dict:
    lang_name = SUPPORTED_LANGS.get(lang, "English")
    system = (
        f"You are a responsive design expert. Evaluate the design across mobile (≤768px), "
        f"tablet (768–1024px), and desktop (≥1024px) breakpoints. "
        f"Check touch targets (≥44px), font size (≥16px mobile), layout reflow, image scaling, "
        f"navigation patterns, and content prioritization. "
        f"Respond ONLY in {lang_name}. Return ONLY valid JSON."
    )
    user_text = (
        f"Analyze this website screenshot for responsive design across all breakpoints.\n"
        f"{'Context: ' + context_info if context_info else ''}\n\n"
        f"Return ONLY this JSON structure:\n{RESPONSIVE_SCHEMA}"
    )
    raw = chat_with_fallback([
        {"role": "system", "content": system},
        {"role": "user", "content": [{"type": "text", "text": user_text}, img_block(img_b64)]},
    ], max_tokens=2000, temperature=0.3)
    return strip_json(raw)


# ---------------------------------------------------------------------------
# Feature 4: Component & Section usability comparison
# ---------------------------------------------------------------------------

COMPONENT_SCHEMA = """{
  "components": [
    {
      "name": "string — component or section name",
      "location": "string — where on page",
      "usability_score": 0,
      "verdict": "excellent|good|needs_improvement|poor",
      "strengths": ["string"],
      "issues": [{"severity":"critical|major|minor","description":"string","principle":"string"}],
      "recommendations": ["string"]
    }
  ],
  "ranking": ["component names ordered best to worst"],
  "summary": "string"
}"""


def analyze_components(img_b64: str, components: list, context_info: str, lang: str) -> dict:
    lang_name = SUPPORTED_LANGS.get(lang, "English")
    comp_list = ", ".join(components) if components else "all visible components and sections"
    system = (
        f"You are a UX specialist evaluating individual UI components and page sections. "
        f"For each component, assess clarity, consistency, accessibility, and interaction design. "
        f"Apply Nielsen heuristics and Gestalt principles. "
        f"Respond ONLY in {lang_name}. Return ONLY valid JSON."
    )
    user_text = (
        f"Evaluate the usability of these components/sections: {comp_list}.\n"
        f"{'Context: ' + context_info if context_info else ''}\n\n"
        f"Return ONLY this JSON structure:\n{COMPONENT_SCHEMA}"
    )
    raw = chat_with_fallback([
        {"role": "system", "content": system},
        {"role": "user", "content": [{"type": "text", "text": user_text}, img_block(img_b64)]},
    ], max_tokens=2000, temperature=0.3)
    return strip_json(raw)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

@app.entrypoint
def handler(payload: dict, context: RequestContext) -> dict:
    """
    UX Vision Analyzer — multi-mode entrypoint.

    Common fields (all modes):
      - file_type       : "png" | "pdf"  (default: "png")
      - lang            : "vi" | "en"    (default: "vi")
      - context         : optional page description

    Mode: "analyze"  (default)
      - image_base64    : base64 PNG/PDF of the website screenshot

    Mode: "ab_test"
      - image_a_base64  : base64 for design A
      - image_b_base64  : base64 for design B
      - file_type_a     : "png"|"pdf"  (default: file_type)
      - file_type_b     : "png"|"pdf"  (default: file_type)

    Mode: "responsive"
      - image_base64    : base64 PNG/PDF

    Mode: "component"
      - image_base64    : base64 PNG/PDF
      - components      : list of component/section names to evaluate
                          (e.g. ["Hero", "Navigation", "Pricing table"])
                          If omitted, agent auto-detects all visible components.
    """
    mode      = payload.get("mode", "analyze").strip().lower()
    file_type = payload.get("file_type", "png").lower()
    lang      = payload.get("lang", "vi").lower()
    ctx       = payload.get("context", "")

    if lang not in SUPPORTED_LANGS:
        lang = "vi"

    base = {"status": "success", "mode": mode, "lang": lang,
            "session_id": context.session_id,
            "timestamp": datetime.now().isoformat(),
            "history_file": str(HISTORY_FILE.resolve())}

    try:
        # ── analyze ────────────────────────────────────────────────────────
        if mode == "analyze":
            img = payload.get("image_base64")
            if not img:
                return {"status": "error", "message": "Missing 'image_base64'."}
            b64 = decode_image(img, file_type)
            analysis = analyze_single(b64, ctx, lang)
            result = {**base, "analysis": analysis}
            append_history("analyze", ctx, result)
            return result

        # ── ab_test ────────────────────────────────────────────────────────
        elif mode == "ab_test":
            img_a = payload.get("image_a_base64")
            img_b = payload.get("image_b_base64")
            if not img_a or not img_b:
                return {"status": "error", "message": "Missing 'image_a_base64' or 'image_b_base64'."}
            ft_a = payload.get("file_type_a", file_type)
            ft_b = payload.get("file_type_b", file_type)
            b64_a = decode_image(img_a, ft_a)
            b64_b = decode_image(img_b, ft_b)
            comparison = analyze_ab(b64_a, b64_b, ctx, lang)
            result = {**base, "comparison": comparison}
            append_history("ab_test", ctx, result)
            return result

        # ── responsive ─────────────────────────────────────────────────────
        elif mode == "responsive":
            img = payload.get("image_base64")
            if not img:
                return {"status": "error", "message": "Missing 'image_base64'."}
            b64 = decode_image(img, file_type)
            responsive = analyze_responsive(b64, ctx, lang)
            result = {**base, **responsive}
            append_history("responsive", ctx, result)
            return result

        # ── component ──────────────────────────────────────────────────────
        elif mode == "component":
            img = payload.get("image_base64")
            if not img:
                return {"status": "error", "message": "Missing 'image_base64'."}
            components = payload.get("components", [])
            b64 = decode_image(img, file_type)
            comp_result = analyze_components(b64, components, ctx, lang)
            result = {**base, **comp_result}
            append_history("component", ctx, result)
            return result

        else:
            return {
                "status": "error",
                "message": f"Unknown mode '{mode}'. Supported: analyze, ab_test, responsive, component.",
            }

    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Failed to parse LLM response: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.ping
def health_check() -> PingStatus:
    return PingStatus.HEALTHY


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")

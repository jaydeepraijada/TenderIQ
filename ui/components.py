import streamlit as st

# Inline-style helpers — all colors use either Streamlit CSS vars or
# semi-transparent rgba so they render correctly in both light and dark mode.

_BADGE = (
    'display:inline-flex;align-items:center;gap:4px;padding:3px 10px;'
    'border-radius:20px;font-size:0.78rem;font-weight:600;'
    'white-space:nowrap;line-height:1.4;'
)


def verdict_pill(verdict: str) -> str:
    cfg = {
        "eligible":     ("rgba(34,197,94,0.15)",   "#22C55E", "✅ Eligible"),
        "not_eligible": ("rgba(239,68,68,0.15)",    "#EF4444", "❌ Not Eligible"),
        "needs_review": ("rgba(245,158,11,0.15)",   "#F59E0B", "⚠️ Needs Review"),
    }
    bg, fg, label = cfg.get(verdict, ("rgba(128,128,128,0.1)", "var(--text-color)", verdict))
    return (f'<span style="{_BADGE}background:{bg};color:{fg};'
            f'border:1px solid {fg}33;">{label}</span>')


def category_badge(category: str) -> str:
    cfg = {
        "financial":  ("rgba(37,99,235,0.12)",  "#3B82F6", "💰 Financial"),
        "technical":  ("rgba(34,197,94,0.12)",  "#22C55E", "🔧 Technical"),
        "compliance": ("rgba(245,158,11,0.12)", "#F59E0B", "📋 Compliance"),
    }
    bg, fg, label = cfg.get(category, ("rgba(128,128,128,0.1)", "var(--text-color)", category))
    return (f'<span style="{_BADGE}background:{bg};color:{fg};'
            f'border:1px solid {fg}33;">{label}</span>')


def ocr_tier_badge(source_type: str) -> str:
    cfg = {
        "text_pdf":   ("rgba(100,116,139,0.12)", "#94A3B8", "📄 Typed PDF"),
        "tesseract":  ("rgba(124,58,237,0.12)",  "#8B5CF6", "🔍 Tesseract"),
        "vision_llm": ("rgba(234,88,12,0.12)",   "#F97316", "👁 Vision LLM"),
    }
    bg, fg, label = cfg.get(source_type, ("rgba(128,128,128,0.1)", "var(--text-color)", source_type))
    return (f'<span style="{_BADGE}background:{bg};color:{fg};'
            f'border:1px solid {fg}33;">{label}</span>')


def mandatory_badge(mandatory: bool) -> str:
    if mandatory:
        return (f'<span style="{_BADGE}background:rgba(239,68,68,0.12);color:#EF4444;'
                f'border:1px solid #EF444433;">🔴 Mandatory</span>')
    return (f'<span style="{_BADGE}background:rgba(245,158,11,0.12);color:#F59E0B;'
            f'border:1px solid #F59E0B33;">🟡 Optional</span>')


def confidence_bar(value: float, label: str = "Confidence") -> None:
    pct = min(max(value, 0.0), 1.0)
    color = "#22C55E" if pct >= 0.80 else "#F59E0B" if pct >= 0.55 else "#EF4444"
    st.markdown(
        f"""<div style="margin:6px 0 10px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
    <span style="font-size:0.72rem;font-weight:600;color:var(--text-color);
                 opacity:0.5;text-transform:uppercase;letter-spacing:0.05em;">{label}</span>
    <span style="font-size:0.8rem;font-weight:700;color:{color};">{pct:.0%}</span>
  </div>
  <div style="background:rgba(128,128,128,0.15);border-radius:6px;height:6px;overflow:hidden;">
    <div style="width:{pct*100:.1f}%;background:{color};height:100%;border-radius:6px;"></div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


def stat_card(value: str | int, label: str, color: str = "#3B82F6") -> None:
    st.markdown(
        f"""<div style="background:var(--secondary-background-color);
                        border:1px solid rgba(128,128,128,0.2);border-radius:12px;
                        padding:20px 18px;text-align:center;">
  <div style="font-size:2rem;font-weight:800;color:{color};line-height:1.1;">{value}</div>
  <div style="font-size:0.7rem;font-weight:700;color:var(--text-color);opacity:0.45;
              margin-top:5px;text-transform:uppercase;letter-spacing:0.08em;">{label}</div>
</div>""",
        unsafe_allow_html=True,
    )

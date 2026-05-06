import streamlit as st


def verdict_pill(verdict: str) -> str:
    cfg = {
        "eligible":     ("tiq-eligible",  "✅ Eligible"),
        "not_eligible": ("tiq-not-elig",  "❌ Not Eligible"),
        "needs_review": ("tiq-review",    "⚠️ Needs Review"),
    }
    cls, label = cfg.get(verdict, ("tiq-review", verdict))
    return f'<span class="tiq-badge {cls}">{label}</span>'


def category_badge(category: str) -> str:
    cfg = {
        "financial":  ("tiq-cat-fin",  "💰 Financial"),
        "technical":  ("tiq-cat-tech", "🔧 Technical"),
        "compliance": ("tiq-cat-comp", "📋 Compliance"),
    }
    cls, label = cfg.get(category, ("tiq-cat-comp", category))
    return f'<span class="tiq-badge {cls}">{label}</span>'


def ocr_tier_badge(source_type: str) -> str:
    cfg = {
        "text_pdf":   ("tiq-ocr-text",   "📄 Typed PDF"),
        "tesseract":  ("tiq-ocr-tess",   "🔍 Tesseract"),
        "vision_llm": ("tiq-ocr-vision", "👁 Vision LLM"),
    }
    cls, label = cfg.get(source_type, ("tiq-ocr-text", source_type))
    return f'<span class="tiq-badge {cls}">{label}</span>'


def mandatory_badge(mandatory: bool) -> str:
    if mandatory:
        return '<span class="tiq-badge tiq-mand">🔴 Mandatory</span>'
    return '<span class="tiq-badge tiq-optional">🟡 Optional</span>'


def confidence_bar(value: float, label: str = "Confidence") -> None:
    pct = min(max(value, 0.0), 1.0)
    color = "#22C55E" if pct >= 0.8 else "#F59E0B" if pct >= 0.55 else "#EF4444"
    st.markdown(
        f"""<div style="margin:4px 0 8px;">
        <div style="display:flex;justify-content:space-between;
                    font-size:0.75rem;color:#64748B;margin-bottom:3px;">
            <span>{label}</span><span style="font-weight:600;color:{color};">{pct:.0%}</span>
        </div>
        <div style="background:#E2E8F0;border-radius:6px;height:7px;overflow:hidden;">
            <div style="width:{pct*100:.1f}%;background:{color};
                        height:100%;border-radius:6px;
                        transition:width 0.4s ease;"></div>
        </div></div>""",
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="tiq-section-header">'
        f'<div style="font-size:1.1rem;font-weight:700;color:#0D1B2A;">{title}</div>'
        + (f'<div style="font-size:0.82rem;color:#64748B;margin-top:2px;">{subtitle}</div>' if subtitle else "")
        + "</div>",
        unsafe_allow_html=True,
    )

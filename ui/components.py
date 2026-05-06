import streamlit as st

# ── Inline-style badge helpers ────────────────────────────────────────────────
# Every function returns an HTML string with 100% inline styles.
# No CSS classes — reliable across all Streamlit markdown containers.

_BADGE = (
    'display:inline-flex;align-items:center;gap:4px;padding:3px 10px;'
    'border-radius:20px;font-size:0.78rem;font-weight:600;'
    'white-space:nowrap;font-family:Inter,sans-serif;line-height:1.4;'
)


def verdict_pill(verdict: str) -> str:
    cfg = {
        "eligible":     ("#D1FAE5", "#065F46", "#6EE7B7", "✅ Eligible"),
        "not_eligible": ("#FEE2E2", "#991B1B", "#FCA5A5", "❌ Not Eligible"),
        "needs_review": ("#FEF3C7", "#92400E", "#FCD34D", "⚠️ Needs Review"),
    }
    bg, fg, border, label = cfg.get(verdict, ("#F1F5F9", "#374151", "#CBD5E1", verdict))
    return (f'<span style="{_BADGE}background:{bg};color:{fg};'
            f'border:1px solid {border};">{label}</span>')


def category_badge(category: str) -> str:
    cfg = {
        "financial":  ("#DBEAFE", "#1E40AF", "#93C5FD", "💰 Financial"),
        "technical":  ("#DCFCE7", "#166534", "#86EFAC", "🔧 Technical"),
        "compliance": ("#FEF3C7", "#92400E", "#FCD34D", "📋 Compliance"),
    }
    bg, fg, border, label = cfg.get(category, ("#F1F5F9", "#374151", "#CBD5E1", category))
    return (f'<span style="{_BADGE}background:{bg};color:{fg};'
            f'border:1px solid {border};">{label}</span>')


def ocr_tier_badge(source_type: str) -> str:
    cfg = {
        "text_pdf":   ("#F1F5F9", "#475569", "#CBD5E1", "📄 Typed PDF"),
        "tesseract":  ("#F5F3FF", "#6D28D9", "#DDD6FE", "🔍 Tesseract"),
        "vision_llm": ("#FFF7ED", "#C2410C", "#FED7AA", "👁 Vision LLM"),
    }
    bg, fg, border, label = cfg.get(source_type, ("#F1F5F9", "#374151", "#CBD5E1", source_type))
    return (f'<span style="{_BADGE}background:{bg};color:{fg};'
            f'border:1px solid {border};">{label}</span>')


def mandatory_badge(mandatory: bool) -> str:
    if mandatory:
        return (f'<span style="{_BADGE}background:#FEE2E2;color:#991B1B;'
                f'border:1px solid #FCA5A5;">🔴 Mandatory</span>')
    return (f'<span style="{_BADGE}background:#FFFBEB;color:#92400E;'
            f'border:1px solid #FDE68A;">🟡 Optional</span>')


def confidence_bar(value: float, label: str = "Confidence") -> None:
    pct = min(max(value, 0.0), 1.0)
    if pct >= 0.80:
        bar_color, text_color = "#22C55E", "#166534"
    elif pct >= 0.55:
        bar_color, text_color = "#F59E0B", "#92400E"
    else:
        bar_color, text_color = "#EF4444", "#991B1B"

    st.markdown(
        f"""<div style="margin:6px 0 10px;">
  <div style="display:flex;justify-content:space-between;align-items:center;
              margin-bottom:4px;">
    <span style="font-size:0.72rem;font-weight:600;color:#94A3B8;
                 text-transform:uppercase;letter-spacing:0.05em;">{label}</span>
    <span style="font-size:0.8rem;font-weight:700;color:{text_color};">{pct:.0%}</span>
  </div>
  <div style="background:#F1F5F9;border-radius:6px;height:6px;overflow:hidden;">
    <div style="width:{pct*100:.1f}%;background:{bar_color};
                height:100%;border-radius:6px;transition:width 0.3s ease;"></div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


def stat_card(value: str | int, label: str, color: str = "#2563EB") -> None:
    st.markdown(
        f"""<div style="background:#fff;border:1px solid #E2E8F0;border-radius:12px;
                        padding:20px 18px;text-align:center;
                        box-shadow:0 1px 3px rgba(0,0,0,0.06);">
  <div style="font-size:2rem;font-weight:800;color:{color};
              font-family:Inter,sans-serif;line-height:1.1;">{value}</div>
  <div style="font-size:0.7rem;font-weight:700;color:#94A3B8;margin-top:5px;
              text-transform:uppercase;letter-spacing:0.08em;">{label}</div>
</div>""",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "") -> None:
    sub_html = (f'<p style="margin:6px 0 0;font-size:0.95rem;color:#64748B;'
                f'font-weight:400;">{subtitle}</p>') if subtitle else ""
    st.markdown(
        f"""<div style="margin-bottom:1.5rem;">
  <h1 style="margin:0;font-size:1.7rem;font-weight:800;color:#0D1B2A;
             font-family:Inter,sans-serif;letter-spacing:-0.02em;">{title}</h1>
  {sub_html}
</div>""",
        unsafe_allow_html=True,
    )

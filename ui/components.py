import streamlit as st


def verdict_pill(verdict: str) -> str:
    if verdict == "eligible":
        return ":green[✅ Eligible]"
    elif verdict == "not_eligible":
        return ":red[❌ Not Eligible]"
    else:
        return ":orange[⚠ Needs Review]"


def confidence_bar(value: float, label: str = "Confidence") -> None:
    st.progress(min(max(value, 0.0), 1.0), text=f"{label}: {value:.0%}")


def ocr_tier_badge(source_type: str) -> str:
    icons = {
        "text_pdf": "📄 text_pdf",
        "tesseract": "🔍 tesseract",
        "vision_llm": "👁 vision_llm",
    }
    return icons.get(source_type, f"❓ {source_type}")


def category_badge(category: str) -> str:
    if category == "financial":
        return ":blue[financial]"
    elif category == "technical":
        return ":green[technical]"
    elif category == "compliance":
        return ":orange[compliance]"
    return category

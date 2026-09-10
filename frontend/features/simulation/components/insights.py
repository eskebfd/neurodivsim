from html import escape
import re

import streamlit as st

from frontend.features.simulation.utils.helpers import profile_color


def clean_explanation_text(text: str) -> str:
    cleaned = " ".join(str(text).strip().split())
    replacements = {
        "Attention": "attention",
        "Fatigue": "fatigue",
        "Reading Speed": "reading speed",
        "Error Risk Score": "error risk",
        "Cognitive Load": "cognitive load",
        "Completion Time": "completion time",
        "Task Step": "interaction step",
        "Time Limit": "Zeitlimit",
        "Text Volume": "Textmenge",
        "Sentence Length": "Sentence length",
    }
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)
    cleaned = cleaned.replace(" .", ".").replace(" :", ":")
    cleaned = cleaned.replace(".,", ",").replace(".:", ":")
    while ".." in cleaned:
        cleaned = cleaned.replace("..", ".")
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def build_profile_recommendation_cards(profile: dict) -> list[dict]:
    return list(profile.get("recommendation_cards") or [])


def build_profile_positive_finding_cards(profile: dict) -> list[dict]:
    return list(profile.get("positive_findings") or [])


def _render_list(items: list[str]) -> str:
    cleaned_items = [clean_explanation_text(item) for item in items if item]
    if not cleaned_items:
        return ""
    return (
        '<ul class="cogsim-explain-card__list">'
        + "".join(f"<li>{escape(item)}</li>" for item in cleaned_items)
        + "</ul>"
    )


def _limit_sentences(text: str, max_sentences: int = 2) -> str:
    cleaned = clean_explanation_text(text)
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", cleaned)
        if sentence.strip()
    ]
    return " ".join(sentences[:max_sentences]) if sentences else cleaned


def _compact_effects(effects: list[str]) -> str:
    cleaned = [clean_explanation_text(effect).rstrip(".") for effect in effects if effect]
    return " · ".join(cleaned[:3])


def _step_box_markup(affected_step: str | None) -> str:
    if not affected_step:
        return ""
    text = clean_explanation_text(affected_step)
    match = re.match(r"^(Step\s+\d+)\s*[–-]\s*(.+)$", text)
    if match:
        step_number = match.group(1)
        step_description = match.group(2)
    else:
        step_number = "Step"
        step_description = text
    return (
        '<div class="cogsim-explain-card__step-box">'
        f'<span>{escape(step_number)}</span>'
        f'<p>{escape(step_description)}</p>'
        "</div>"
    )


def _recommendation_markup(card: dict, *, title: str, tone: str) -> str:
    actions = card.get("suggested_actions") or []
    expected_effects = card.get("expected_effects") or []
    priority = card.get("priority")
    affected_step = card.get("affected_step")
    badges = (
        f'<span class="cogsim-explain-card__badge">Priority: {escape(priority)}</span>'
        if priority
        else ""
    )

    return (
        f'<article class="cogsim-explain-card cogsim-explain-card--{escape(tone)}">'
        '<div class="cogsim-explain-card__topline">'
        f'<div class="cogsim-explain-card__eyebrow">{escape(title)}</div>'
        f'<div class="cogsim-explain-card__badges">{badges}</div>'
        "</div>"
        f'<h5>{escape(card.get("title", "Recommendation"))}</h5>'
        + _step_box_markup(affected_step)
        + '<div class="cogsim-explain-card__analysis">'
        '<div class="cogsim-explain-card__section">'
        "<span>Observation</span>"
        f'<p>{escape(_limit_sentences(card.get("finding", "")))}</p>'
        "</div>"
        '<div class="cogsim-explain-card__section">'
        "<span>Rationale</span>"
        f'<p>{escape(_limit_sentences(card.get("reasoning", "")))}</p>'
        "</div>"
        "</div>"
        + (
            '<div class="cogsim-explain-card__example">'
            "<span>Concrete changes</span>"
            + _render_list(actions)
            + "</div>"
            if actions
            else ""
        )
        + (
            '<div class="cogsim-explain-card__effect-row">'
            "<span>Expected Effect</span>"
            f'<p>{escape(_compact_effects(expected_effects))}</p>'
            + "</div>"
            if expected_effects
            else ""
        )
        + "</article>"
    )


def _positive_finding_markup(card: dict) -> str:
    evidence = card.get("evidence") or []
    return (
        '<article class="cogsim-explain-card cogsim-explain-card--positive">'
        '<div class="cogsim-explain-card__eyebrow">Positive observation</div>'
        f'<h5>{escape(card.get("title", "No urgent adjustment required"))}</h5>'
        '<div class="cogsim-explain-card__section">'
        "<span>What does the simulation show?</span>"
        f'<p>{escape(clean_explanation_text(card.get("finding", "")))}</p>'
        "</div>"
        + (
            '<div class="cogsim-explain-card__section">'
            "<span>Simulation insights</span>"
            + _render_list(evidence)
            + "</div>"
            if evidence
            else ""
        )
        + "</article>"
    )


def render_profile_explainable_cards(
    title: str,
    cards: list[dict],
    *,
    tone: str,
) -> None:
    if not cards:
        return

    card_markup = [
        _recommendation_markup(card, title=title, tone=tone) for card in cards
    ]
    st.markdown(
        '<div class="cogsim-explain-grid">'
        + "".join(card_markup)
        + "</div>",
        unsafe_allow_html=True,
    )


def render_profile_positive_findings(cards: list[dict]) -> None:
    if not cards:
        return
    st.markdown(
        '<div class="cogsim-explain-grid">'
        + "".join(_positive_finding_markup(card) for card in cards)
        + "</div>",
        unsafe_allow_html=True,
    )


def render_profile_recommendation_collection(
    profiles: list[dict],
    *,
    compact: bool = False,
) -> None:
    st.markdown("### What should be adjusted?")
    if not compact:
        st.caption(
            "The recommendations are grouped by reference configuration. They show "
            "which step was notable, why this may occur and which concrete "
            "adaptation may be useful."
        )
    first_open_profile = next(
        (
            profile["profile_id"]
            for profile in profiles
            if build_profile_recommendation_cards(profile)
        ),
        None,
    )
    for profile in profiles:
        cards = build_profile_recommendation_cards(profile)
        findings = build_profile_positive_finding_cards(profile)
        if not cards and not findings:
            continue
        with st.expander(
            profile["profile_label"],
            expanded=profile["profile_id"] == first_open_profile,
        ):
            if cards:
                render_profile_explainable_cards(
                    "Recommendation",
                    cards,
                    tone="recommendation",
                )
            else:
                render_profile_positive_findings(findings)


def _action_items_from_profile(profile: dict) -> list[str]:
    actions = []
    for card in build_profile_recommendation_cards(profile):
        for action in card.get("suggested_actions") or []:
            cleaned_action = clean_explanation_text(action)
            if cleaned_action and cleaned_action not in actions:
                actions.append(cleaned_action)
    return actions


def render_overview_design_recommendations(profiles: list[dict]) -> None:
    cards = []
    for index, profile in enumerate(profiles):
        actions = _action_items_from_profile(profile)
        profile_label = str(profile.get("profile_label") or "reference configuration")
        color = profile_color(profile, index)
        if actions:
            body = _render_list(actions)
        else:
            body = (
                '<p class="cogsim-overview-action-card__empty">'
                "For this configuration, the simulation does not indicate urgent "
                "adaptation needs. The design should nevertheless be checked for clear "
                "and easy-to-understand structure."
                "</p>"
            )
        cards.append(
            (
                '<article class="cogsim-overview-action-card">'
                '<div class="cogsim-overview-action-card__top">'
                f'<span style="background:{escape(color)}"></span>'
                f"<strong>{escape(profile_label)}</strong>"
                "</div>"
                "<small>Design recommendation</small>"
                f"{body}"
                "</article>"
            )
        )

    if not cards:
        return

    st.markdown(
        (
            '<section class="cogsim-overview-action-panel">'
            '<div class="cogsim-overview-action-panel__header">'
            "<span>What should be adjusted?</span>"
            "<p>The cards summarize only the concrete changes for designers. "
            "The profile tabs explain in more detail why a configuration is notable.</p>"
            "</div>"
            '<div class="cogsim-overview-action-grid">'
            + "".join(cards)
            + "</div>"
            "</section>"
        ),
        unsafe_allow_html=True,
    )

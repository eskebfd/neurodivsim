import streamlit as st

from frontend.shared.ui.icons import render_icon

PROFILE_OPTIONS = [
    "Generic",
    "ADHD",
    "Dyslexia",
]

PROFILE_SELECTION_CHANGED_FLAG = "_user_profiles_changed"

PROFILE_CARD_CONTENT = {
    "Generic": {
        "title": "Generic comparison",
        "description": (
            "A baseline configuration without a specific cognitive emphasis. "
            "It provides the comparison point for the simulated patterns."
        ),
        "footer_label": "Baseline",
        "icon": "user",
    },
    "ADHD": {
        "title": "ADHD-informed",
        "description": (
            "A reference configuration with increased sensitivity to "
            "distraction and reduced stability of sustained attention."
        ),
        "footer_label": "Select ADHD-informed",
        "icon": "user",
    },
    "Dyslexia": {
        "title": "Dyslexia-informed",
        "description": (
            "A reference configuration with increased effort for reading "
            "and processing text-based interface information."
        ),
        "footer_label": "Select dyslexia-informed",
        "icon": "user",
    },
}


def normalize_user_profiles(
    selected_profiles: list[str],
) -> list[str]:
    selected = list(dict.fromkeys(selected_profiles or ["Generic"]))

    if "Generic" not in selected:
        selected.insert(0, "Generic")

    return [profile for profile in PROFILE_OPTIONS if profile in selected]


def toggle_user_profile(
    current_profiles: list[str],
    profile: str,
) -> list[str]:
    profiles = normalize_user_profiles(current_profiles)

    if profile == "Generic":
        return profiles

    if profile in profiles:
        profiles = [item for item in profiles if item != profile]
    else:
        profiles = [*profiles, profile]

    return normalize_user_profiles(profiles)


def update_user_profile_selection(profile: str) -> None:
    current_profiles = st.session_state.get(
        "user_profiles",
        ["Generic"],
    )

    next_profiles = toggle_user_profile(
        current_profiles,
        profile,
    )

    if next_profiles != normalize_user_profiles(current_profiles):
        st.session_state.user_profiles = next_profiles
        st.session_state[PROFILE_SELECTION_CHANGED_FLAG] = True


def _profile_slug(profile: str) -> str:
    return (
        profile.lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def _build_profile_content_html(
    profile: str,
    selected: bool,
) -> str:
    content = PROFILE_CARD_CONTENT[profile]

    state_classes = [
        "cogsim-profile-card__content",
    ]

    if selected:
        state_classes.append("is-selected")

    if profile == "Generic":
        state_classes.append("is-baseline")

    class_names = " ".join(state_classes)

    icon_html = render_icon(
        content["icon"],
        size=34,
        stroke_width=1.7,
        label=f'{content["title"]} configuration',
    )

    check_html = ""

    if selected:
        check_html = (
            '<div class="cogsim-profile-card__check">'
            f'{render_icon("check", size=13, stroke_width=2.5)}'
            "</div>"
        )

    return (
        f'<div class="{class_names}">'
        f"{check_html}"
        '<div class="cogsim-profile-card__icon">'
        f"{icon_html}"
        "</div>"
        '<div class="cogsim-profile-card__title">'
        f'{content["title"]}'
        "</div>"
        '<div class="cogsim-profile-card__description">'
        f'{content["description"]}'
        "</div>"
        "</div>"
    )


def _render_profile_card(
    profile: str,
    selected: bool,
) -> None:
    content = PROFILE_CARD_CONTENT[profile]
    slug = _profile_slug(profile)
    state = "selected" if selected else "idle"

    with st.container(key=f"profile_option_{slug}_{state}"):
        card_html = _build_profile_content_html(
            profile=profile,
            selected=selected,
        )

        st.markdown(
            card_html,
            unsafe_allow_html=True,
        )

        if profile == "Generic":
            st.markdown(
                (
                    '<div class="cogsim-profile-card__footer '
                    'is-static">'
                    f'{content["footer_label"]}'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            return

        button_label = (
            f"Deselect {content['title']}" if selected else content["footer_label"]
        )

        st.button(
            button_label,
            key=f"profile_card_button_{slug}",
            use_container_width=True,
            on_click=update_user_profile_selection,
            args=(profile,),
        )


def render_user_profiles_section() -> list[str]:
    profiles = normalize_user_profiles(
        st.session_state.get(
            "user_profiles",
            ["Generic"],
        )
    )

    st.markdown(
        (
            '<div class="cogsim-user-profiles-intro">'
            '<div class="cogsim-user-profiles-intro__title">'
            "Which cognitive reference configurations should be compared?"
            "</div>"
            '<div class="cogsim-user-profiles-intro__text">'
            "Select the configurations for which NeuroDivSim should run the "
            "scenario. The generic comparison configuration remains active "
            "as the baseline."
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    columns = st.columns(
        len(PROFILE_OPTIONS),
        gap="medium",
    )

    for column, profile in zip(
        columns,
        PROFILE_OPTIONS,
    ):
        with column:
            _render_profile_card(
                profile=profile,
                selected=profile in profiles,
            )

    return profiles

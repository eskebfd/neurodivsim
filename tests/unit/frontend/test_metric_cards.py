from frontend.shared.styles.components.cards import CARDS_CSS
from frontend.shared.ui import metric_cards


def test_metric_card_uses_numeric_value_style_for_numbers(monkeypatch):
    rendered = []
    monkeypatch.setattr(
        metric_cards.st,
        "markdown",
        lambda body, **kwargs: rendered.append(body),
    )

    metric_cards.render_metric_card("Completion Time", "168 s")

    assert "cogsim-kpi-value--numeric" in rendered[0]


def test_metric_card_uses_text_value_style_for_step_names(monkeypatch):
    rendered = []
    monkeypatch.setattr(
        metric_cards.st,
        "markdown",
        lambda body, **kwargs: rendered.append(body),
    )

    metric_cards.render_metric_card(
        "Longest task step",
        "Step 2 – Detailinformationen und Bedingungen review",
    )

    assert "cogsim-kpi-value--text" in rendered[0]
    assert "Detailinformationen und Bedingungen review" in rendered[0]


def test_kpi_text_values_wrap_without_ellipsis():
    assert ".cogsim-kpi-value--text" in CARDS_CSS
    assert "white-space: normal" in CARDS_CSS
    assert "overflow-wrap: anywhere" in CARDS_CSS
    assert "text-overflow: ellipsis" not in CARDS_CSS

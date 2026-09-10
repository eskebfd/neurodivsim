from collections.abc import Sequence
import math
from typing import Any


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """
    Constrains a numeric value to a defined value range.
    By default, values are constrained to the 0 to 100 scale.
    """
    return max(minimum, min(maximum, float(value)))


def attribute_value(model: dict, attribute: str, default: float = 0.0) -> float:
    """
    Reads the numeric value of a model attribute.

    Supports attributes as plain numbers as well as attributes in the
    schema format {"value": ...}. Invalid values are replaced by the
    default value.
    """
    raw_value: Any = model.get(attribute, default)

    if isinstance(raw_value, dict):
        raw_value = raw_value.get("value", default)

    try:
        return clamp(float(raw_value))
    except (TypeError, ValueError):
        return clamp(default)


def parameter_value(model: dict, parameter: str, default: float = 0.0) -> float:
    """
    Reads a computed parameter from a parameter dictionary.
    The same logic as attribute_value() is used.
    """
    return attribute_value(model, parameter, default)


def rounded(value: float) -> float:
    """
    Clamps a value to the valid range and rounds
    it to two decimal places.
    """
    return round(clamp(value), 2)


def equal_weights(factor_count: int) -> tuple[float, ...]:
    """
    Creates equally distributed weights for any
    number of influencing factors.
    """
    if factor_count <= 0:
        raise ValueError("factor_count must be greater than zero")

    weight = 1 / factor_count
    return tuple(weight for _ in range(factor_count))


def validated_weights(
    weights: Sequence[float] | None,
    factor_count: int,
) -> tuple[float, ...]:
    """
    Validates weights for linear models.

    If no weights are provided, uniformly distributed weights
    are used automatically.
    """
    resolved = tuple(weights) if weights is not None else equal_weights(factor_count)


    if len(resolved) != factor_count:
        raise ValueError(f"Expected {factor_count} weights, received {len(resolved)}")


    if any(weight < 0 for weight in resolved):
        raise ValueError("Model weights must not be negative")


    if not math.isclose(sum(resolved), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("Model weights must sum to 1")

    return resolved


def weighted_sum(
    factors: Sequence[float],
    weights: Sequence[float] | None = None,
) -> float:
    """
    Berechnet die gewichtete Summe mehrerer Einflussfaktoren.

    Diese Funktion bildet die Grundlage aller linearen Modelle
    innerhalb der Simulation.
    """
    resolved_weights = validated_weights(weights, len(factors))

    return rounded(
        sum(weight * factor for weight, factor in zip(resolved_weights, factors))
    )

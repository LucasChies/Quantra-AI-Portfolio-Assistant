from datetime import date

from app.integrations.schemas import FreshnessMetadata, MacroObservation

_SUPPORTED_FREQUENCIES = frozenset(
    {"daily", "business_daily", "monthly", "quarterly"}
)


def assess_freshness(
    observations: list[MacroObservation],
    frequency: str,
    max_age_days: int,
    evaluated_on: date,
) -> FreshnessMetadata:
    """Assess the latest economic observation using its catalogue freshness policy.

    The age is measured from observation_date, not retrieved_at. Publication
    delays for lower-frequency series are represented by their catalogue
    max_age_days policy; no 24-hour rule is applied to monthly or quarterly data.
    """
    latest = max(observations, key=lambda item: item.observation_date, default=None)

    if frequency not in _SUPPORTED_FREQUENCIES:
        return FreshnessMetadata(
            status="unknown",
            frequency=frequency,
            observation_date=latest.observation_date if latest else None,
            age_days=None,
            max_age_days=max_age_days,
            evaluated_on=evaluated_on,
            reason=f"Unsupported observation frequency: {frequency}",
        )

    if latest is None:
        return FreshnessMetadata(
            status="unknown",
            frequency=frequency,
            observation_date=None,
            age_days=None,
            max_age_days=max_age_days,
            evaluated_on=evaluated_on,
            reason="The provider returned no observations.",
        )

    age_days = (evaluated_on - latest.observation_date).days

    if age_days < 0:
        return FreshnessMetadata(
            status="unknown",
            frequency=frequency,
            observation_date=latest.observation_date,
            age_days=age_days,
            max_age_days=max_age_days,
            evaluated_on=evaluated_on,
            reason="The latest observation date is in the future.",
        )

    if latest.value is None:
        return FreshnessMetadata(
            status="unknown",
            frequency=frequency,
            observation_date=latest.observation_date,
            age_days=age_days,
            max_age_days=max_age_days,
            evaluated_on=evaluated_on,
            reason="The latest observation has no usable numeric value.",
        )

    if age_days > max_age_days:
        return FreshnessMetadata(
            status="stale",
            frequency=frequency,
            observation_date=latest.observation_date,
            age_days=age_days,
            max_age_days=max_age_days,
            evaluated_on=evaluated_on,
            reason=(
                f"The latest observation is {age_days} days old; "
                f"the configured maximum is {max_age_days} days."
            ),
        )

    return FreshnessMetadata(
        status="fresh",
        frequency=frequency,
        observation_date=latest.observation_date,
        age_days=age_days,
        max_age_days=max_age_days,
        evaluated_on=evaluated_on,
        reason=(
            f"The latest observation is within the configured "
            f"{max_age_days}-day freshness window."
        ),
    )

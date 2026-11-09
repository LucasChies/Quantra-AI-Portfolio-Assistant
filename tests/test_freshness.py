from datetime import UTC, date, datetime
from decimal import Decimal

from app.integrations.freshness import assess_freshness
from app.integrations.schemas import MacroObservation

EVALUATED_ON = date(2026, 11, 9)


def make_observation(
    observation_date: date,
    value: Decimal | None = Decimal("1.25"),
) -> MacroObservation:
    return MacroObservation(
        observation_date=observation_date,
        value=value,
        provider="test",
        series_id="TEST",
        retrieved_at=datetime(2026, 11, 9, 12, 0, tzinfo=UTC),
        source_url="https://example.test/series",
    )


def test_daily_observation_is_fresh_at_maximum_allowed_age() -> None:
    result = assess_freshness(
        [make_observation(date(2026, 11, 4))],
        frequency="daily",
        max_age_days=5,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "fresh"
    assert result.age_days == 5
    assert result.observation_date == date(2026, 11, 4)


def test_daily_observation_is_stale_after_maximum_allowed_age() -> None:
    result = assess_freshness(
        [make_observation(date(2026, 11, 3))],
        frequency="daily",
        max_age_days=5,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "stale"
    assert result.age_days == 6


def test_monthly_observation_can_be_fresh_beyond_24_hours() -> None:
    result = assess_freshness(
        [make_observation(date(2026, 9, 30))],
        frequency="monthly",
        max_age_days=50,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "fresh"
    assert result.age_days == 40


def test_quarterly_observation_uses_its_longer_freshness_window() -> None:
    result = assess_freshness(
        [make_observation(date(2026, 7, 22))],
        frequency="quarterly",
        max_age_days=120,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "fresh"
    assert result.age_days == 110


def test_business_daily_observation_allows_non_trading_days() -> None:
    result = assess_freshness(
        [make_observation(date(2026, 11, 5))],
        frequency="business_daily",
        max_age_days=5,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "fresh"
    assert result.age_days == 4


def test_empty_series_has_unknown_freshness() -> None:
    result = assess_freshness(
        [],
        frequency="daily",
        max_age_days=5,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "unknown"
    assert result.observation_date is None
    assert result.age_days is None


def test_latest_observation_without_numeric_value_is_unknown() -> None:
    result = assess_freshness(
        [make_observation(date(2026, 11, 8), value=None)],
        frequency="daily",
        max_age_days=5,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "unknown"
    assert result.age_days == 1


def test_future_observation_date_is_unknown() -> None:
    result = assess_freshness(
        [make_observation(date(2026, 11, 10))],
        frequency="daily",
        max_age_days=5,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "unknown"
    assert result.age_days == -1


def test_unsupported_frequency_is_unknown() -> None:
    result = assess_freshness(
        [make_observation(date(2026, 11, 8))],
        frequency="hourly",
        max_age_days=1,
        evaluated_on=EVALUATED_ON,
    )

    assert result.status == "unknown"
    assert "Unsupported" in result.reason

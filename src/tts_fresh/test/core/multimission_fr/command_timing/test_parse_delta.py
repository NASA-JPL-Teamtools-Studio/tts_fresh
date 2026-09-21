from datetime import timedelta

import pytest

from tts_fresh.flightrules.core.command_timing import FR_Command_Timing_Checker

_parse_delta = FR_Command_Timing_Checker._parse_delta


def test_HH_MM_SS_f():
    assert _parse_delta("03:30:17.521") == timedelta(seconds=12_617.521)
    assert _parse_delta("+03:30:17.521") == timedelta(seconds=12_617.521)
    assert _parse_delta("-03:30:17.521") == timedelta(seconds=-12_617.521)

    assert _parse_delta("27:30:17.521") == timedelta(days=1, seconds=12_617.521)
    assert _parse_delta("+27:30:17.521") == timedelta(days=1, seconds=12_617.521)
    assert _parse_delta("-27:30:17.521") == -timedelta(days=1, seconds=12_617.521)


def test_j_HH_MM_SS():
    assert _parse_delta("000T03:30:17.512") == timedelta(seconds=12_617.512)
    assert _parse_delta("+000T03:30:17.512") == timedelta(seconds=12_617.512)
    assert _parse_delta("-000T03:30:17.512") == -timedelta(seconds=12_617.512)

    assert _parse_delta("001T03:30:17.512") == timedelta(days=1, seconds=12_617.512)
    assert _parse_delta("+001T03:30:17.512") == timedelta(days=1, seconds=12_617.512)
    assert _parse_delta("-001T03:30:17.512") == -timedelta(days=1, seconds=12_617.512)


def test_integer_seconds():
    assert _parse_delta("00:00:00") == timedelta()
    assert _parse_delta("01:02:03") == timedelta(hours=1, minutes=2, seconds=3)


def test_invalid_tag_raises():
    for bad in ("", "not-a-time", "1:2", "00:00:00T"):
        with pytest.raises(ValueError):
            _parse_delta(bad)

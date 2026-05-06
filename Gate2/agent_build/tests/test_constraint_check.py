from agent_build.src.constraint_check import aurum_realtime_correction_possible


def test_realtime_correction_always_false():
    """Aurum has no real-time API — this must always be False, unconditionally."""
    assert aurum_realtime_correction_possible() is False


def test_called_multiple_times_always_false():
    """Must be deterministic regardless of call frequency."""
    for _ in range(5):
        assert aurum_realtime_correction_possible() is False

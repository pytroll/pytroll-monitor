"""Tests for custom logging handlers."""
import os
import logging


def test_checkmk_handler(tmp_path):
    """Test functionality for checkmk log handler."""
    from pytroll_monitor.checkmk_logger import CheckMKHandler
    f = tmp_path / "bla"
    ch = CheckMKHandler(os.fspath(f))
    logger = logging.getLogger("pytroll.test")
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
            "{asctime:s} - {name:s} - {levelname:s} - {message:s}",
            style="{", validate=True)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    try:
        # status is unknown, nothing logged yet
        status = ch.get_status_line()
        assert status == '3 "Pytroll status report" - Pytroll lives!'
        with f.open(mode="rt", encoding="ascii") as fp:
            contents = fp.read()
            assert contents == status

        # log something uninformative
        logger.debug("No sono spaghetto")
        assert ch.get_status_line() == ('3 "Pytroll status report" - '
                                        "Pytroll lives!")

        # log something problematic
        logger.warning("You stepped on my toe!")
        assert ch.get_status_line().startswith("1 ")  # 1 for warning

        # log something critical
        logger.critical("We're out of chocolate, coffee, and beer.")
        assert ch.get_status_line().startswith("2 ")  # 2 for critical
    finally:
        logger.removeHandler(ch)

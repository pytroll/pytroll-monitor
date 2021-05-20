"""Tests for custom logging handlers."""
import os
import logging


def test_checkmk_handler(tmp_path):
    """Test functionality for checkmk log handler."""
    from pytroll_monitor.checkmk_logger import CheckMKHandler
    f = tmp_path / "bla"
    ch = CheckMKHandler(os.fspath(f))
    logger = logging.getLogger("pytroll.test")
    logger.setLevel(logging.DEBUG)
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
        assert ch.get_status_line().startswith("3 ")  # 3 for unknown
        assert ch.get_status_line() == ('3 "Pytroll status report" - '
                                        "Pytroll lives!")

        # log something problematic
        logger.warning("You stepped on my toe!")
        assert ch.get_status_line().startswith("1 ")  # 1 for warning

        # log something bad
        logger.error("Lunch will be late")
        assert ch.get_status_line().startswith("2 ")  # 2 for critical

        # log something critical
        logger.critical("We're out of chocolate, coffee, and beer.")
        assert ch.get_status_line().startswith("2 ")  # 2 for critical

        # log something not so good
        logger.info("All 0 files produced nominally in 00:00:00")
        assert ch.get_status_line().startswith("1 ")  # 1 for warning

        # log something good
        logger.info("All 100 files produced nominally in 00:00:00")
        assert ch.get_status_line().startswith("0 ")  # 0 for OK, resets warnings

        # check that this is in the file, too
        with f.open(mode="rt", encoding="ascii") as fp:
            contents = fp.read(1)
            assert contents == "0"

    finally:
        logger.removeHandler(ch)

import os
def test_checkmk_handler(tmp_path):
    from pytroll_monitor.checkmk_logger import CheckMKHandler
    f = tmp_path / "bla"
    handler = CheckMKHandler(os.fspath(f))
    status = handler.get_status_line()
    assert status == '3 "Pytroll status report" - Pytroll lives!'
    with f.open(mode="rt", encoding="ascii") as fp:
        contents = fp.read()
        assert contents == status
    handler.emit(None)

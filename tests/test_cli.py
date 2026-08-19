from ..cli import parse_args


def test_debug_flag_selects_debug_mode():
    args = parse_args(["--debug", "find", "the", "problem"])

    assert args.mode == "debug"
    assert args.question == ["find", "the", "problem"]


def test_custom_mode_is_accepted():
    args = parse_args(["--mode", "via_negativa", "simplify", "this"])

    assert args.mode == "via_negativa"
    assert args.question == ["simplify", "this"]

def test_no_save_flag_is_enabled():
    args = parse_args(["--debug", "--no-save", "inspect this"])

    assert args.mode == "debug"
    assert args.no_save is True
    assert args.question == ["inspect this"]
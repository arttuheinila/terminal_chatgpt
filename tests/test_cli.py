from ..cli import parse_args


def test_debug_flag_selects_debug_mode():
    args = parse_args(["--debug", "find", "the", "problem"])

    assert args.mode == "debug"
    assert args.question == ["find", "the", "problem"]


def test_custom_mode_is_accepted():
    args = parse_args(["--mode", "via_negativa", "simplify", "this"])

    assert args.mode == "via_negativa"
    assert args.question == ["simplify", "this"]
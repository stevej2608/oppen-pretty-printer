from oppen_pretty_printer import Tokens as T, BreakType



def test_tokens(pprint):
    tokens = [T.BEGIN(), T.STRING("XXXXXXX"), T.BREAK(), T.STRING("YYYYYYY"), T.END(), T.EOF()]
    result = pprint(tokens)
    assert result == "XXXXXXX YYYYYYY"


def test_break_and_offset(pprint):
    """Test long lines are folded as we reduce the print width

    Test string:
        XXXXXXXXXX + YYYYYYYYYY + ZZZZZZZZZZ

    Result width=75

        XXXXXXXXXX + YYYYYYYYYY + ZZZZZZZZZZ

    Result width=25

        XXXXXXXXXX + YYYYYYYYYY +
          ZZZZZZZZZZ

    Result width=20

        XXXXXXXXXX +
          YYYYYYYYYY +
          ZZZZZZZZZZ

    Result width=20, T.BEGIN(offset=4)

        XXXXXXXXXX +
            YYYYYYYYYY +
            ZZZZZZZZZZ

    """

    def get_sample(offset: int = None):
        _Begin = T.BEGIN(offset=offset) if offset else T.BEGIN()
        return [
            _Begin,
            T.STRING("XXXXXXXXXX"),
            T.BREAK(), T.STRING("+"), T.BREAK(),
            T.STRING("YYYYYYYYYY"),
            T.BREAK(), T.STRING("+"), T.BREAK(),
            T.STRING("ZZZZZZZZZZ"),
            T.END(),
            T.EOF()]

    text = get_sample()

    result = pprint(text)
    assert result == 'XXXXXXXXXX + YYYYYYYYYY + ZZZZZZZZZZ'

    result = pprint(text, lineWidth=25)
    assert result == 'XXXXXXXXXX + YYYYYYYYYY +\n  ZZZZZZZZZZ'

    result = pprint(text, lineWidth=20)
    assert result == 'XXXXXXXXXX +\n  YYYYYYYYYY +\n  ZZZZZZZZZZ'

    # Change offset

    text = get_sample(offset=4)
    result = pprint(text, lineWidth=20)
    assert result == 'XXXXXXXXXX +\n    YYYYYYYYYY +\n    ZZZZZZZZZZ'

    text = get_sample(offset=4)
    result = pprint(text, lineWidth=20)
    assert result == 'XXXXXXXXXX +\n    YYYYYYYYYY +\n    ZZZZZZZZZZ'



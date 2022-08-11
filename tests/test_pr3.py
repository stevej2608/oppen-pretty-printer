
from oppen_pretty_printer import pprint, Tokens as T

def test_pr3(pprint):
    tokens = [
        T.BEGIN(),
        T.STRING("begin"),T.BREAK(),
        T.STRING("x"),
        T.BREAK(), T.STRING(":="), T.BREAK(),
        T.STRING("40"),
        T.BREAK(), T.STRING("+"), T.BREAK(),
        T.STRING("2"),T.BREAK(),
        T.STRING("end"),
        T.END(),
        T.EOF()]

    result = pprint(tokens)
    assert result == "begin x := 40 + 2 end"
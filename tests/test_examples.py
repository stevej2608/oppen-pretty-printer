from oppen_pretty_printer import Tokens as T, BreakType

def block_weave(text):
    """Convert words in text into String tokens and spaces into T.BREAK tokens

    Arguments:
        text {str} -- Test to be woven

    Returns:
        [list] -- List of tokens

    Example:

        weave('Hello World !')

    Returns:

        [T.BEGIN(), String('Hello'), T.BREAK(), String('World'), T.BREAK(), String('!'), T.END()]

    """
    words = [T.STRING(word) for word in text.split(' ')]

    result = [T.BREAK()] * (len(words) * 2 - 1)
    result[0::2] = words
    return [T.BEGIN()] + result + [T.END()]


def test_case_example(pprint):
    """Test offset

    Expected result:

        cases 1 : XXXXX
              2 : YYYYY
              3 : ZZZZZ

    See Oppen doc, section 5
    """

    text = [
        T.BEGIN(offset=6),
        *block_weave('cases 1 : XXXXX'), T.LINEBREAK,
        *block_weave('2 : YYYYY'), T.LINEBREAK,
        *block_weave('3 : ZZZZZ'),
        T.END(),
        T.EOF()]

    result = pprint(text)
    assert result == 'cases 1 : XXXXX\n      2 : YYYYY\n      3 : ZZZZZ'


def test_breakType_example(pprint):
    """Test offset (example taken from Oppen paper)

    Result width=75

        begin
          x := f(x); y := f(y); z := f(z); w := f(w);
          end;

    Result width=24

        begin
          x := f(x); y := f(y);
          z := f(z); w := f(w);
          end;

    Result width=75, T.BEGIN(breakType=BreakType.consistent)

        begin
          x := f(x);
          y := f(y);
          z := f(z);
          w := f(w);
          end;

    See Oppen, section 5: Modifications of the basic algorithm
    """

    def get_sample(breakType: BreakType = None):
        _Begin = T.BEGIN(breakType=breakType) if breakType else T.BEGIN()
        return [
            _Begin,
            *block_weave('begin'), T.LINEBREAK,
            *block_weave('x := f(x);'), T.BREAK(),
            *block_weave('y := f(y);'), T.BREAK(),
            *block_weave('z := f(z);'), T.BREAK(),
            *block_weave('w := f(w);'), T.LINEBREAK,
            *block_weave('end;'),
            T.END(),
            T.EOF()]

    text = get_sample()
    result = pprint(text)
    assert result == 'begin\n  x := f(x); y := f(y); z := f(z); w := f(w);\n  end;'

    result = pprint(text, lineWidth=24)
    assert result == 'begin\n  x := f(x); y := f(y);\n  z := f(z); w := f(w);\n  end;'

    text = get_sample(breakType=BreakType.consistent)
    result = pprint(text)
    assert result == 'begin\n  x := f(x);\n  y := f(y);\n  z := f(z);\n  w := f(w);\n  end;'

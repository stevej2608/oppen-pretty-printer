from oppen_pretty_printer import Tokens as T, BreakType


def test_nested_blocks(pprint):
    """
    Expected result:

		procedure test(x, y: Integer);
		begin
		  x:=1;
		  y:=200;
		  for z:= 1 to 100 do
		  begin
			x := x + z;
		  end;
		  y:=x;
		end;

    """

    def brk(offset=0):
        "force a new line and indent by given offset"
        return T.BREAK(blankSpace=9999, offset=offset)

    text = [
        T.BEGIN(breakType=BreakType.consistent, offset=0),

        T.STRING('procedure test(x, y: Integer);'), brk(),
        T.STRING("begin"),

        brk(2), T.STRING("x:=1;"),
        brk(2), T.STRING("y:=200;"),

        # indented for loop

        brk(2), T.BEGIN(breakType=BreakType.consistent, offset=0),
        T.STRING("for z:= 1 to 100 do"), brk(),
        T.STRING("begin"),
        brk(2), T.STRING("x := x + z;"), brk(),
        T.STRING("end;"),
        T.END(),

        brk(2), T.STRING("y:=x;"), brk(),
        T.STRING("end;"),

        T.END(),
        T.EOF()]


    result = pprint(text)

    assert result == (
        'procedure test(x, y: Integer);\n'
        'begin\n'
        '  x:=1;\n'
        '  y:=200;\n'
        '  for z:= 1 to 100 do\n'
        '  begin\n'
        '    x := x + z;\n'
        '  end;\n'
        '  y:=x;\n'
        'end;'
        )

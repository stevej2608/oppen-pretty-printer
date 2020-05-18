from enum import Enum

# Pretty printer Token definition

class BreakType(Enum):
    """Modifies the Break token behaviour in a Begin...End block:

    consistent: if a block cannot fit on a line, and the blanks in the block are
    consistent blanks, then each subblock of the block will be placed
    on a new line.

    inconsistent: if the blanks in the block are inconsistent, then a new line will be
    forced only if necessary

    fits: no breaks are needed (the block fits on the line)
    """
    ﬁts = 1
    inconsistent = 2
    consistent = 3

class Token:
    """Token base class
    """

    def __eq__(self, other):
        return isinstance(self, other)

    def __repr__(self):
        return self.__str__()


class String(Token):

    def __init__(self, string):
        self.string = string

    @property
    def length(self):
        return len(self.string)

    def __str__(self):
        return f"String('{self.string}')"


class Break(Token):
    """
    A token of type Break denotes an optional line-break; if
    the prettyprinter outputs a line-break, it indents "offset"
    spaces relative to the indentation of the enclosing
    block; otherwise it outputs "blankSpace" blanks; these values
    are defaulted to 0 and 1, respectively.

    Keyword Arguments:
        blankSpace {int} -- [description] (default: {1})
        offset {int} -- number of indent spaces (default: {0})
    """
    def __init__(self, blankSpace: int = 1, offset: int = 0):
        self.blankSpace = blankSpace    # number of spaces per blank
        self.offset = offset            # indent for overﬂow lines

    def __str__(self):
        return f'Break(off={self.offset}, space={self.blankSpace})'


class Begin(Token):
    """Begin token

    Keyword Arguments:
        offset {int} -- indent for overﬂow lines (default: {2})
        breakType {BreakType} -- The break sub-type (default: {BreakType.inconsistent})
    """


    def __init__(self, offset: int = 2, breakType: BreakType = BreakType.inconsistent):
        self.offset = offset            # indent for overﬂow lines
        self.breakType = breakType      # default “inconsistent”

    def __str__(self):
        return f'Begin(off={self.offset}, {str(self.breakType.name)})'


class End(Token):

    def __str__(self):
        return f'End()'

class Eof(Token):

    def __str__(self):
        return f'Eof()'

LineBreak = Break(blankSpace=9999)

class Tokens:

    BEGIN = Begin
    END = End
    BREAK = Break
    EOF = Eof
    STRING = String

    LINEBREAK = LineBreak

import sys
from typing import List
import logging

from io import StringIO


from .tokens import BreakType, Token, Begin, End, Break, String, Eof

# This module is class based implementation of the pretty-printing algorithm developed
# by DEREK C. OPPEN at Stanford University in the late 1970s.

log = logging.getLogger()


class Error(Exception):
    pass


sizeInﬁnity: int = sys.maxsize
CR = "\n"


class PrettyPrint:
    """The prettyprinter receives tokens which are records of various types.

    A token of type STRING contains a string.

    A token of type BREAK denotes an optional line break; if the prettyprinter
    outputs a line break, it indents "offset" spaces relative to the indentation of the
    enclosing block; otherwise it outputs "blank_space" blanks; these values are
    defaulted to 0 and 1, respectively.

    Tokens of type BEGIN and END correspond to our {[ and ]}, except that the
    type of breaks is associated with the BEGIN rather than with the break
    itself (the type is defaulted to "inconsistent"), and an offset value may be
    associated with the BEGIN (the offset applies to the wholeblock and is defaulted to 2).

    A token of type EOF initiates cleanup.

    Finally, a "linebreak" is a distinguished instance of "break" which forces a line
    break (by setting "blankSpace" to be a very large integer).

    Arguments:
        tkn {Token} -- [description]
    """

    # Total number of spaces needed to print all elements of the token buffer
    # from token[1] through token[left]

    left_total: int

    # Total number of spaces needed to print all elements of the token buffer
    # from token[1] through token[right]

    right_total: int

    def __init__(self, lineWidth=75):

        n = 3 * lineWidth

        self.token = [None] * n
        self.size = [None] * n
        self.scan_stack = ScanStack(n)

        self.left_total = self.right_total = 1
        self.left = self.right = 0

        self.printer = TokenPrinter(lineWidth)

    def pprint(self, tkn: Token):
        t = tkn
        # log.info('PrettyPrint(%s)', t)
        if t == Eof:
            if not self.scan_stack.empty:
                self.check_stack(0)
                self.advance_left(self.token[self.left], self.size[self.left])
            self.printer.indent(0)
        elif t == Begin:
            if self.scan_stack.empty:
                self.left_total = self.right_total = 1
                self.left = self.right = 0
            else:
                self.advance_right()

            self.token[self.right] = t
            self.size[self.right] = -self.right_total
            self.scan_stack.push(self.right)

        elif t == End:
            if self.scan_stack.empty:
                self.printer.print(t, 0)
            else:
                self.advance_right()
                self.token[self.right] = t
                self.size[self.right] = -1                    # Different
                self.scan_stack.push(self.right)

        elif t == Break:
            if self.scan_stack.empty:
                self.left_total = self.right_total = 1
                self.left = self.right = 0

            else:
                self.advance_right()

            self.check_stack(0)
            self.scan_stack.push(self.right)
            self.token[self.right] = t
            self.size[self.right] = -self.right_total
            self.right_total += t.blankSpace

        elif t == String:
            if self.scan_stack.empty:
                self.printer.print(t, t.length)
            else:
                self.advance_right()
                self.token[self.right] = t
                self.size[self.right] = t.length
                self.right_total += t.length
                self.check_stream()

    def check_stream(self):

        if self.right_total - self.left_total > self.printer.space:

            if not self.scan_stack.empty:
                if self.left == self.scan_stack.bottom:
                    self.size[self.scan_stack.pop_bottom()] = sizeInﬁnity

            self.advance_left(self.token[self.left], self.size[self.left])

            if not self.left == self.right:
                self.check_stream()

    def advance_right(self):
        """Advance the token buffer input index raise ERROR on buffer overflow"""

        self.right = (self.right + 1) % self.scan_stack.len
        if self.right == self.left:
            raise Error("TokenQueueFull")

    def advance_left(self, x: Token, l: int):

        if l >= 0:
            self.printer.print(x, l)

            if x == Break:
                self.left_total += x.blankSpace

            if x == String:
                self.left_total += l

            if self.left != self.right:
                self.left = (self.left + 1) % self.scan_stack.len
                self.advance_left(self.token[self.left], self.size[self.left])

    def check_stack(self, k: int):
        x: int
        if not self.scan_stack.empty:
            x = self.scan_stack.top
            if self.token[x] == Begin:
                if k > 0:
                    self.size[self.scan_stack.pop()] = self.size[x] + self.right_total
                    self.check_stack(k - 1)
            elif self.token[x] == End:
                self.size[self.scan_stack.pop()] = 1
                self.check_stack(k + 1)
            else:
                self.size[self.scan_stack.pop()] = self.size[x] + self.right_total
                if k > 0:
                    self.check_stack(k)

    def getvalue(self):
        return self.printer.getvalue()


class ScanStack:
    def __init__(self, size):
        self._stack = [None] * size
        self._empty = True
        self._top = self._bottom = 0

    @property
    def empty(self):
        return self._empty

    @property
    def len(self):
        return len(self._stack)

    def _inc(self, index):
        return (index + 1) % len(self._stack)

    def _dec(self, index):
        return (index - 1) % len(self._stack)

    def push(self, x: int):
        """Push the index of a token in the token buffer"""

        if self.empty:
            self._empty = False
        else:
            self._top = self._inc(self._top)
            if self._top == self._bottom:
                raise Error("ScanStackFull")
        self._stack[self._top] = x

    def pop(self) -> int:
        """Pop the index of a token in the token buffer"""

        if self.empty:
            raise Error("ScanStackEmpty")
        x = self._stack[self._top]
        if self._top == self._bottom:
            self._empty = True
        else:
            self._top = self._dec(self._top)
        return x

    @property
    def top(self) -> int:
        """Return the token buffer index of the most recently added token"""

        if self.empty:
            raise Error("ScanStackEmpty")
        return self._stack[self._top]

    @property
    def bottom(self) -> int:
        """Return the token buffer index of the oldest token"""
        return self._stack[self._bottom]

    def pop_bottom(self) -> int:
        """Pop the token buffer index of the oldest token"""

        if self.empty:
            raise Error("ScanStackEmpty")
        x = self._stack[self._bottom]
        if self._top == self._bottom:
            self._empty = True
        else:
            self._bottom = self._inc(self._bottom)
        return x


# Print stack definition


class PrintStackEntry:
    """Holds details of Begin token
    """
    offset: int

    # The block brake type

    brk: BreakType

    def __init__(self, offset: int, brk: BreakType):
        self.brk = brk
        self.offset = offset

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'PrintStackEntry brk={self.brk.name}, offset={self.offset}'


class TokenPrinter:

    # 'space' is  the remaning space in the line

    space: int
    margin: int
    output: StringIO

    # Holds received BEGIN token parameters. The parameters
    # are pushed onto the stack when a BEGIN token is 
    # received. The stack top value is popped and discarded
    # when an END token is received.

    printStack: List[PrintStackEntry]

    def __init__(self, lineWidth):
        self.printStack = []
        self.space = self.margin = lineWidth
        self.output = StringIO()

    def print(self, x: Token, l: int):
        """
        Accept tokens from the pretty-print scanner and emit characters
        to the output stream

        Arguments:
            x {Token} -- token sent from the scanner
            l {int} -- the computed length for the token

        """
        if x == Begin:
            if l > self.space:
                self._push(
                    PrintStackEntry(
                        self.space - x.offset,
                        (BreakType.consistent if x.breakType == BreakType.consistent else BreakType.inconsistent),
                    )
                )
            else:
                entry = PrintStackEntry(0, BreakType.ﬁts)
                self._push(entry)

        elif x == End:

            # Printing of the current block is compleat, pop and discard the the Begin token
            # parameters associated with the block.

            self._pop()

        elif x == Break:
            block = self.top
            if block.brk == BreakType.fits:
                self.space -= x.blankSpace
                self.indent(x.blankSpace)
            elif block.brk == BreakType.consistent:
                self.space = block.offset - x.offset
                self.new_line(self.margin - self.space)
            elif block.brk == BreakType.inconsistent:
                if l > self.space:
                    self.space = block.offset - x.offset
                    self.new_line(self.margin - self.space)
                else:
                    self.space = self.space - x.blankSpace
                    self.indent(x.blankSpace)
        elif x == String:
            if l > self.space:
                raise Error("LineTooLong")
            self.space -= l
            self._puts(x.string)
        else:
            raise Error("Invalid switch")

    def _push(self, obj: PrintStackEntry):
        """Push Begin token parameters"""
        self.printStack.append(obj)

    def _pop(self) -> PrintStackEntry:
        """Pup the top value o the Begin token stack"""
        return self.printStack.pop()

    @property
    def top(self) -> PrintStackEntry:
        """Top value on the Begin token stack"""
        return self.printStack[-1]

    def new_line(self, amount: int):
        """Output CR and indent by given amount"""
        self._putc(CR)
        self.indent(amount)


    def _putc(self, c):
        """Print the given character"""
        # log.info('_putc("%s")', (c if c != "\n" else "\\n"))
        self.output.write(c)

    def _puts(self, s):
        """Print the given string"""
        # log.info('_puts("%s")', s)
        self.output.write(s)

    def indent(self, amount: int):
        """Indent by given amount"""
        if amount:
            self._puts(" " * amount)


    def getvalue(self):
        """Return pretty printed output"""
        return self.output.getvalue()


# Public interface


def pprint(tokens=[], lineWidth=75):
    pprint = PrettyPrint(lineWidth=lineWidth)
    for t in tokens:
        pprint.pprint(t)
    return pprint.getvalue()

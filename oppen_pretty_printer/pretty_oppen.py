import sys
import logging

from io import StringIO
from typing import List


from .tokens import BreakType, Token, Begin, End, Break, String, Eof

# This module is an attempt at a faithful recreation, in python, of the
# pretty-printing algorithm developed by DEREK C. OPPEN at Stanford  University
# in the late 1970s. The appendix of [PRETTY PRINTING, Derek C. Oppen, 1979] contains
# the original prettyprint program written in [MESA]
#
# Comments starting with APPX refere to the PRETTY PRINTING appendix
#
# [PRETTY PRINTING, Derek C. Oppen, 1979]: https://www.cs.tufts.edu/~nr/cs257/archive/derek-oppen/prettyprinting.pdf
# [MESA]: http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-79-3_Mesa_Language_Manual_Version_5.0.pdf


log = logging.getLogger()

output = StringIO()
CR = "\n"

class Error(Exception):
    pass

def PutChar(char):
    global output
    output.write(char)

def PutString(s):
    global output
    output.write(s)


#APPX PrettyPrinter: PROGRAM

margin: int
space: int

# Token buffer and associated size buffer. This is used exclusively by
# the token scanner: PrettyPrint()

left: int = 0               # token buffer output index
right: int = 0              # token input index

token: List[Token] = []     # token buffer
size: List[int] = []        # size of associated token in the token buffer

# Total number of spaces needed to print all elements of the token buffer
# from token[1] through token[left]

leftTotal: int

# Total number of spaces needed to print all elements of the token buffer
# from token[1] through token[right]

rightTotal: int

sizeInﬁnity: int = sys.maxsize

# ScanStack holds the indexes of Begin, End and Break tokens in the
# token[] buffer. ScanStack is really managed as a ring
# buffer. Bottom is the index of the oldest entry, top is
# the index of the most recent.

scanStack: List[int] = []
scanStackEmpty: bool
top: int = 0
bottom: int = 0

#APPX PrettyPrintInit: PROCEDURE[lineWidth: CARDINAL <— 75]

def PrettyPrintInit(lineWidth=75):
    global space, margin, top, bottom, scanStackEmpty, token, size, scanStack, output

    space = margin = lineWidth
    n = 3 * margin
    top = bottom = 0
    scanStackEmpty = True
    token = [None] * n
    size = [None] * n
    scanStack = [None] * n

    output.truncate(0)
    output.seek(0)

#APPX PrettyPrint: PROCEDURE[tkn: Token]

def PrettyPrint(tkn: Token):
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
    global left, leftTotal, right, rightTotal, scanStackEmpty, size, token, scanStackEmpty
    t = tkn
    # log.info('PrettyPrint(%s)', t)
    if t == Eof:
        if not scanStackEmpty:
            CheckStack(0)
            AdvanceLeft(token[left], size[left])
        Indent(0)
    elif t == Begin:
        if scanStackEmpty:
            leftTotal = rightTotal = 1
            left = right = 0
        else:
            AdvanceRight()

        token[right] = t
        size[right] = -rightTotal
        ScanPush(right)

    elif t == End:
        if scanStackEmpty:
            Print(t, 0)
        else:
            AdvanceRight()
            token[right] = t
            size[right] = -1
            ScanPush(right)

    elif t == Break:
        if scanStackEmpty:
            leftTotal = rightTotal = 1
            left = right = 0

        else:
            AdvanceRight()

        CheckStack(0)
        ScanPush(right)
        token[right] = t
        size[right] = -rightTotal
        rightTotal = rightTotal + t.blankSpace

    elif t == String:
        if scanStackEmpty:
            Print(t, t.length)
        else:
            AdvanceRight()
            token[right] = t
            size[right] = t.length
            rightTotal = rightTotal + t.length
            CheckStream()

#APPX CheckStream: PROCEDURE

def CheckStream():
    global bottom, left, leftTotal, right, scanStack, scanStackEmpty
    global size, sizeInﬁnity, space, token, rightTotal

    if rightTotal - leftTotal > space:

        if not scanStackEmpty:
            if left == scanStack[bottom]:
                size[ScanPopBottom()] = sizeInﬁnity

        AdvanceLeft(token[left], size[left])

        if not left == right:
            CheckStream()

#APPX ScanPush: PROCEDURE[x: CARDINAL]

def ScanPush(x: int):
    """Push the index of a token in the token buffer"""
    global scanStackEmpty, scanStack, top, bottom
    if scanStackEmpty:
        scanStackEmpty = False
    else:
        top = (top + 1) % len(scanStack)
        if top == bottom:
            raise Error("ScanStackFull")
    scanStack[top] = x

#APPX ScanPop: PROCEDURE RETURNS[x: CARDINAL]

def ScanPop() -> int:
    """Pop the index of a token in the token buffer"""
    global scanStackEmpty, scanStack, top, bottom
    if scanStackEmpty:
        raise Error("ScanStackEmpty")
    x = scanStack[top]
    if top == bottom:
        scanStackEmpty = True
    else:
        top = (top + len(scanStack) - 1) % len(scanStack)
    return x

#APPX ScanTop: PROCEDURE RETURNS[CARDINAL]

def ScanTop() -> int:
    """Return the token buffer index of the most recently added token"""
    global scanStackEmpty, scanStack, top, bottom
    if scanStackEmpty:
        raise Error("ScanStackEmpty")
    return scanStack[top]

#APPX ScanPopBottom: PROCEDURE RETURNS[x: CARDINAL]

def ScanPopBottom() -> int:
    """Return the token buffer index of the oldest token"""
    global scanStackEmpty, scanStack, top, bottom
    if scanStackEmpty:
        raise Error("ScanStackEmpty")
    x = scanStack[bottom]
    if top == bottom:
        scanStackEmpty = True
    else:
        bottom = (bottom + 1) % len(scanStack)
    return x

#APPX AdvanceRight: PROCEDURE

def AdvanceRight():
    """Advance the token buffer input index raise ERROR on buffer overflow"""
    global left, right, scanStack
    right = (right + 1) % len(scanStack)
    if right == left:
        raise Error("TokenQueueFull")

#APPX AdvanceLeft: PROCEDURE[x: Token, l: INTEGER]

def AdvanceLeft(x: Token, l: int):
    global leftTotal, left, right, size, token, scanStack
    if l >= 0:
        Print(x, l)

        if x == Break:
            leftTotal = leftTotal + x.blankSpace

        if x == String:
            leftTotal = leftTotal + l

        if left != right:
            left = (left + 1) % len(scanStack)
            AdvanceLeft(token[left], size[left])

#APPX CheckStack: PROCEDURE[k: INTEGER]

def CheckStack(k: int):
    global scanStackEmpty, size, rightTotal, token
    x: int
    if not scanStackEmpty:
        x = ScanTop()
        if token[x] == Begin:
            if k > 0:
                size[ScanPop()] = size[x] + rightTotal
                CheckStack(k - 1)
        elif token[x] == End:
            size[ScanPop()] = 1
            CheckStack(k + 1)
        else:
            size[ScanPop()] = size[x] + rightTotal
            if k > 0:
                CheckStack(k)

#APPX PrintNewLine: PROCEDURE[amount: CARDINAL]

def PrintNewLine(amount: int):
    PutChar(CR)  # output a carriage return
    for x in range(0, amount):
        PutChar(" ")  # indent

#APPX Indent: PROCEDURE[amount: CARDINAL]

def Indent(amount: int):
    for x in range(0, amount):
        PutChar(" ")  # indent

#APPX print stack handling
#
# We assume push, pop, and top are deﬁned on the stack printStack; printStack is a
# stack of records; each record contains two fields: the integer "offset" and a ﬂag "break"
# (which equals "ﬁts" if no breaks are needed (the block ﬁts on the line), or "consistent"
# or "inconsistent")

#APPX Print: PROCEDURE[x: Token, l: INTEGER]

def Print(x: Token, l: int):
    global space, margin
    if x == Begin:
        if l > space:
            Push(
                PrintStackEntry(
                    space - x.offset,
                    (
                        BreakType.consistent
                        if x.breakType == BreakType.consistent
                        else BreakType.inconsistent
                    ),
                )
            )
        else:
            entry = PrintStackEntry(0, BreakType.ﬁts)
            Push(entry)
    elif x == End:
        Pop()
    elif x == Break:
        if Top().brk == BreakType.fits:
            space = space - x.blankSpace
            Indent(x.blankSpace)
        elif Top().brk == BreakType.consistent:
            space = Top().offset - x.offset
            PrintNewLine(margin - space)
        elif Top().brk == BreakType.inconsistent:
            if l > space:
                space = Top().offset - x.offset
                PrintNewLine(margin - space)
            else:
                space = space - x.blankSpace
                Indent(x.blankSpace)
    elif x == String:
        if l > space:
            raise Error("LineTooLong")
        space = space - l
        PutString(x.string)
    else:
        raise Error("Invalid switch")

# Print stack definition

class PrintStackEntry:
    offset: int
    brk: BreakType

    def __init__(self, offset: int, brk: BreakType):
        self.brk = brk
        self.offset = offset

printStack: List[PrintStackEntry] = []

def Push(obj: PrintStackEntry):
    printStack.append(obj)

def Pop() -> PrintStackEntry:
    return printStack.pop()

def Top() -> PrintStackEntry:
    return printStack[-1]

# Public interface

def pprint(tokens=[], lineWidth=75):
    PrettyPrintInit(lineWidth=lineWidth)
    for t in tokens:
        PrettyPrint(t)
    return output.getvalue()

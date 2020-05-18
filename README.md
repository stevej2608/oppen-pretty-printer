## oppen-pretty-printer

This project is a faithful translation, to python, of the 
pretty-printing algorithm developed by DEREK C. OPPEN at Stanford  University 
in the late 1970s. The appendix of [PRETTY PRINTING, Derek C. Oppen, 1979] contains 
the original prettyprint program written in [MESA]

A much quoted, more recent algorithm, [A prettier printer, Philip Wadler 2003] refers to 
Oppen, saying, "The pretty printer presented here uses an algorithm equivalent to Oppen’s, but presented 
in a functional rather than an imperative style". Many of todays pretty printer implementations
are based on the Wadler algorithm. So, in a way, the road leads back to Derek C. Oppen, 1979.

Two python versions are included. `pretty_oppen.py` is, as far as possible, a 
line-by-line translation of the Oppen algorithm from [MESA] to Python. `pretty.py` is
functionally identical to `pretty_oppen.py` but written using a more Pythonic idiom.

Pytest tests and example output are included for both versions.


### Usage

	pip install oppen-pretty-printer

Example:
```
from oppen_pretty_printer import pprint, Token as T

tokens = [
    T.BEGIN(),
    T.STRING("begin"),
    T.STRING("x"),
    T.BREAK(), T.STRING(":="), T.BREAK(),
    T.STRING("40"),
    T.BREAK(), T.STRING("+"), T.BREAK(),
    T.STRING("2"),
    T.STRING("end"),
    T.END(),
    T.EOF()]

pprint(tokens)
```
	
### Overview

The pretty printer processes a sequence of the tokens BEGIN, END, STRING, BREAK, EOF.
The tokens BEGIN..END define a block that can contain any number of STRING and BREAK
tokens together with nested BEGIN..END sub-blocks. The pretty printer attempts
to keep the content of blocks together on the same line. If this is not possible
then the block is automatically folded and indented at a suitable BREAK. 

The STRING token holds a sequence of printable characters that will never be broken. The BRAKE token 
is a replacement for a sequence of non-printing, white-space, characters. A
BRAKE token is nominally printed as a `single-space` or, if 
folding takes place, `new-line-with-indent-and-offset`.

This example from Oppen's paper shows how the pretty printer deals with the same input for
different line widths.

```
width=75

        begin
          x := f(x); y := f(y); z := f(z); w := f(w);
          end;

width=24

        begin
          x := f(x); y := f(y);
          z := f(z); w := f(w);
          end;

width=75, BreakType.consistent

        begin
          x := f(x);
          y := f(y);
          z := f(z);
          w := f(w);
          end;
```

BLOCK and BREAK tokens can be parameterized, if needed, to modify the default folding
behaviour. The parameters are used to control indent, offset and the consistency of folding.

To create a pretty printer for a new language grammar it is normal to write a tree 
visitor using the visitor design-pattern. The visitor emits pretty-printer tokens 
as is traverses the program AST. The token sequence is passed to the pretty 
printer for printing. 

See **[odata-pretty-printer](https://github.com/stevej2608/odata-pretty-printer)** for an
example of traversing an AST and emitting `oppen-pretty-printer` tokens. For other
examples of usage see the pytest examples in this projects the `./tests` folder.


### Development

    pip install -r requirements.txt

    pytest

To run pytest on `pretty_oppen.py` use:

    pytest --oppen


publish:

    invoke publish 0.1.2 --pypi

**Links:** (copies in the docs folder)

* [PRETTY PRINTING, Derek C. Oppen, 1979]
* [A prettier printer, Philip Wadler 2003]
* [MESA]



[PRETTY PRINTING, Derek C. Oppen, 1979]: https://www.cs.tufts.edu/~nr/cs257/archive/derek-oppen/prettyprinting.pdf
[A prettier printer, Philip Wadler 2003]: http://homepages.inf.ed.ac.uk/wadler/papers/prettier/prettier.pdf
[MESA]: http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-79-3_Mesa_Language_Manual_Version_5.0.pdf

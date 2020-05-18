## oppen-pretty-printer

This package is a faithful translation, to python, of the 
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
	
## Documentation

Head over to the [*README*][docs-homepage] for more details.

## Contributing

The source code for *oppen-pretty-printer* is available
[on GitHub][opp-repo]. If you find a bug or something is unclear, we encourage
you to raise an issue. We also welcome contributions, to contribute, fork the
repository and open a [pull request][opp-pulls].

[opp-repo]: https://github.com/stevej2608/oppen-pretty-printer
[docs-homepage]: https://github.com/stevej2608/oppen-pretty-printer/blob/master/README.md
[opp-pulls]: https://github.com/stevej2608/oppen-pretty-printer/pulls
[PRETTY PRINTING, Derek C. Oppen, 1979]: https://www.cs.tufts.edu/~nr/cs257/archive/derek-oppen/prettyprinting.pdf
[A prettier printer, Philip Wadler 2003]: http://homepages.inf.ed.ac.uk/wadler/papers/prettier/prettier.pdf
[MESA]: http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-79-3_Mesa_Language_Manual_Version_5.0.pdf
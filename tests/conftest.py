import pytest

from oppen_pretty_printer import pprint as pprint_default, pprint_open


# https://docs.pytest.org/en/latest/example/simple.html#pass-different-values-to-a-test-function-depending-on-command-line-options

def pytest_addoption(parser):
    parser.addoption('--oppen', action='store_true', default=False, help='run pytest on pretty_oppen.py')


@pytest.fixture
def pprint(request):
    oppen = request.config.getoption("--oppen")
    if oppen:
        return pprint_open
    else:
        return pprint_default

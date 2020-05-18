
from termcolor import cprint
from shutil import which
from pathlib import Path


import semver

from invoke import run as invoke_run
from invoke import task


VERSION_TEMPLATE = """__version__ = "{version_string}"
"""

HERE = Path(__file__).parent

@task(help={"version": "Version number to publish", "pipy": "publish on pypi"})
def publish(_ctx, version, pipy=False):
    """
    Publish package with given version number to git and pypi
    """

    def python_sdist():
        run("python setup.py sdist")

    def release_python_sdist():

        if pipy:
            info("PyPI credentials:")
            invoke_run("twine upload dist/*", echo=True)
        else:
            run("python setup.py sdist upload -r pypicloud")


    def tag_in_use(tag):
        tags = run('git tag').split('\n')
        return tag in tags

    check_prerequisites()
    set_pyversion(version)

    python_sdist()

    if tag_in_use(f'v{version}'):
        error(f"Version tag {version} allready used!")
        exit(127)

    run(f'git commit -am "Bump version to {version}"')
    info(f"Tagging version {version} and pushing repository")

    run(f'git tag -a v{version} -m "Version v{version}"')
    run("git push origin master --tags")

    release_python_sdist()


def check_prerequisites():
    for executable in ["twine"]:
        if which(executable) is None:
            error(
                f"{executable} executable not found. "
                f"You must have {executable} to release "
                "test."
            )
            exit(127)


def set_pyversion(version):
    version = normalize_version(version)
    version_path = HERE / package_name() / "_version.py"
    with version_path.open("w") as f:
        f.write(VERSION_TEMPLATE.format(version_string=version))


def package_name():
    return "oppen_pretty_printer"


def normalize_version(version):
    version_info = semver.parse_version_info(version)
    version_string = str(version_info)
    return version_string


def run(command, **kwargs):
    print(f'{command}')
    result = invoke_run(command, hide=True, warn=True, **kwargs)
    if (result.exited is not None) and (result.exited != 0):
        error(f"Error running {command}")
        print(result.stdout)
        print()
        print(result.stderr)
        exit(result.exited)

    return result.stdout


def error(text):
    cprint(text, "red")


def info(text):
    print(text)

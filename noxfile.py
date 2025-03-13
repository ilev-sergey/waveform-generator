import shutil
from pathlib import Path

import nox

nox.options.error_on_external_run = True
nox.options.sessions = ["tests"]
nox.options.default_venv_backend = "uv|virtualenv"


@nox.session(python=["3.13", "3.12", "3.11", "3.10", "3.9", "3.8"])
def build(session):
    session.install("build", "twine")
    distdir = Path("dist")
    if distdir.exists():
        shutil.rmtree(distdir)
    session.run("python", "-m", "build")
    session.run("twine", "check", *distdir.glob("*"))


@nox.session(python=["3.13", "3.12", "3.11", "3.10", "3.9", "3.8"])
def tests(session):
    session.install(".[tests]")
    session.run("coverage", "run", "-m", "pytest", *session.posargs)
    session.notify("coverage")


@nox.session
def coverage(session):
    session.install("coverage")
    if any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")
    session.run("coverage", "report")

import nox


@nox.session
def lint(session):
    session.install("poetry")
    session.run("poetry", "install")
    session.run("poetry", "shell")
    session.run("black", "--check", "updater.py")
    session.run("pyflakes", "updater.py")


@nox.session
def typing(session):
    session.install("poetry")
    session.run("poetry", "install")
    session.run("poetry", "shell")
    session.run("mypy", "updater.py")

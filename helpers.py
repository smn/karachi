from fabric.api import *

def _staging():
    require("hosts", provided_by = ['test', 'development', 'production'])

rollbacks = []
def _add_rollback(rollback_function):
    rollbacks.append(rollback_function)


def _rollback():
    "Rollback the executed operations"
    print "rolling back %s operations" % len(rollbacks)
    [rollback_function() for rollback_function in rollbacks]


def _helpers_setup():
    "Setup the directory layout for the application to be deployed"
    _staging()
    cmd = "mkdir -p %s" % " ".join([
        "%(releases_path)s" % env,
        "%(shared_path)s" % env,
        "%(shared_path)s/logs" % env,
        "%(shared_path)s/tmp" % env,
    ])
    run(cmd % env)

def _helpers_checkout():
    "Checkout the repository"
    _add_rollback(lambda: run("rm -rf %(current_release)s" % env))
    _staging()
    run("git clone %(repository)s %(current_release)s" % env)
    with cd("%(current_release)s" % env):
        run("git checkout %(branch)s" % env)
        run("echo %(branch)s > BRANCH" % env)


def _helpers_symlink():
    "Symlink `current` to the latest release"
    _add_rollback(lambda: run("rm -f %(current_path)s && ln -s $PREVIOUS_RELEASE %(current_path)s" % env))
    _staging()
    run("export PREVIOUS_RELEASE=$(ls -1 %(releases_path)s | tail -1)" % env)
    run("rm -f %(current_path)s && ln -s %(current_release)s %(current_path)s" % env)


def _helpers_cleanup():
    "Cleanup old releases, keeping the last remaining 5"
    _staging()
    run("cd %(releases_path)s && ls -1 . | head --line=-5 | xargs rm -rf " % env)


def _helpers_releases():
    "Get a list of all the deployed releases"
    _staging()
    run("ls -x %(releases_path)s" % env)


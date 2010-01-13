from fabric.api import *

def staging():
    require("hosts", provided_by = ['test', 'development', 'production'])

rollbacks = []
def add_rollback(rollback_function):
    rollbacks.append(rollback_function)


def rollback():
    "Rollback the executed operations"
    print "rolling back %s operations" % len(rollbacks)
    [rollback_function() for rollback_function in rollbacks]


def setup():
    "Setup the directory layout for the application to be deployed"
    staging()
    cmd = "mkdir -p %s" % " ".join([
        "%(releases_path)s" % env,
        "%(shared_path)s" % env,
        "%(shared_path)s/logs" % env,
        "%(shared_path)s/tmp" % env,
    ])
    run(cmd % env)

def checkout():
    "Checkout the repository"
    add_rollback(lambda: run("rm -rf %(current_release)s" % env))
    staging()
    run("git clone %(repository)s %(current_release)s" % env)
    with cd("%(current_release)s" % env):
        # have the deploy branch track the branch specified in the config
        run("git checkout -b deploy origin/%(branch)s" % env)
        run("echo %(branch)s >> BRANCH" % env)


def symlink():
    "Symlink `current` to the latest release"
    add_rollback(lambda: run("rm -f %(current_path)s && ln -s $PREVIOUS_RELEASE %(current_path)s" % env))
    staging()
    run("export PREVIOUS_RELEASE=$(ls -1 %(releases_path)s | tail -1)" % env)
    run("rm -f %(current_path)s && ln -s %(current_release)s %(current_path)s" % env)


def cleanup():
    "Cleanup old releases, keeping the last remaining 5"
    staging()
    run("cd %(releases_path)s && ls -1 . | head --line=-5 | xargs rm -rf " % env)


def releases():
    "Get a list of all the deployed releases"
    staging()
    run("ls -x %(releases_path)s" % env)


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
        "%(shared_path)s/repositories" % env,
    ])
    run(cmd % env)

def get_previous_release():
    if 'previous_release' not in env:
        env.previous_release = run("ls -1 %(releases_path)s | tail -2 | head -1" % env)
    

# def checkout():
#     "Checkout the repository"
#     add_rollback(lambda: run("rm -rf %(current_release)s" % env))
#     staging()
#     run("git clone %(repository)s %(current_release)s/%(project)s" % env)
#     with cd("%(current_release)s/%(project)s" % env):
#         # have the deploy branch track the branch specified in the config
#         run("git checkout -b deploy origin/%(branch)s" % env)
#         run("echo %(branch)s >> BRANCH" % env)
# 

def checkout():
    add_rollback(lambda: run("rm -rf %(current_release)s" % env))
    staging()
    # run a check to see if we've already got a repository checked out
    cold_check = run("if [ -d %(shared_path)s/repositories/%(project)s ]; then "
                    "echo 'warm'; "
                "else "
                    "echo 'cold'; fi" % env)
    # if it's a cold start then checkout the full repository and switch to the 
    # deploy branch
    if cold_check == "cold":
        run("git clone %(repository)s %(shared_path)s/repositories/%(project)s" % env)
    
    # update the now warm repository to the latest code
    with cd("%(shared_path)s/repositories/%(project)s" % env):
        run("git pull")
    
    # create the release path
    run("mkdir -p %(current_release)s/%(project)s" % env)
    # copy it to the current release path
    run("cp -RPp %(shared_path)s/repositories/%(project)s %(current_release)s/" % env)
    with cd("%(current_release)s/%(project)s" % env):
        run("git checkout -b deploy origin/%(branch)s" % env)
        run("echo %(branch)s >> BRANCH" % env)
        run("echo `git rev-list --max-count=1 deploy` >> REVISION" % env)

def copy_settings_files():
    add_rollback(lambda: run("rm -rf %(current_release)s" % env))
    staging()
    put(
        "~/Documents/Repositories/txtalert/environments/live/%(branch)s.py" % env,
        "%(current_release)s/%(project)s/environments/live/%(branch)s.py" % env
    )
    put(
        "~/Documents/Repositories/txtalert/environments/live/testing.py" % env,
        "%(current_release)s/%(project)s/environments/live/testing.py" % env
    )


def symlink_current():
    "Symlink `current` to the latest release"
    get_previous_release()
    add_rollback(lambda: run("rm -f %(current_path)s && ln -s %(previous_release)s %(current_path)s" % env))
    staging()
    run("rm -f %(current_path)s && ln -s %(current_release)s %(current_path)s" % env)


def symlink_tmp():
    staging()
    run("rm -rf %(current_release)s/%(project)s/tmp && ln -s %(shared_path)s/tmp %(current_release)s/%(project)s/tmp" % env)
    

def symlink_logs():
    staging()
    run("rm -rf %(current_release)s/%(project)s/logs && ln -s %(shared_path)s/logs %(current_release)s/%(project)s/logs" % env)
    

def cleanup():
    "Cleanup old releases, keeping the last remaining 5"
    staging()
    run("cd %(releases_path)s && ls -1 . | head --line=-5 | xargs rm -rf " % env)


def releases():
    "Get a list of all the deployed releases"
    staging()
    run("ls -x %(releases_path)s" % env)


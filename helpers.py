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
    sudo(cmd % env, user=env.sudo_user)

def get_previous_release():
    if 'previous_release' not in env:
        env.previous_release = run("ls -1 %(releases_path)s | tail -2 | head -1" % env)
    

def checkout():
    add_rollback(lambda: sudo("rm -rf %(current_release)s" % env, user=env.sudo_user))
    staging()
    
    # run a check to see if we've already got a repository checked out
    cold_check = run("if [ -d %(shared_path)s/repositories/%(project)s ]; then "
                    "echo 'warm'; "
                "else "
                    "echo 'cold'; fi" % env)
    # if it's a cold start then checkout the full repository and switch to the 
    # deploy branch
    if cold_check == "cold":
        sudo("git clone %(repository)s %(shared_path)s/repositories/%(project)s" % env, user=env.sudo_user)
    
    # update the now warm repository to the latest code
    with cd("%(shared_path)s/repositories/%(project)s" % env):
        sudo("git pull", user=env.sudo_user)
    
    # create the release path
    sudo("mkdir -p %(current_release)s/%(project)s" % env, user=env.sudo_user)
    # copy it to the current release path
    sudo("cp -RPp %(shared_path)s/repositories/%(project)s %(current_release)s/" % env, user=env.sudo_user)
    with cd("%(current_release)s/%(project)s" % env):
        sudo("git checkout -b deploy origin/%(branch)s" % env, user=env.sudo_user)
        sudo("echo %(branch)s >> BRANCH" % env, user=env.sudo_user)
        sudo("echo `git rev-list --max-count=1 deploy` >> REVISION" % env, user=env.sudo_user)


def symlink_current():
    "Symlink `current` to the latest release"
    get_previous_release()
    add_rollback(lambda: sudo("rm -f %(current_path)s && ln -s %(previous_release)s %(current_path)s" % env, user=env.sudo_user))
    staging()
    sudo("rm -f %(current_path)s && ln -s %(current_release)s %(current_path)s" % env, user=env.sudo_user)


def symlink_tmp():
    staging()
    sudo("rm -rf %(current_release)s/%(project)s/tmp && ln -s %(shared_path)s/tmp %(current_release)s/%(project)s/tmp" % env, user=env.sudo_user)
    

def symlink_logs():
    staging()
    sudo("rm -rf %(current_release)s/%(project)s/logs && ln -s %(shared_path)s/logs %(current_release)s/%(project)s/logs" % env, user=env.sudo_user)
    

def cleanup():
    "Cleanup old releases, keeping the last remaining 5"
    staging()
    sudo("cd %(releases_path)s && ls -1 . | head --line=-5 | xargs rm -rf " % env, user=env.sudo_user)


def releases():
    "Get a list of all the deployed releases"
    staging()
    return sudo("ls -x %(releases_path)s" % env, user=env.sudo_user).split()


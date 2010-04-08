from fabric.api import *
import helpers

def checkout_code():
    """
    Do a git clone or pull depending on whether this is a cold deploy or not
    """
    helpers.check_minimum_requirements()
    
    # remove the newest release completely if something goes wrong
    helpers.add_rollback("Removing checkout of project '%(current_release)s'" % env, 
                            lambda: sudo("rm -rf %(current_release)s" % env, user=env.sudo_user))
    
    # FIXME:    this is hacky, we should have a file.exists() type if function
    #           to check the server if a file exists
    
    # run a check to see if we've already got a repository checked out
    cold_check = run("if [ -d %(shared_path)s/repositories/%(project)s ]; then "
                    "echo 'warm'; "
                "else "
                    "echo 'cold'; fi" % env)
    
    # FIXME:    this probably needs to be split into two different functions,
    #           one that does 'git clone' and the other that does 'git pull'
    
    # if it's a cold start then checkout the full repository and switch to the 
    # deploy branch
    if cold_check == "cold":
        sudo("git clone %(repository)s %(shared_path)s/repositories/%(project)s" % env, user=env.sudo_user)
    
    # update the now warm repository to the latest code, pointless if we've
    # just cloned
    with cd("%(shared_path)s/repositories/%(project)s" % env):
        sudo("git pull", user=env.sudo_user)
    
    # create the release path
    sudo("mkdir -p %(current_release)s/%(project)s" % env, user=env.sudo_user)
    # copy it to the current release path
    sudo("cp -RPp %(shared_path)s/repositories/%(project)s %(current_release)s/" % env, user=env.sudo_user)
    with cd("%(current_release)s/%(project)s" % env):
        # create a new local deploy branch, tracking the development/production 
        # branches in origin
        sudo("git checkout -b deploy origin/%(branch)s" % env, user=env.sudo_user)
        # store the BRANCH and REVISION in a local file for future reference
        # when the shit certainly sometime will hit the fan
        sudo("echo %(branch)s >> BRANCH" % env, user=env.sudo_user)
        sudo("echo `git rev-list --max-count=1 deploy` >> REVISION" % env, user=env.sudo_user)



from __future__ import with_statement # for python 2.5
from fabric.api import *
import logging

def check_minimum_requirements():
    """
    make sure we have the bare essentials needed for doing anything
    """
    require("hosts", provided_by = ['development', 'production'])


# a list of callbacks to call when a rollback() is required. This is like a
# deploy-level undo, not guaranteed to be 100% accurate.
rollbacks = []
def add_rollback(name, callback):
    """Add a callback to the rollback stack"""
    rollbacks.append((name, callback))


def rollback():
    "Execute all the callbacks in rollback one by one"
    logging.error("rolling back %s operations" % len(rollbacks))
    while rollbacks:
        name, callback = rollbacks.pop()
        logging.error("Rolling back: %s (%s)" % (name, callback))
        callback()


def setup():
    "Setup the directory layout for the application to be deployed"
    check_minimum_requirements()
    cmd = "mkdir -p %s" % " ".join([
        "%(releases_path)s" % env,
        "%(shared_path)s" % env,
        "%(shared_path)s/logs" % env,
        "%(shared_path)s/tmp" % env,
        "%(shared_path)s/repositories" % env,
    ])
    sudo(cmd % env, user=env.sudo_user)

def store_previous_release():
    """Store the previous release in the env dictionary for future use"""
    if 'previous_release' not in env:
        env.previous_release = run("ls -1 %(releases_path)s | tail -2 | head -1" % env)
    return env.previous_release

def symlink_current():
    "Symlink `current` to the latest release"
    check_minimum_requirements()
    store_previous_release()
    add_rollback("Relinking 'current' to 'previous_release'", lambda: sudo("rm -f %(current_path)s && ln -s %(previous_release)s %(current_path)s" % env, user=env.sudo_user))
    sudo("rm -f %(current_path)s && ln -s %(current_release)s %(current_path)s" % env, user=env.sudo_user)


def symlink_tmp():
    check_minimum_requirements()
    sudo("rm -rf %(current_release)s/%(project)s/tmp && ln -s %(shared_path)s/tmp %(current_release)s/%(project)s/tmp" % env, user=env.sudo_user)
    

def symlink_logs():
    check_minimum_requirements()
    sudo("rm -rf %(current_release)s/%(project)s/logs && ln -s %(shared_path)s/logs %(current_release)s/%(project)s/logs" % env, user=env.sudo_user)
    

def cleanup(release_limit=5):
    "Cleanup old releases, keeping the last remaining 5"
    check_minimum_requirements()
    tmp_env = env.copy()
    tmp_env.update({'release_limit': release_limit})
    sudo("cd %(releases_path)s && ls -1 . | head --line=-%(release_limit)s | xargs rm -rf " % tmp_env, user=env.sudo_user)


def releases():
    "Get a list of all the deployed releases"
    check_minimum_requirements()
    return sudo("ls -x %(releases_path)s" % env, user=env.sudo_user).split()


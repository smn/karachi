from __future__ import with_statement

from datetime import datetime
from fabric.api import *
import helpers
import git
import logging

def development():
    env.hosts = ["ovm1.praekelt.com"]
    env.branch = "development"
    env.fcgi_port = '9991'
    env.deploy_to = "/var/praekelt/dev/txtalert"
    env.django_settings = 'environments.live.development'
    _defaults()

def production():
    env.hosts = ["ovm1.praekelt.com"]
    env.branch = "production"
    env.fcgi_port = '9992'
    env.deploy_to = '/var/praekelt/live/txtalert'
    env.django_settings = 'environments.live.production'
    _defaults()

def _defaults():
    env.project = 'txtalert'
    env.user = "sdehaan"
    env.sudo_user = "www-data"
    env.repository = "git://github.com/smn/txtalert.git"
    
    env.fcgi_host = '127.0.0.1'
    env.fcgi_protocol = 'fcgi'
    env.fcgi_pidfile = '%(deploy_to)s/current/%(project)s/tmp/%(project)s_%(branch)s.pid' % env
    env.fcgi_outlog = '%(deploy_to)s/current/%(project)s/logs/fcgi_%(branch)s.log' % env
    env.fcgi_errlog = '%(deploy_to)s/current/%(project)s/logs/fcgi_%(branch)s_err.log' % env
    env.fcgi_debug = 'true'
    
    env.release_format = '%Y%m%d%H%M%S'
    env.releases_path = "%(deploy_to)s/releases" % env
    env.current_path = "%(deploy_to)s/current" % env
    env.shared_path = "%(deploy_to)s/shared" % env


def setup():
    "Create the necessary directory layout for a deploy"
    helpers.setup()

def deploy():
    try: 
        "Build the project and deploy it to a specified environment"
        
        env.release_name = datetime.utcnow().strftime(env.release_format)
        env.current_release = "%(releases_path)s/%(release_name)s" % env
        
        helpers.setup()
        git.checkout_code()
        copy_settings_file("%(branch)s.py" % env)
        helpers.symlink_current()
        helpers.symlink_tmp()
        helpers.symlink_logs()
    except Exception, e:
        logging.exception(e)
        helpers.rollback()

def update():
    try:
        git.update_code()
    except Exception, e:
        logging.exception(e)
        helpers.rollback()

def start():
    helpers.check_minimum_requirements()
    sudo('python %(current_path)s/%(project)s/manage.py '
            'runfcgi --settings=%(django_settings)s host=%(fcgi_host)s '
            'port=%(fcgi_port)s protocol=%(fcgi_protocol)s '
            'outlog=%(fcgi_outlog)s '
            'errlog=%(fcgi_errlog)s '
            'debug=%(fcgi_debug)s '
            'pidfile=%(fcgi_pidfile)s' % env, user=env.sudo_user)


def stop():
    helpers.check_minimum_requirements()
    sudo('if [ -f %(fcgi_pidfile)s ]; then kill -HUP `cat %(fcgi_pidfile)s`; fi' % env, user=env.sudo_user)

def restart():
    stop()
    start()

def test():
    if 'current_release' in env:
        app_path = "%(current_release)s/%(project)s" % env
    else:
        app_path = "%(current_path)s/%(project)s" % env
    copy_settings_file("testing.py")
    sudo("python %s/manage.py test --settings=environments.live.testing --failfast" % (app_path,), user=env.sudo_user)


def copy_settings_file(file_name):
    # def remove_settings_files_rollback():
    #     sudo("rm -rf %(current_path)s/%(project)s/environments/live/%(branch)s.py" % env, user=env.sudo_user)
    #     sudo("rm -rf %(current_path)s/%(project)s/environments/live/testing.py" % env, user=env.sudo_user)
    # helpers.add_rollback("Removing settings files", remove_settings_files_rollback)
    helpers.check_minimum_requirements()
    run("mkdir -p ~/fabrictmp")
    put(
        "~/Documents/Repositories/txtalert/environments/live/%s" % file_name,
        "~/fabrictmp/%s" % file_name
    )
    sudo(
        "cp ~/fabrictmp/%s "
        "%s/%s/environments/live/%s" % (
            file_name,
            env.current_path,
            env.project,
            file_name
        ), 
        user=env.sudo_user
    )
    run("rm ~/fabrictmp/%s" % file_name)
    run("rmdir ~/fabrictmp")


def cleanup():
    helpers.cleanup()

def releases():
    releases = helpers.releases()
    print "%s Releases:\n\t" % len(releases) + '\n\t'.join(releases)

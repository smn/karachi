from datetime import datetime
from fabric.api import *
import helpers

def test():
    env.hosts = ["testing.server"]


def development():
    env.hosts = ["ovm1.praekelt.com"]
    env.branch = "development"
    env.fcgi_port = '9991'
    env.deploy_to = "/var/praekelt/dev/txtalert"
    env.django_settings = 'environments.live.development'

def production():
    env.hosts = ["ovm1.praekelt.com"]
    env.branch = "production"
    env.fcgi_port = '9992'
    env.deploy_to = '/var/praekelt/live/txtalert'
    env.django_settings = 'environments.live.production'


def _defaults():
    env.project = 'txtalert'
    env.user = "sdehaan"
    env.sudo_user = "www-data"
    env.repository = "git://github.com/smn/txtalert.git"
    
    env.fcgi_host = '127.0.0.1'
    env.fcgi_protocol = 'fcgi'
    env.fcgi_pidfile = '%(deploy_to)s/current/txtalert/tmp/txtalert_dev.pid' % env
    env.fcgi_outlog = '%(deploy_to)s/current/txtalert/logs/fcgi.log' % env
    env.fcgi_errlog = '%(deploy_to)s/current/txtalert/logs/fcgi-err.log' % env
    env.fcgi_debug = 'true'
    
    env.release_name = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    env.releases_path = "%(deploy_to)s/releases" % env
    env.current_release = "%(releases_path)s/%(release_name)s" % env
    
    env.current_path = "%(deploy_to)s/current" % env
    env.shared_path = "%(deploy_to)s/shared" % env


def setup():
    "Create the necessary directory layout for a deploy"
    _defaults()
    helpers.setup()

def deploy():
    try: 
        "Build the project and deploy it to a specified environment"
        _defaults()
        helpers.setup()
        helpers.checkout()
        helpers.copy_settings_files()
        # run_tests()
        helpers.symlink_current()
        helpers.symlink_tmp()
        helpers.symlink_logs()
    except Exception, e:
        print e
        helpers.rollback()

def start_django():
    helpers.staging()
    _defaults()
    sudo('python %(current_path)s/%(project)s/manage.py '
            'runfcgi --settings=%(django_settings)s host=%(fcgi_host)s '
            'port=%(fcgi_port)s protocol=%(fcgi_protocol)s '
            'outlog=%(fcgi_outlog)s '
            'errlog=%(fcgi_errlog)s '
            'debug=%(fcgi_debug)s '
            'pidfile=%(fcgi_pidfile)s' % env, user=env.sudo_user)


def stop_django():
    helpers.staging()
    _defaults()
    sudo('if [ -f %(fcgi_pidfile)s ]; then kill -HUP `cat %(fcgi_pidfile)s`; fi' % env, user=env.sudo_user)

def restart_django():
    stop_django()
    start_django()

def run_tests():
    sudo("python %(current_release)s/%(project)s/manage.py test --settings=environments.live.testing" % env, user=env.sudo_user)



def cleanup():
    _defaults()
    helpers.cleanup()

def releases():
    _defaults()
    helpers.releases()
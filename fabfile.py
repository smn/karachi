from datetime import datetime
from fabric.api import *
import helpers

def test():
    env.hosts = ["testing.server"]


def development():
    env.hosts = ["ovm1.praekelt.com"]
    env.branch = "development"
    env.fcgi_host = '127.0.0.1'
    env.fcgi_port = '9991'
    env.fcgi_protocol = 'fcgi'
    env.fcgi_pidfile = '/var/run/django/txtalert_dev.pid'
    env.django_settings = 'environments.development'

def production():
    env.hosts = ["production.server"]
    env.branch = "production"


def _defaults():
    env.project = 'txtalert'
    env.user = "sdehaan"
    env.deploy_to = "/home/sdehaan/development/fabric/txtalert"
    env.repository = "git://github.com/smn/txtalert.git"
    
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
        helpers.symlink()
    except Exception, e:
        print e
        _rollback()

def start_django():
    helpers.staging()
    _defaults()
    run('python %(current_path)s/manage.py '
            'runfcgi --settings=%(django_settings)s host=%(fcgi_host)s '
            'port=%(fcgi_port)s protocol=%(fcgi_protocol)s '
            'pidfile=%(fcgi_pidfile)s' % env)


def stop_django():
    _defaults()
    helpers.staging()
    run('kill -HUP `cat %(fcgi_pidfile)s`' % env)

def cleanup():
    _defaults()
    helpers.cleanup()

def releases():
    _defaults()
    helpers.releases()
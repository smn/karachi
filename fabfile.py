from datetime import datetime
from fabric.api import *
import helpers

def test():
    env.hosts = ["testing.server"]
    _defaults()


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
    
    env.release_name = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    env.releases_path = "%(deploy_to)s/releases" % env
    env.current_release = "%(releases_path)s/%(release_name)s" % env
    
    env.current_path = "%(deploy_to)s/current" % env
    env.shared_path = "%(deploy_to)s/shared" % env


def setup():
    "Create the necessary directory layout for a deploy"
    helpers.setup()

def deploy():
    try: 
        "Build the project and deploy it to a specified environment"
        helpers.setup()
        helpers.checkout()
        copy_settings_files()
        # run_tests()
        helpers.symlink_current()
        helpers.symlink_tmp()
        helpers.symlink_logs()
    except Exception, e:
        print e
        helpers.rollback()


def start_django():
    helpers.staging()
    sudo('python %(current_path)s/%(project)s/manage.py '
            'runfcgi --settings=%(django_settings)s host=%(fcgi_host)s '
            'port=%(fcgi_port)s protocol=%(fcgi_protocol)s '
            'outlog=%(fcgi_outlog)s '
            'errlog=%(fcgi_errlog)s '
            'debug=%(fcgi_debug)s '
            'pidfile=%(fcgi_pidfile)s' % env, user=env.sudo_user)


def stop_django():
    helpers.staging()
    sudo('if [ -f %(fcgi_pidfile)s ]; then kill -HUP `cat %(fcgi_pidfile)s`; fi' % env, user=env.sudo_user)

def restart_django():
    stop_django()
    start_django()

def run_tests():
    sudo("python %(current_release)s/%(project)s/manage.py test --settings=environments.live.testing" % env, user=env.sudo_user)


def copy_settings_files():
    helpers.add_rollback(lambda: sudo("rm -rf %(current_release)s" % env, user=env.sudo_user))
    helpers.staging()
    run("mkdir -p ~/fabrictmp")
    put(
        "~/Documents/Repositories/txtalert/environments/live/%(branch)s.py" % env,
        "~/fabrictmp/%(branch)s.py" % env
    )
    sudo(
        "cp ~/fabrictmp/%(branch)s.py "
        "%(current_release)s/%(project)s/environments/live/%(branch)s.py" % env, 
        user=env.sudo_user
    )
    put(
        "~/Documents/Repositories/txtalert/environments/live/testing.py",
        "~/fabrictmp/testing.py"
    )
    sudo(
        "cp ~/fabrictmp/testing.py "
        "%(current_release)s/%(project)s/environments/live/testing.py" % env,
        user=env.sudo_user
    )
    run("rm ~/fabrictmp/%(branch)s.py" % env)
    run("rm ~/fabrictmp/testing.py" % env)
    run("rmdir ~/fabrictmp")


def cleanup():
    helpers.cleanup()

def releases():
    releases = helpers.releases()
    print "%s Releases:\n\t" % len(releases) + '\n\t'.join(releases)

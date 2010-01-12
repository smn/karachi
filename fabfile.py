from datetime import datetime
from fabric.api import env
from helpers import (_helpers_setup, _helpers_checkout, _helpers_symlink,
                        _rollback, _helpers_cleanup, _helpers_releases)

def test():
    env.hosts = ["testing.server"]


def development():
    env.hosts = ["development.server"]


def production():
    env.hosts = ["production.server"]


def _defaults():
    env.project = 'txtalert'
    env.user = "sdehaan"
    env.deploy_to = "/home/sdehaan/development/fabric/txtalert"
    
    env.repository = "git://github.com/smn/txtalert.git"
    env.branch = "master"
    
    env.release_name = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    env.releases_path = "%(deploy_to)s/releases" % env
    env.current_release = "%(releases_path)s/%(release_name)s" % env
    
    env.current_path = "%(deploy_to)s/current" % env
    env.shared_path = "%(deploy_to)s/shared" % env


def setup():
    "Create the necessary directory layout for a deploy"
    _defaults()
    _helpers_setup()

def deploy():
    try: 
        "Build the project and deploy it to a specified environment"
        _defaults()
        _helpers_setup()
        _helpers_checkout()
        _helpers_symlink()
    except Exception, e:
        print e
        _rollback()

def cleanup():
    _defaults()
    _helpers_cleanup()

def releases():
    _defaults()
    _helpers_releases()
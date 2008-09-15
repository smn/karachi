def test():
    set(fab_hosts = ["ubuntumini.local"])


def development():
    set(fab_hosts = ["ubuntumini.local"])


def production():
    set(fab_hosts = ["ubuntumini.local"])


set(
    project = 'fajango',
    fab_user = "deployer",
    deploy_to = "/home/deployer/fajango",
    release_name = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S'),
    repository = "http://kathmandu.googlecode.com/svn/trunk/",
    revision = "HEAD"
)


class Fajango:

    INITIAL_DIRS = [
        "$(deploy_to)/releases",
        "$(deploy_to)/shared",
        "$(deploy_to)/shared/logs",
        "$(deploy_to)/shared/tmp",
    ]
    
    @staticmethod
    def setup():
        "Setup the directory layout for the application to be deployed"
        require("fab_hosts", provided_by = [test, development, production])
        run("mkdir -p %s" % " ".join(Fajango.INITIAL_DIRS))
    

    @staticmethod
    def checkout():
        "Checkout the SVN repository"
        require("fab_hosts", provided_by = [test, development, production])
        run("svn co -r $(revision) $(repository) $(deploy_to)/releases/$(release_name)")
    


def deploy():
    "Build the project and deploy it to a specified environment"
    require("fab_hosts", provided_by = [test, development, production])
    Fajango.setup()
    Fajango.checkout()
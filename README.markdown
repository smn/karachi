Originally developed for Fabric 0.1 but somewhat ported over to 1.0a. Still needs some love even though it is slightly usable.

usage: fab `environment` `command`

**fab development setup**

will create the following directory structure:

releases/ # timestamped releases
		20100112214510/
		20100112222418/
		...

shared/	# stuff that's shared between deploys
		logs/
		tmp/
		repositories/

current # symlinks to one of the releases

**fab development deploy**

will: 

1. create a new timestamped release folder
2. clone a git repository in it
3. have the `current` symlink point at it
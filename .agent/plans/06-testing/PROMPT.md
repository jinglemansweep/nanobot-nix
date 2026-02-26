* When gateway container starts up, it creates a directory called "*" in the skills directory. Looks like the allowed package variable isn't working as expected.
* Docker-Compose file should ideally run as local user allowing local files/resources to be mounted in without breaking/overwriting permissions, but i believe Docker image runs as root. Don't change the container setup too much

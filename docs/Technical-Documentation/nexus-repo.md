# Nexus Artifact Repository

We are using Nexus as an artifact store in order to retain docker images and other artifacts needed for our apps and pipelines.

Nexus UI can be accessed at [https://tdp-nexus.dev.raftlabs.tech/](https://tdp-nexus.dev.raftlabs.tech/)

## Hosted Docker Repository

### Setup

In order to use Nexus as a Docker repository, the DNS for the repo needs to be able to terminate https. We are currently using cloudflare to do this.

When creating the repository (must be signed in with admin privileges), since the nexus server isn't actually terminating the https, select the HTTP repository connector. The port can be anything you assign, as long as the tool used to terminate the https connection forwards the traffic to that port. 

In order to allow [Docker client login and connections](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/docker-registry/docker-authentication) you must set up the Docker Bearer Token Realm in Settings -> Security -> Realms -> and move the Docker Bearer Token Realm over to Active.
Also, any users will need nx-repository-view-docker-#{RepoName}-(browse && read) at a minimum and (add and edit) in order to push images.

We have a separate endpoint to connect specifically to the docker repository.
[https://tdp-docker.dev.raftlabs.tech](tdp-docker.dev.raftlabs.tech)

e.g. `docker login https://tdp-docker.dev.raftlabs.tech`

### Pushing Images

Before an image can be pushed to the nexus repository, it must be tagged for that repo:

`docker image tag ${ImageId} tdp-docker.dev.raftlabs.tech/${ImageName}:${Version}`

then you can push:

`docker push tdp-docker.dev.raftlabs.tech/${ImageName}:${Version}`

### Pulling Images

`docker pull tdp-docker.dev.raftlabs.tech/${ImageName}:${Version}`
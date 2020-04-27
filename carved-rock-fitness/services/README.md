# Login to Docker Hub

`docker login`

# Create a Secret with Docker Hub Credentials

`kubectl create secret generic regcred --from-file=.dockerconfigjson=$HOME/.docker/config.json --type=kubernetes.io/dockerconfigjson`

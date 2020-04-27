# Introduction

The examples use `doomhammer` as the Docker Hub user name. If you want build,
push, and use your own images, substitute `doomhammer` with your user name.

# Build the image

`docker build . -t doomhammer/carvedrock:run-controller`

# Push the image

`docker push doomhammer/carvedrock:run-controller`

# Apply the Deployment manifest

`kubectl apply -f deployment.yaml`

# Apply the Service manifest

`kubectl apply -f service.yaml`

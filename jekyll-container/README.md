# Build
buildah bud --format docker -f Containerfile -t jekyll

# Run
podman run -it --net=host -v $(pwd):/site:z localhost/jekyll

Then run 'make serve' from the /site folder.

# Browse
http://127.0.0.1:4000/


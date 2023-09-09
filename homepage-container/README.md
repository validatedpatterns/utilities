# Homepage Container

## Run

If you want to just run the homepage container do:

```shell
podman run -it --net=host -v $(pwd):/site:z quay.io/hybridcloudpatterns/homepage-container:latest
make serve
```

## Build the container

```shell
buildah bud --format docker -f Containerfile -t homepage-container
```

## Run the built container

```shell
podman run -it --net=host -v $(pwd):/site:z localhost/homepage-container
```

Then run `make serve` from the /site folder.

* Browse [http://127.0.0.1:4000/](http://127.0.0.1:4000/)
* Upload the container to the quay.io org

```shell
buildah push localhost/homepage-container:latest quay.io/hybridcloudpatterns/homepage-container:latest
```

# Homepage Container

## Automatic build

Any pushes to main will automatically trigger a rebuild and a push in the quay.io/validatedpatterns/homepage-container
repository

## Run

If you want to just run the homepage container do:

```shell
podman run -it --net=host -v $(pwd):/site:z quay.io/validatedpatterns/homepage-container:latest
make serve
```

## Build the container

```shell
make build
```

Optionally you can set the Hugo version via the `HUGO_VERSION` env variable.

## Run the built container

```shell
podman run -it --net=host -v $(pwd):/site:z localhost/homepage-container
```

Then run `make serve` from the /site folder.

- Browse [http://127.0.0.1:4000/](http://127.0.0.1:4000/)
- Upload the container to the quay.io org

```shell
buildah push localhost/homepage-container:latest quay.io/validatedpatterns/homepage-container:latest
```

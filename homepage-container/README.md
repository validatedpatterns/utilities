* Run
If you want to just run the homepage container do:
```
podman run -it --net=host -v $(pwd):/site:z quay.io/hybridcloudpatterns/homepage-container:latest
make serve
```

* Build the container
```
buildah bud --format docker -f Containerfile -t homepage-container
```

* Run the built container
```
podman run -it --net=host -v $(pwd):/site:z localhost/homepage-container
```

Then run `make serve` from the /site folder.

* Browse
http://127.0.0.1:4000/

* Upload the container to the quay.io org
```
buildah push localhost/homepage-container:latest quay.io/hybridcloudpatterns/homepage-container:latest
```

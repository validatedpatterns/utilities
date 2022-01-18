# utilities repository

This repo includes a set of (hopefully) utilities that can be used to query namespaces,
operators, argocd projects and argocd applications in an OpenShift cluster.

This is still work in progress so we will be re-arranging a lot of the code in the near future.

## Requirements

The openshift directory contains a classes that can be used in an OpenShift cluster environment.
The class library uses the [OpenShift Rest CLI](https://github.com/openshift/openshift-restclient-python)
to make the proper calls to the OpenShift api.

To install you can follow the Installation instructions found in the README.

We also make use of the `python3-pyyaml` library to parse YAML files. You will have to install
the package on your system using DNF, apt-get or pip.

## Directories

| Directory | Description |
| ------ | ------ |
| aws-tools | This directory contains some S3 tools and EC2  tools |
| openshift | This directory contains the helper classes for openshift |

If you have any questions please contact [Lester Claudio](claudiol@redhat.com) or [Jonny Rickard](jrickard@redaht.com)

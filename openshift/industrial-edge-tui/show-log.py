import sys
import os
import getopt
from kubernetes import config, dynamic, client
from kubernetes.client import api_client

import pod as op

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hn:p:"

# Long options
long_options = ["help", "namespace", "pod"]

def usage():
    msg = "Usage: python " + sys.argv[0] + "\n"  \
        "Options: \n" \
        " -n or --namespace \n" \
        "    namespace for operator search that is included in the name of the operator.  \n" \
        "    Example: -n pipelines \n" \
        " -p or --pod \n" \
        "    namespace for operator search that is included in the name of the operator.  \n" \
        "    Example: -p line-dashboard-7cbd6885cb-pmksb\n" \
        " -h or --help \n" \
        "    Usage message"
    print(msg)
    exit()


KUBE_CONFIG = os.getenv('KUBECONFIG')

def get_dynamic_client_instance():
    """
    Create a client instance for the Kubernetes API
    :rtype: DynamicClient
    """

    dynamic_client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.
                             load_kube_config(KUBE_CONFIG)))

    return dynamic_client

def get_name_object_given_namespace(namespace, kind_object):

    objects = []

    try:
        dynamic_client = get_dynamic_client_instance()

        api = dynamic_client.resources.get(api_version="v1", kind=kind_object)

        for item in api.get(namespace=namespace).items:
            print(item.metadata.name)
            objects.append(item.metadata.name)

        return objects

    except dynamic.exceptions.ApiException as ex:
        print("Got Kubernetes Exception: ", ex)

def get_pod_logs(pod_name, namespace):

    api = client.CoreV1Api()
    api_response = api.read_namespaced_pod_log(
        name=pod_name, namespace=namespace)
    print(api_response)


def main():

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        if len(arguments) == 0:
            usage()
        # checking each argument
        for currentArgument, currentValue in arguments:            
            if currentArgument in ("-h", "--help"):
                usage()
            elif currentArgument in ("-p", "--pod"):
                print ("Adding filter: ", currentValue, " to search for OpenShift Operators")
                podname=currentValue
            elif currentArgument in ("-n", "--namespace"):
                print ("Adding filter: ", currentValue, " to search for OpenShift Operators")
                namespace=currentValue

        pod_instance = op.Pods(namespace)
        response = pod_instance.getPodLogs(podname, namespace)
        print (response)
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()


if __name__ == "__main__":
    sys.exit(main())

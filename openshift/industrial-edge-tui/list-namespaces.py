from kubernetes import client, config
from openshift.dynamic import DynamicClient

# Python imports
import sys
import getopt

import namespace as ns

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hf:a"

# Long options
long_options = ["help", "filter", "all"]

def usage():
    msg = "Usage: python " + sys.argv[0] + "\n"  \
        "Options: \n" \
        " -f or --filter \n" \
        "    Filter for cluster search. Will be added to the *master* and *worker* filter \n" \
        "    Example: -f *claudiol-dc1* \n" \
        " -h or --help \n" \
        "    Usage message"
    print(msg)
    exit()

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
            elif currentArgument in ("-f", "--filter"):
                print ("Adding filter: ", currentValue, " to search for OpenShift Namespaces")
                filter=currentValue
                break
            elif currentArgument in ("-a", "--all"):
                print ("Listing ALL OpenShift Namespaces")
                filter="ALL"
                break
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()

    instance = ns.Namespace(filter)
    instance.printList()
    
if __name__ == "__main__":
    main()


# Python imports
import sys
import getopt
import yaml

from validatedpattern import ValidatedPattern

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hf:"
# Long options
long_options = ["help", "file"]
            
def usage():
    msg = "Usage: python " + sys.argv[0] + "\n"  \
        "Options: \n" \
        " -f or --file \n" \
        "    File that contains ValidatePattern values. \n" \
        "    Example: -f values-datacenter.yaml \n" \
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
            elif currentArgument in ("-f", "--file"):
                print ("Reading Validated Pattern values file [", currentValue, "] ")
                file=currentValue
                break
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()

    pattern = ValidatedPattern(file)
    pattern.loadPatternValues()
    pattern.printSite()
    pattern.printSiteNameSpaces()
    pattern.printSiteSubscriptions()
    pattern.printSiteArgoProjects()
    pattern.printSiteArgoApplications()
    pattern.validateNameSpaces()
    list = pattern.validateOperators()

    for operator in list:
        print (operator[0], operator[1], operator[2]) 

    for operator in list:
      operatorName = operator[0]
      namespace = operator[1]
      if namespace == "none":
        pattern.deleteOperator(operatorName)
      else:
        pattern.deleteOperator(operatorName, namespace)

    nslist = pattern.getSiteNameSpaces()
    for namespace in nslist:
        pattern.deleteNamespace(namespace)

if __name__ == "__main__":
    main()

from kubernetes import client, config
from openshift.dynamic import DynamicClient

# Python imports
import sys
import getopt
import yaml

from yaml.loader import SafeLoader

import namespace as ns
from ocpoperator import Operators

class ValidatedPattern:
    def __init__(self, file):
        self.file = file
        self.data = []
        
    #
    # loadPatternValues
    # Loads the file that was passed in the ValidatedPattern class
    # instantiation.
    def loadPatternValues(self):
        with open(self.file, 'r') as f:
            self.data = list(yaml.load_all(f, Loader=SafeLoader))

    #
    # Prints the site configured in the ValidatePatterns values file
    #
    def printSite(self):
        site = self.data[0]['site']['name']
        print ("Pattern for: " + site)

    def getSite(self):
        site = self.data[0]['site']['name']
        return site

    #
    # Prints the site namespaces in the ValidatePatterns values file
    #            
    def printSiteNameSpaces(self):
        print ("Namespaces: ")
        namespaceList = self.data[0]['site']['namespaces']
        for namespace in namespaceList:
            print (namespace)

    def getSiteNameSpaces(self):
        namespaceList = self.data[0]['site']['namespaces']
        return namespaceList

    def printSiteSubscriptions(self):
        print("Site subscriptions: ")
        subscriptions = self.data[0]['site']['subscriptions']
        for sub in subscriptions:
            print ("Name: " + sub['name'] + " CSV: " + sub['csv'] + " Target Namespace: " + (sub['namespace'] if 'namespace' in sub else "none" ))

    def getSiteSubscriptions(self):
        subscriptions = self.data[0]['site']['subscriptions']
        return subscriptions
    
    def printSiteArgoProjects(self):
        print("ArgoCD Projects: ")
        projects = self.data[0]['site']['projects']

        for project in projects:
            print ("Name: " + project )

    def getSiteArgoProjects(self):
        projects = self.data[0]['site']['projects']
        return projects
    
    def printSiteArgoApplications(self):
        print("ArgoCD Applications: ")
        applications = self.data[0]['site']['applications']

        for application in applications:
            print ("Name: " + application['name'] )

    def getSiteArgoApplications(self):
        applications = self.data[0]['site']['applications']
        return applications

    def validateNameSpaces(self):
        list = []
        namespaceList = self.data[0]['site']['namespaces']

        instance = ns.Namespace()
        for namespace in namespaceList:
            validated = instance.validate(namespace)
            list.append ( (namespace, str(validated)) )
            #print ("Namespace [" + namespace + "] exists " + str(validated))
        return list
                          
    def validateOperators(self):
        list = []
        operator_instance = Operators()
        operator_list = operator_instance.getList()
        print (operator_list)
        operator_list = self.getSiteSubscriptions()
        for operator in operator_list:
            operatorName = operator['name'] 
            namespace = (operator['namespace'] if 'namespace' in operator else "none" )
            validated, namespace = operator_instance.validate(operatorName, namespace)
            list.append((operatorName, namespace, validated))
            #print ("Operator[" + operatorName + "] exists in namespace [" + namespace + "] ===>" + str(validated))
        return list

    def deleteNamespace(self, namespace):
        instance = ns.Namespace()
        instance.delete(namespace)

    def deleteOperator(self, operator, namespace=None):
        list = []
        operator_instance = Operators()
        if namespace == None:
            print ("Removing Operator[" + operator + "] in namespace [openshift-operators]" )
            operator_instance.delete(operator)
        else:
            print ("Removing Operator[" + operator + "] in namespace [" + namespace + "]" )
            operator_instance.delete(operator, namespace)
            #print ("Operator[" + operatorName + "] exists in namespace [" + namespace + "] ===>" + str(validated))

    def listOperatorCSV(self):
        list = []
        operator_instance = Operators()
        operator_instance.printCSV()


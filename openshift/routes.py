#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kubernetes import client, config
from openshift.dynamic import DynamicClient

# Python imports
import sys

class Routes:
    """
       Routes is a class that includes methods to list and manipulate OpenShift operators installed
       ...
       Attributes
       ----------
       TODO: Document Attributes

       Methods
       -------
       printList():
         Prints the list of running routes
    """
    def __init__(self, filter):
        # Initialize our variables
        self.api_version = 'v1'
        self.kind        = 'Route'
        self.k8s_client = config.new_client_from_config()
        self.dyn_client = DynamicClient(self.k8s_client)
        self.filter = filter
        
    def printListAllNamespaces(self):
        print ("Routes:")
        v1_routes = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        route_list = v1_routes.get()
        print (type(route_list ))
        for route in route_list.items:
            if self.filter == "ALL":
                print("Name: " + route.metadata.name + " Namespace: " + route.metadata.namespace)
            elif self.filter in route.metadata.name:
                print(route.metadata.name+ " Namespace: " + route.metadata.namespace)

    def printList(self):
        print ("Routes:")
        v1_route = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        route_list = v1_route.get()
        for route in route_list.items:
            if self.filter == "ALL":
                print("Name: " + route.metadata.name + " Route: " + route.spec.host)
            elif self.filter in route.metadata.namespace:
                print(route.metadata.name+ " Route: " + route.spec.host)

    def getRouteList(self, namespace="ALL"):
        #print ("Routes in Namespace [" + namespace + "]")
        ret_list=[]
        v1_routes = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        route_list = v1_routes.get()
        #print (type(route_list))
        for route in route_list.items:
            if namespace == "ALL":
                #print("Name: " + route.metadata.name + " Route: " + route.spec.host)
                ret_list.append(route)
            elif namespace in route.metadata.namespace:
                #print("Name: " + route.metadata.name + " Route: " + route.spec.host)
                ret_list.append(route)
        return ret_list
        

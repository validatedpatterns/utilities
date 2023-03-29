#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kubernetes import client, config
from openshift.dynamic import DynamicClient

# Python imports
import sys

class ArgoCDApplication:
    """
       ArgoCDApplication is a class that includes methods to list and manipulate ArgoCD Applications
       ...
       Attributes
       ----------
       TODO: Document Attributes

       Methods
       -------
       printList():
         Prints the list of applications in the Argocd instance
    """
    def __init__(self, filter):
        # Initialize our variables
        self.api_version = 'argoproj.io/v1alpha1'
        self.kind        = 'Application'
        self.k8s_client = config.new_client_from_config()
        self.dyn_client = DynamicClient(self.k8s_client)
        self.filter = filter
        
    def printList(self):
        print ("ArgoCD Applications:")
        v1_applications = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        application_list = v1_applications.get()
        for application in application_list.items:
            if self.filter == "ALL":
                print(application.metadata.name)
            elif self.filter in application.metadata.name:
                print(application.metadata.name)

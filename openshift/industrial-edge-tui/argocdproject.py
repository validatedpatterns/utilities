#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kubernetes import client, config
from openshift.dynamic import DynamicClient

# Python imports
import sys

class ArgoCDProject:
    """
       ArgoCDProject is a class that includes methods to list and manipulate ArgoCD Projects
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
        self.kind        = 'AppProject'
        self.k8s_client = config.new_client_from_config()
        self.dyn_client = DynamicClient(self.k8s_client)
        self.filter = filter
        
    def printList(self):
        print ("ArgoCD Projects:")
        v1_projects = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        project_list = v1_projects.get()
        for project in project_list.items:
            if self.filter == "ALL":
                print(project.metadata.name)
            elif self.filter in project.metadata.name:
                print(project.metadata.name)


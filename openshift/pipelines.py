#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kubernetes import client, config
from openshift.dynamic import DynamicClient

# Python imports
import sys

class Pipelines:
    """
       Pipelines is a class that includes methods to list and manipulate OpenShift Pipelines resources 
       ...
       Attributes
       ----------
       TODO: Document Attributes

       Methods
       -------
       printList():
         Prints the list of pipelines available
    """
    def __init__(self, filter="ALL"):
        # Initialize our variables
        apiVersion: v1
        self.api_version = 'tekton.dev/v1beta1'
        self.kind        = 'Pipeline'
        self.k8s_client = config.new_client_from_config()
        self.dyn_client = DynamicClient(self.k8s_client)
        self.filter = filter
        
    def printList(self):
        print ("Available Pipelines:")
        v1_pipelines = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        pipeline_list = v1_pipelines.get()
        for pipeline in pipeline_list.items:
            if self.filter == "ALL":
                print("Name: " + pipeline.metadata.name + " Namespace: " + pipeline.metadata.namespace)
            elif self.filter in pipeline.metadata.name:
                print(pipeline.metadata.name+ " Namespace: " + pipeline.metadata.namespace)

    def getList(self):
        list = []
        v1_pipelines = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        pipeline_list = v1_pipelines.get()
        for pipeline in pipeline_list.items:
            if self.filter == "ALL":
                list.append((pipeline.metadata.name, pipeline.metadata.namespace))
            elif self.filter in pipeline.metadata.namespace:
                list.append((pipeline.metadata.name, pipeline.metadata.namespace))
        return list

    def validate(self, namespace):
      pipeline_list = self.getList()
      for pipeline in pipeline_list:
          if ( (pipeline[1] == namespace) ):
              return True
      return False

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kubernetes import client, config, dynamic
from openshift.dynamic import DynamicClient
from kubernetes.client import api_client

# Python imports
import sys
import os

KUBE_CONFIG = os.getenv('KUBE_CONFIG_RHEV')

class Pods:
    """
       Pods is a class that includes methods to list and manipulate OpenShift operators installed
       ...
       Attributes
       ----------
       TODO: Document Attributes

       Methods
       -------
       printList():
         Prints the list of running pods
    """
    def __init__(self, filter):
        # Initialize our variables
        self.api_version = 'v1'
        self.kind        = 'Pod'
        self.k8s_client = config.new_client_from_config()
        self.dyn_client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.
                                 load_kube_config(KUBE_CONFIG)))
        self.filter = filter
        

    def printListAllNamespaces(self):
        print ("Running Pods:")
        v1_pods = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        pod_list = v1_pods.get()
        print (type(pod_list ))
        for pod in pod_list.items:
            if self.filter == "ALL":
                print("Name: " + pod.metadata.name + " Namespace: " + pod.metadata.namespace)
            elif self.filter in pod.metadata.name:
                print(pod.metadata.name+ " Namespace: " + pod.metadata.namespace)

    def printList(self):
        print ("Running Pods:")
        v1_pods = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        pod_list = v1_pods.get()
        for pod in pod_list.items:
            if self.filter == "ALL":
                print("Name: " + pod.metadata.name + " Namespace: " + pod.metadata.namespace)
            elif self.filter in pod.metadata.namespace:
                print(pod.metadata.name+ " Namespace: " + pod.metadata.namespace)

    def getPodList(self, namespace="ALL"):
        #print ("Running Pods in Namespace [" + namespace + "]")
        ret_list=[]
        v1_pods = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        pod_list = v1_pods.get()
        #print (type(pod_list))
        for pod in pod_list.items:
            if namespace == "ALL":
                #print("Name: " + pod.metadata.name + " Namespace: " + pod.metadata.namespace)
                ret_list.append(pod)
            elif namespace in pod.metadata.namespace:
                #print(pod.metadata.name+ " Namespace: " + pod.metadata.namespace)
                ret_list.append(pod)
        return ret_list

    def getPodLogs(self, podname, namespace):
        api = client.CoreV1Api()
        api_response = api.read_namespaced_pod_log(
                    name=podname, namespace=namespace)
        return api_response
        

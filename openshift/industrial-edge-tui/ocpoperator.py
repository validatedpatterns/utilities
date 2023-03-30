#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kubernetes import client, config
from openshift.dynamic import DynamicClient

# Python imports
import sys

class Operators:
    """
       Operators is a class that includes methods to list and manipulate OpenShift operators installed
       ...
       Attributes
       ----------
       TODO: Document Attributes

       Methods
       -------
       printList():
         Prints the list of installed operators 
    """
    def __init__(self, filter="ALL"):
        # Initialize our variables
        self.api_version = 'operators.coreos.com/v1alpha1'
        self.kind        = 'Subscription'
        self.csvkind        = 'ClusterServiceVersion'
        self.k8s_client = config.new_client_from_config()
        self.dyn_client = DynamicClient(self.k8s_client)
        self.filter = filter
        
    def printCSV(self):
        print ("Installed CSVs:")
        v1_csvs = self.dyn_client.resources.get(api_version=self.api_version, kind=self.csvkind)
        csv_list = v1_csvs.get()
        for csv in csv_list.items:
            if self.filter == "ALL":
                print("Name: " + csv.metadata.name + " Namespace: " + csv.metadata.namespace)
            elif self.filter in csv.metadata.name:
                print(csv.metadata.name + " Namespace: " + csv.metadata.namespace)

    def printList(self):
        print ("Installed Operators:")
        v1_subscriptions = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        subscription_list = v1_subscriptions.get()
        print (subscription_list)
        for subscription in subscription_list.items:
            if self.filter == "ALL":
                print("Name: " + subscription.metadata.name + " Namespace: " + subscription.metadata.namespace)
            elif self.filter in subscription.metadata.name:
                print(subscription.metadata.name+ " Namespace: " + subscription.metadata.namespace)

    def getCSVList(self, operator, namespace):
        print ("Installed CSVs:")
        v1_csvs = self.dyn_client.resources.get(api_version=self.api_version, kind=self.csvkind)
        csv_list = v1_csvs.get()
        list=[]
        for csv in csv_list.items:
            if (csv.metadata.name == operator) and (csv.metadata.namespace == namespace): 
                print("Name: " + csv.metadata.name + " Namespace: " + csv.metadata.namespace)
                list.append((csv.metadata.name, csv.metadata.namespace))
                return list
        return list

    def delete(self, name, namespace=None):
        try:
            print ("Delete Operator")
            v1_subscriptions = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
            v1_csv = self.dyn_client.resources.get(api_version=self.api_version, kind=self.csvkind)
            subscription_list = v1_subscriptions.get()
            csv_list = self.getCSVList(name, namespace)
            if namespace == None:
                namespace = 'openshift_operators'
                v1_subscriptions.delete(name=name, namespace=namespace)
                
            for csv in csv_list:
                v1_csv.delete(name=csv[0], namespace=csv[1])
        except:
            pass
        
    def getList(self):
        list = []
        v1_subscriptions = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        subscription_list = v1_subscriptions.get()
        #print(subscription_list)
        for subscription in subscription_list.items:
            #print(subscription.metadata)
            if self.filter == "ALL":
                list.append((subscription.metadata.name, subscription.metadata.namespace))
            elif self.filter in subscription.metadata.name:
                list.append((subscription.metadata.name, subscription.metadata.namespace))
        return list

    def validate(self, name, namespace):
      subscription_list = self.getList()
      for subscription in subscription_list:
          if namespace == 'none':
            if ( subscription[0] == name  ):
              return True, namespace
          elif ( (subscription[0] == name) and (subscription[1] == namespace) ):
              return True, namespace
      return False, namespace

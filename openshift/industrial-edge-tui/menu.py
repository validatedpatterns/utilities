#!/usr/bin/env python3

# Python imports
import curses
import sys
import os
import time

from kubernetes import client, config
from openshift.dynamic import DynamicClient

import namespace as ns
import pod as nspod
import validatedpattern as vp
import pipelines as pipe
import routes as myroutes

from cursesmenu import CursesMenu
import npyscreen

# Define functions


def validatePods():
    # Create a Form
    form = npyscreen.Form(name = "OpenShift POD Search",)
    # Add a entry widget
    filter = form.add(npyscreen.TitleText, name = "Enter namespace to search [ALL for all namespaces]: ")
    # Go ahead and get user input
    form.edit()
    # Create a Namespace instance and pass the filter value.
    if not filter.value:
        instance = nspod.Pods("ALL")
        # Get the list from OpenShift 
        pods=instance.getPodList(filter.value)
    else:
        instance = nspod.Pods(filter.value)
        # Get the list from OpenShift 
        pods=instance.getPodList(filter.value)

    # Create a Form to display results
    F = npyscreen.Form(name = "Validated Patterns App",)
    messages = []

    if len(pods) == 0:
        messages.append(("No pods found in namespace", filter.value))
    else:
        for item in pods:
            messages.append((item.metadata.name,item.status.phase))
    t2 = F.add(npyscreen.GridColTitles,
               name="OpenShift Pods Found:",
               #col_width=60,
               values=messages,
               col_titles=['Pod Name', 'State'])         
    t2.values = messages  
    F.edit()

#
# displayPods - displays Pods in a specified OpenShift Namespaces
# 

def displayRoutes():
    # Create a Form
    form = npyscreen.Form(name = "OpenShift Route Search",)
    # Add a entry widget
    filter = form.add(npyscreen.TitleText, name = "Enter namespace to search [ALL for all namespaces]: ")
    # Go ahead and get user input
    form.edit()
    # Create a Namespace instance and pass the filter value.
    #print (filter.value)
    if not filter.value:
        instance = myroutes.Routes("ALL")
        # Get the list from OpenShift 
        routesList=instance.getRouteList(filter.value)
    else:
        instance = myroutes.Routes(filter.value)
        # Get the list from OpenShift 
        routesList=instance.getRouteList(filter.value)

    # Create a Form to display results
    F = npyscreen.Form(name = "Validated Patterns Routes in Namespace [" + filter.value + "]",)
    messages = []

    if len(routesList) == 0:
        messages.append(("No routes found in namespace", filter.value))
    else:
        for item in routesList:
            if 'host' in item.spec:
              messages.append((item.metadata.name,item.spec.host))
            else:
              messages.append((item.metadata.name,item.status.ingress[0].host))
              
        t2 = F.add(npyscreen.GridColTitles,
             name="OpenShift Routes Found in [" + filter.value + "]",
             col_width=10,
             values=messages,
             col_titles=['Route Name', 'Route'])         
    #t2.values = messages  
    F.edit()

def displayPods():
    # Create a Form
    form = npyscreen.Form(name = "OpenShift POD Search",)
    # Add a entry widget
    filter = form.add(npyscreen.TitleText, name = "Enter namespace to search [ALL for all namespaces]: ")
    # Go ahead and get user input
    form.edit()
    # Create a Namespace instance and pass the filter value.
    if not filter.value:
        instance = nspod.Pods("ALL")
        # Get the list from OpenShift 
        pods=instance.getPodList(filter.value)
    else:
        instance = nspod.Pods(filter.value)
        # Get the list from OpenShift 
        pods=instance.getPodList(filter.value)

    # Create a Form to display results
    F = npyscreen.Form(name = "Validated Patterns PODS in Namespace [" + filter.value + "]",)
    messages = []

    if len(pods) == 0:
        messages.append(("No pods found in namespace", filter.value))
    else:
        for item in pods:
            messages.append((item.metadata.name,item.status.phase))
    t2 = F.add(npyscreen.GridColTitles,
               name="OpenShift Pods Found in [" + filter.value + "]",
               #col_width=60,
               values=messages,
               col_titles=['Pod Name', 'State'])         
    t2.values = messages  
    F.edit()

#
# displayNameSpaces - gets OpenShift Namespaces
# 
def displayNameSpaces() :
    # Create a Form
    form = npyscreen.Form(name = "OpenShift Namespace Search",)
    # Add a entry widget
    filter = form.add(npyscreen.TitleText, name = "Enter namespace filter: ")
    # Go ahead and get user input
    form.edit()
    # Create a Namespace instance and pass the filter value.
    instance = ns.Namespace(filter.value)
    # Get the list from OpenShift 
    namespaces=instance.getList()

    # Create a Form to display results
    F = npyscreen.Form(name = "Validated Patterns App",)
    t2 = F.add(npyscreen.BoxTitle, name="OpenShift Namespaces Found:", max_height=20)         
    t2.entry_widget.scroll_exit = True
    if not namespaces:
        message = "No namespaces found that contain [" + filter.value + "]"
        messages = []
        messages.append(message)
        t2.values = messages
    else:
        t2.values = namespaces 
    F.edit()

#
# validateDataCenterNameSpaces - validate OpenShift Namespaces found in values-datacenter.yaml file
# 

def validateDataCenterNameSpaces():
    # Create a Form
    form = npyscreen.Form(name = "Validated Patterns OpenShift Datacenter Namespace Validation",)
    # Add a entry widget
    filter = form.add(npyscreen.TitleText, name = "Enter file name (e.g. /home/claudiol/values-datacenter.yaml) values file to validate: ")
    # Go ahead and get user input
    form.edit()
    # Create a Namespace instance and pass the filter value.
    if filter.value:
        instance = vp.ValidatedPattern(filter.value)
        instance.loadPatternValues()
        # Get the list from OpenShift 
        validated_list=instance.validateNameSpaces()

    # Create a Form to display results
    F = npyscreen.Form(name = "Validated Patterns Datacenter Namespace Validation",)
    messages = []

    if len(validated_list) == 0:
        messages.append(("No namespaces found to validate in file: ", filter.value))
    else:
        for item in validated_list:
            messages.append((item[0],item[1]))
    t2 = F.add(npyscreen.GridColTitles,
               name="OpenShift Namespacess Validated in [" + filter.value + "]",
               #col_width=60,
               values=messages,
               col_titles=['Namespace', 'Validated Status'])         
    t2.values = messages  
    F.edit()

#
# validateOperators - validate OpenShift Operators listed in values-datacenter.yaml file
# 

def validateDataCenterOperators():
    # Create a Form
    form = npyscreen.Form(name = "Validated Patterns OpenShift Datacenter Installed Operators Validation",)
    # Add a entry widget
    filter = form.add(npyscreen.TitleText, name = "Enter file name (e.g. /home/claudiol/values-datacenter.yaml) values file to validate: ")
    # Go ahead and get user input
    form.edit()
    # Create a Namespace instance and pass the filter value.
    if filter.value:
        instance = vp.ValidatedPattern(filter.value)
        instance.loadPatternValues()
        # Get the list from OpenShift 
        validated_list=instance.validateOperators()

    # Create a Form to display results
    F = npyscreen.Form(name = "Validated Patterns Datacenter Installed Operator Validation",)
    messages = []

    if len(validated_list) == 0:
        messages.append(("No operators found to validate in file: ", filter.value))
    else:
        for item in validated_list:
            messages.append((item[0], item[1], item[2]))
    t2 = F.add(npyscreen.GridColTitles,
               name="OpenShift Operators Validated in [" + filter.value + "]",
               #col_width=60,
               values=messages,
               col_titles=['Operator', 'Namespace', 'Validated Status'])         
    t2.values = messages  
    F.edit()

def displayPipelines():
    # Create a Form
    form = npyscreen.Form(name = "Validated Patterns Available Pipelines",)
    # Add a entry widget
    filter = form.add(npyscreen.TitleText, name = "Enter namespace to look for pipelines: ")
    # Go ahead and get user input
    form.edit()
    # Create a Namespace instance and pass the filter value.
    if filter.value:
        instance = pipe.Pipelines(filter.value) 
        # Get the list from OpenShift 
        pipeline_list=instance.getList()

    # Create a Form to display results
    F = npyscreen.Form(name = "Validated Patterns Industrial Edge Pipelines",)
    messages = []

    if len(pipeline_list) == 0:
        messages.append(("No pipelines found in namespace: ", filter.value))
    else:
        for item in pipeline_list:
            messages.append((item[0], item[1]))
    t2 = F.add(npyscreen.GridColTitles,
               name="OpenShift Pipelines found in [" + filter.value + "]",
               #col_width=60,
               values=messages,
               col_titles=['Pipeline Name', 'Namespace'])         
    t2.values = messages  
    F.edit()



def main():
    try:
        kubeconfig = os.environ['KUBECONFIG']

        if not kubeconfig:
            raise Exception("KUBECONFIG environment variable not set. Please export KUBECONFIG=[kubeconfig file]")
        
        message = "Using kubeconfig [" + kubeconfig + "]"
        menu = {'title' : 'Validated Pattern Menu',
                'type' : 'menu',
                'subtitle' : message
                }

        option_1 = {'title' : 'Display Openshift Namespaces',
                    'type' : 'namespaces'
                    }
        
        option_2 = {'title' : 'Display Openshift Pods',
                    'type' : 'pods'
                    }

        option_3 = {'title' : 'Validate Datacenter Namespaces',
                    'type' : 'dc-namespaces'
                    }

        option_4 = {'title' : 'Validate Datacenter Operators',
                    'type' : 'dc-operators'
                    }

        option_5 = {'title' : 'Validate Datacenter Pipelines',
                    'type' : 'dc-pipelines'
                    }

        option_6 = {'title' : 'Validate Datacenter Routes',
                    'type' : 'dc-routes'
                    }

        menu['options'] = [option_1, option_2, option_3, option_4, option_5, option_6]

        m = CursesMenu(menu)
        
        while True:
            selected_action = m.display()
            
            if selected_action['type'] == 'exitmenu':
                break
            elif selected_action['type'] == 'namespaces':
                displayNameSpaces()
            elif selected_action['type'] == 'pods':
                displayPods()
            elif selected_action['type'] == 'dc-namespaces':
                validateDataCenterNameSpaces()
            elif selected_action['type'] == 'dc-operators':
                validateDataCenterOperators()
            elif selected_action['type'] == 'dc-pipelines':
                displayPipelines()
            elif selected_action['type'] == 'dc-routes':
                displayRoutes()
    except Exception as err:
        if "KUBECONFIG" in str(err):
            print ("KUBECONFIG environment variable not set. Please export KUBECONFIG=[kubeconfig file]")
        else:
            # output error, and return with an error code
            print ("Exception: " + str(err))


if __name__ == "__main__":
    main()

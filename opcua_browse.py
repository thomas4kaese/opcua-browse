#!/usr/bin/env python

import sys
sys.path.insert(0, "..")
import re
import csv
from opcua import Client

# SETTINGS


# Lapis 2
conn_str = 'opc.tcp://USERNAME:PASSWORD@IPADDRESS:PORT/'


# 0 = check for devices, 1 = browse object, 2 = browse root, 3 = custom node nodeID
device_mode = 1
custom_nodeID = "ns=3;s=BuildingAutomation"# example for a B-und-R OPC UA Server

var_s = []
types = []
index = []
names = []
nodenumbers = []
var_i = 0


def get_node_ID(node):
	nodeID = re.findall("NodeId\((.+?)\)", str(node))
	return nodeID;

# input: nodenodeID or list of node nodeIDs
# returns name(s) of nodenodeID(s)
def get_node_name(nodeID):
	name_list = []
	if not isinstance(nodeID, str):
		for i in range(0, len(nodeID)):
			node = client.get_node(str(nodeID[i]))
			node_name = node.get_browse_name()
			split_name = re.search("\:(.+?)\)", str(node_name)).group(0)[1:-1]
			name_list.append(split_name)
	else:
		print(nodeID)
		node = client.get_node(str(nodeID))
		node_name = nodeID.get_browse_name()
		name_list = re.search("\:(.+?)\)", str(node_name)).group(0)[1:-1]
	# print name_list
	return name_list

# input: nodenodeID or list of node nodeIDs
# returns list of children as nodeIDs
def get_children(nodeID):
	children_nodeIDs = []
	if not isinstance(nodeID, str):
		for i in range(0, len(nodeID)):
			nodeID = client.get_node(str(nodeID[i]))
			children = nodeID.get_children()
			split_name = re.findall("NodeId\((.+?)\)", str(children))
			print(split_name)
			children_nodeIDs.append(split_name)
	else:
		nodeID = client.get_node(str(nodeID))
		children = nodeID.get_children()
		children_nodeIDs = re.findall("NodeId\((.+?)\)", str(children))
	print("Kinder: " + str(children_nodeIDs))
	return children_nodeIDs


def browse_children(evalNode):
	current_node = client.get_node(evalNode)

	# Klasse des aufgerufenen Knotens pruefen
	currentNode_class = current_node.get_node_class()
	
	print("Pruefen von Node: " + evalNode + " , Klasse: " + str(currentNode_class))
		
	if str(currentNode_class) == "NodeClass.Variable":
		try:
			node_type = client.get_node(evalNode).get_data_value()
			node_type = re.search("Type\.(.+?)\)", str(node_type)).group(0)[5:-1]
			node_name = client.get_node(evalNode).get_display_name()# evtl auf browse name umsatteln
			node_name = re.search("Text\:(.+?)\)", str(node_name)).group(0)[5:-1]
			add_line(evalNode, node_name, node_type)
		except:
			node_type = "CORRUPTED ITEM"
		
	# Knotennummern der Kinder des aktuellen Knotens auslesen
	loop_children = get_children(evalNode)
	for item in loop_children:	
		print("Aufruf von Item: " + item)
		browse_children(item) # alle Knoten rekursiv aufrufen
					

def add_line(item, node_name, node_type):
	global var_i
	global var_s
	global types
	global names
	var_i = var_i + 1
	index.append(var_i)
	names.append(node_name)	
	var_s.append(item)
	types.append(node_type)	


if __name__ == "__main__":
		
	# client.set_security(None)
	client = Client(conn_str)
	client.connect()

	client.load_type_definitions(nodes=None)
	
	root = client.get_root_node()
	print('root: ' + str(root))
	root_nodeID = get_node_ID(root)
	print('root_nodeID: ' + str(root_nodeID))
	
	objects = client.get_objects_node()
	print('objects: ' + str(objects))
	object_nodeID = get_node_ID(objects)
	print('object_nodeID: ' + str(object_nodeID))
	
	# find DeviceSets and get name(s) of PLC instances
	object_childs = objects.get_children()
	print('object_childs: ' + str(object_childs))
	object_childs_nodeID = get_node_ID(object_childs)
	print('object_childs_nodeID: ' + str(object_childs_nodeID))
	object_child_names = get_node_name(object_childs_nodeID)
	print('object_child_names: ' + str(object_child_names))
	
	device_mode = 1
	
	if device_mode == 0:
		try:
			deviceset_nodenodeID = object_childs_nodeID[object_child_names.index("DeviceSet")]
			devices = get_children(deviceset_nodenodeID)
			device_names = get_node_name(devices)
			# print("Device(s) is/are ", device_names, "with DEVICE NodenodeID(s)", devices)
		
			object_device_nodenodeID = []
			for i in range(0, len(device_names)):
				object_device_nodenodeID.append(object_childs_nodeID[object_child_names.index(device_names[i])])
				print("Device(s) is/are ", device_names, "with NodenodeID(s)", object_device_nodenodeID)
			
			# browse objects and search for variables
			for i in range(0, len(object_device_nodenodeID)):
				objects = object_device_nodenodeID[0]
		except:
			print("DeviceSet is not in List, please try other setting for DeviceMode")
		
	elif device_mode == 1:
		objects = object_nodeID[0]
	elif device_mode == 2:
		objects = root_nodeID[0]
	else:
		objects = custom_nodeID

	browse_children(objects)
	for index_i in index:
		print(index[index_i-1], names[index_i-1], var_s[index_i-1], types[index_i-1])
	print("collected items: ", var_i)
		
	# build and write csv
	rows = zip(index, names, var_s, types)
	
	with open('output.csv', "w" , newline='') as f:
		writer = csv.writer(f)
		for row in rows:
			writer.writerow(row)
		print("Output complete: output.csv")
		
	client.disconnect()

import os
import sys

# Ensure SUMO_HOME is set and add the tools folder to the Python path
if "SUMO_HOME" not in os.environ:
    os.environ["SUMO_HOME"] = "/usr/share/sumo"
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import sumolib

def inspect_junction():
    net_path = os.path.join(os.path.dirname(__file__), '..', 'envs', 'katubedda.net.xml')
    
    print(f"Loading network: {net_path}")
    net = sumolib.net.readNet(net_path)
    
    node_id = "cluster_1278003886_50422936"
    
    try:
        node = net.getNode(node_id)
        
        print("\n========================================")
        print(f"VALID EDGES FOR JUNCTION: {node_id}")
        print("========================================")
        
        print("\n[INCOMING EDGES] (Traffic driving TOWARDS the traffic light)")
        for edge in node.getIncoming():
            print(f"  - {edge.getID()}")
            
        print("\n[OUTGOING EDGES] (Traffic driving AWAY from the traffic light)")
        for edge in node.getOutgoing():
            print(f"  - {edge.getID()}")
            
        print("========================================\n")
        
    except KeyError:
        print(f"Error: Node {node_id} not found in the network!")

if __name__ == "__main__":
    inspect_junction()
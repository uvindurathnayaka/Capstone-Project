import os
import random

SIM_STEPS = 3600

PROB_GALLE_ROAD = 2400 / 3600 
PROB_CAMPUS_ROAD = 600 / 3600  

SPLIT = {
    "car": 0.532,           
    "three_wheeler": 0.748, 
    "motorcycle": 0.867,    
    "bus": 0.958,           
    "truck": 1.000          
}

# UPDATED: north_out is now 112446377.41 due to the J8 bus merge node
EDGES = {
    "north_in": "51133939#0",    "north_out": "112446377.41",
    "south_in": "112446386#0",   "south_out": "51133939#1",
    "campus_in": "159380574#0",  "campus_out": "-487435376#1"
}

def get_vehicle_type():
    rand = random.random()
    if rand <= SPLIT["car"]: return "car"
    if rand <= SPLIT["three_wheeler"]: return "three_wheeler"
    if rand <= SPLIT["motorcycle"]: return "motorcycle"
    if rand <= SPLIT["bus"]: return "bus"
    return "truck"

def generate_katubedda_routes(filename):
    with open(filename, "w") as routes:
        print("""<routes>
        <vType id="car" vClass="passenger" accel="2.6" decel="4.5" length="4.5" minGap="2.0" maxSpeed="15" guiShape="passenger"/>
        <vType id="three_wheeler" vClass="passenger" accel="3.5" decel="5.0" length="2.5" width="1.3" minGap="1.0" maxSpeed="12" guiShape="passenger/hatchback" color="0,1,0"/>
        <vType id="motorcycle" vClass="motorcycle" accel="4.0" decel="6.0" length="2.0" width="0.8" minGap="0.5" maxSpeed="15" guiShape="motorcycle" color="0,0,1"/>
        <vType id="bus" vClass="bus" accel="1.2" decel="3.0" length="10.0" minGap="3.0" maxSpeed="12" guiShape="bus" color="1,0,0"/>
        <vType id="truck" vClass="truck" accel="1.0" decel="2.5" length="8.0" minGap="3.0" maxSpeed="10" guiShape="truck" color="1,1,0"/>
        """, file=routes)

        edges_in = [EDGES["north_in"], EDGES["south_in"], EDGES["campus_in"]]

        for step in range(SIM_STEPS):
            for in_edge in edges_in:
                prob = PROB_GALLE_ROAD if in_edge in [EDGES["north_in"], EDGES["south_in"]] else PROB_CAMPUS_ROAD
                
                if random.random() < prob:
                    if in_edge == EDGES["south_in"]:
                        out_edge = EDGES["north_out"] if random.random() < 0.8 else EDGES["campus_out"]
                    elif in_edge == EDGES["north_in"]:
                        out_edge = EDGES["south_out"] if random.random() < 0.8 else EDGES["campus_out"]
                    elif in_edge == EDGES["campus_in"]:
                        out_edge = EDGES["north_out"] if random.random() < 0.5 else EDGES["south_out"]
                        
                    v_type = get_vehicle_type()
                    
                    print(f'    <trip id="veh_{step}_{in_edge}" type="{v_type}" depart="{step}" from="{in_edge}" to="{out_edge}"/>', file=routes)

        print("</routes>", file=routes)

if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), '..', 'envs', 'katubedda.rou.xml')
    generate_katubedda_routes(filepath)
    print(f"Katubedda traffic generated at {filepath}")
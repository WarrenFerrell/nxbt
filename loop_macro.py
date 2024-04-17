import time
import sys
 
from random import randint

import nxbt
from nxbt import Buttons
from nxbt import Sticks


RETURN_TO_GAME_MACRO = """
0.25s
LOOP 2
    B 0.1s
    0.25s
0.5s
HOME 0.1s
0.5s
"""


def random_colour():

    return [
        randint(0, 255),
        randint(0, 255),
        randint(0, 255),
    ]

def dumpclean(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                dumpclean(v)
            else:
                print('%s : %s' % (k, v))
    elif isinstance(obj, list):
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print(v)
    else:
        print(obj)

if __name__ == "__main__":

    # Init NXBT
    nx = nxbt.Nxbt()

    # Get a list of all available Bluetooth adapters
    adapters = nx.get_available_adapters()
    # Prepare a list to store the indexes of the
    # created controllers.
    controller_idxs = []
    # Loop over all Bluetooth adapters and create
    # Switch Pro Controllers
    reconnect_address = "D0:55:09:B1:FF:5D"
    for i in range(0, len(adapters)):
        index = nx.create_controller(
            nxbt.PRO_CONTROLLER,
            adapter_path=adapters[i],
            colour_body=random_colour(),
            colour_buttons=random_colour()
            ,reconnect_address=reconnect_address
            )
        controller_idxs.append(index)

    # Select the last controller for input
    controller_idx = controller_idxs[-1]

    # Wait for the switch to connect to the controller
    print("Waiting to Connect (Go to Change grip Order if not already there)")
    nx.wait_for_connection(controller_idx)
    print("Connected, returning to game")
    dumpclean(nx.state[controller_idx])
    time.sleep(0.5)
    
    macro_id = nx.macro(controller_idx, RETURN_TO_GAME_MACRO)

    i = 0
    controller = nx.state[controller_idx]
    while True:
        file = open("/vagrant/ace_tourney.txt", "r")
        macro = file.read()
        print("Starting Macro... ", end='', flush=True )
        
        macro_id = nx.macro(controller_idx, macro, block=False)
        while macro_id not in nx.state[controller_idx]["finished_macros"]: 
            if i % 500 == 0:
                print("still running... ", end='', flush=True)
            #     dumpclean(nx.state[controller_idx])

            if controller["state"] not in ["connected", "reconnecting", "connecting"]:
                print("error detected... ")
                dumpclean(nx.state[controller_idx])
                raise OSError("Blocked macro is no longer connected, error:", controller["errors"])
            time.sleep(0.01)
            i += 1
        print("Macro has finished")

    print("Exiting...")

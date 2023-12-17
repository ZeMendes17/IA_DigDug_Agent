"""Example client."""
import asyncio
import getpass
import json
import os

# Next 4 lines are not needed for AI agents, please remove them from your code!
import websockets

from agent import Agent
import time




async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        # Next 3 lines are not needed for AI agent
        # SCREEN = pygame.display.set_mode((299, 123))
        # SPRITES = pygame.image.load("data/pad.png").convert_alpha()
        # SCREEN.blit(SPRITES, (0, 0))

        # create an instance of the agent
        agent = Agent()
        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                key = ""

                ## AI agent logic ##

                # calculate the time it takes to update the state
                # start = round(time.time() * 1000)
                # update the state --> returns the key to be pressed
                key = agent.update_state(state)
                # end = round(time.time() * 1000)
                # print("Time: ", end - start)

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

            # Next line is not needed for AI agent
            # pygame.display.flip()


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))

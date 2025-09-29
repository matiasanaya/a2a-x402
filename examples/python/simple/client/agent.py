from google.adk import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH

from .remote_a2a_agent import RemoteA2aAgent

remote_echo_agent = RemoteA2aAgent(
    name="remote_echo_agent",
    agent_card=f"http://localhost:10000/agents/merchant_agent{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = Agent(
    model="gemini-2.0-flash",
    name="delegator",
    description="Delegator that's connected to sub agents",
    instruction="When users ask for anything, delegate to a sub agent and report the result back to the user.",
    sub_agents=[remote_echo_agent],
)

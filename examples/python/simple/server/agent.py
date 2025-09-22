from a2a.types import AgentSkill
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from x402_a2a.core.agent import create_x402_agent_card
from x402_a2a.core.helpers import require_payment

agent_card = create_x402_agent_card(
    name="Echo Agent",
    description="This agent can echo back your requests.",
    url="http://localhost:10000",
    version="0.0.1",
    streaming=False,
    skills=[
        AgentSkill(
            id="echo_skill",
            name="Echo Skill",
            description="This skill echoes back your requests.",
            tags=["echo"],
            examples=[
                "What's the meaning of life?",
                "Prove the Collatz Conjecture.",
                "How are you doing today?",
            ],
        )
    ],
)


def before_agent_callback(callback_context: CallbackContext):
    if callback_context.state.get("x402_payment_verified", False):
        callback_context.state["x402_payment_verified"] = False
        return None

    raise require_payment(
        price="$0.001",
        pay_to_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        network="base-sepolia",
        description="Payment for this request",
        message="Payment required for request",
    )


def get_short_uuid(tool_context: ToolContext) -> str:
    return "6f5a38b1-d483-469e-96a0-00330063c25b"


root_agent = Agent(
    name="echo_agent",
    model="gemini-2.0-flash",
    description="An agent that echoes back requests",
    instruction="You are an agent that echoes back requests and adds a new short uuid request ID (use the tool for this) to each response in the format '<random_id>: <request>'. If the request contains multiple parts, just echo back part[0]",
    before_agent_callback=before_agent_callback,
    tools=[get_short_uuid],
)

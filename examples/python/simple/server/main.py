import uvicorn
import logging

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from starlette.applications import Starlette

from .agent import root_agent, agent_card
from .a2a_executor import OuterA2aAgentExecutor, InnerA2aAgentExecutor
from .x402_seller_executor import x402SellerExecutor


def main():
    agent = root_agent

    runner = Runner(
        app_name="simple_agent_app",
        agent=agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

    agent_executor = InnerA2aAgentExecutor(runner=runner)
    agent_executor = x402SellerExecutor(delegate=agent_executor)
    agent_executor = OuterA2aAgentExecutor(agent_executor)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    app = Starlette(
        routes=a2a_app.routes(
            agent_card_url="/agents/merchant_agent/.well-known/agent-card.json"
        )
    )

    logging.basicConfig(level=logging.ERROR)
    uvicorn.run(app, host="127.0.0.1", port=10000)


if __name__ == "__main__":
    main()

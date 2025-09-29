import uuid

from datetime import datetime
from datetime import timezone
from typing import override
from venv import logger

from a2a.types import Message
from a2a.types import Part
from a2a.types import Role
from a2a.types import TaskStatusUpdateEvent
from a2a.types import TextPart
from x402_a2a.types import AgentExecutor
from x402_a2a.types import EventQueue
from x402_a2a.types import TaskState
from x402_a2a.types import TaskStatus
from x402_a2a.types import RequestContext

from .a2a_monkey import MonkeyA2aAgentExecutor


class OuterA2aAgentExecutor(AgentExecutor):
    def __init__(
        self,
        delegate: AgentExecutor,
    ):
        super().__init__()
        self._delegate = delegate

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        return await self._delegate.cancel(context, event_queue)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        if not context.message:
            raise ValueError("A2A request must have a message")

        assert context.task_id, "A2A request must have a task ID"
        assert context.context_id, "A2A request must have a context ID"

        # for new task, create a task submitted event
        if not context.current_task:
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    status=TaskStatus(
                        state=TaskState.submitted,
                        message=context.message,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    ),
                    context_id=context.context_id,
                    final=False,
                )
            )
        try:
            await self._delegate.execute(context, event_queue)
        except Exception as e:
            logger.error("Error handling A2A request: %s", e, exc_info=True)
            # Publish failure event
            try:
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        task_id=context.task_id,
                        status=TaskStatus(
                            state=TaskState.failed,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            message=Message(
                                message_id=str(uuid.uuid4()),
                                role=Role.agent,
                                parts=[Part(TextPart(text=str(e)))],
                            ),
                        ),
                        context_id=context.context_id,
                        final=True,
                    )
                )
            except Exception as enqueue_error:
                logger.error(
                    "Failed to publish failure event: %s", enqueue_error, exc_info=True
                )


class InnerA2aAgentExecutor(MonkeyA2aAgentExecutor):
    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        await self._handle_request(context, event_queue)

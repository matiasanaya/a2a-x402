from typing import override
# from pprint import pformat

from a2a.client import ClientEvent as A2AClientEvent
from a2a.types import Message as A2AMessage
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent as BaseRemoteA2aAgent
from google.adk.events.event import Event
from x402_a2a import PaymentPayload
from x402_a2a.core.utils import create_payment_submission_message
from x402_a2a.core.utils import x402Utils
from x402_a2a.types import PaymentStatus
from x402.types import ExactPaymentPayload
from x402.types import EIP3009Authorization


class RemoteA2aAgent(BaseRemoteA2aAgent):
    @override
    async def _handle_a2a_response(
        self, a2a_response: A2AClientEvent | A2AMessage, ctx: InvocationContext
    ) -> Event:
        try:
            # print(f"### [x402-ma] Initial a2a_response:\n{pformat(a2a_response)}")
            status = None
            if isinstance(a2a_response, tuple):
                task = a2a_response[0]

                status = x402Utils().get_payment_status(task)

                if status == PaymentStatus.PAYMENT_REQUIRED:
                    payment_requirements = x402Utils().get_payment_requirements(task)
                    # print(f"### [x402-ma] Payment Required: {payment_requirements}")
                    if payment_requirements:
                        message = create_payment_submission_message(
                            task_id=task.id,
                            payment_payload=PaymentPayload(
                                x402_version=1,
                                scheme="exact",
                                network="base-sepolia",
                                payload=ExactPaymentPayload(
                                    signature="fake",
                                    authorization=EIP3009Authorization(
                                        **{
                                            "from": payment_requirements.accepts[
                                                0
                                            ].pay_to,
                                            "to": payment_requirements.accepts[
                                                0
                                            ].pay_to,
                                            "value": payment_requirements.accepts[
                                                0
                                            ].max_amount_required,
                                            "valid_after": "0",
                                            "valid_before": "9999999999999999999999",
                                            "nonce": "9jc903j903j9cj349034j",
                                        }
                                    ),
                                ),
                            ),
                        )
                        message.context_id = task.context_id
                        await self._ensure_resolved()
                        if self._a2a_client:
                            # print(
                            #     f"### [x402-ma] Payment Submitted message:\n{pformat(message.model_dump_json())}"
                            # )
                            responses = []
                            resp = self._a2a_client.send_message(request=message)
                            while True:
                                try:
                                    responses.append(await anext(resp))
                                except StopAsyncIteration:
                                    break

                            # Update a2a_response with the last payment response if we got any
                            if responses:
                                # print(
                                #     f"### [x402-ma] Payment submission response last:\n{pformat(responses[-1])}"
                                # )
                                a2a_response = responses[-1]
            # Otherwise, it's a regular A2AMessage.
            elif isinstance(a2a_response, A2AMessage):
                status = x402Utils().get_payment_status_from_message(a2a_response)
                if status == PaymentStatus.PAYMENT_REQUIRED:
                    raise NotImplementedError(
                        "Payment required in A2AMessage not handled yet."
                    )
        except Exception as e:
            print(f"Failed to create payment submission: {e}")

        # print(f"### [x402-ma] Final a2a_response:\n{pformat(a2a_response)}")
        return await super()._handle_a2a_response(a2a_response, ctx)

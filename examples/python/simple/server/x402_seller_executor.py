from typing import override

from a2a.server.agent_execution import AgentExecutor
from x402_a2a import x402ExtensionConfig
from x402_a2a.executors import x402ServerExecutor
from x402_a2a.types import (
    PaymentPayload,
    PaymentRequirements,
    SettleResponse,
    VerifyResponse,
)


class x402SellerExecutor(x402ServerExecutor):
    def __init__(
        self,
        delegate: AgentExecutor,
    ):
        super().__init__(delegate, x402ExtensionConfig())

    @override
    async def verify_payment(
        self, payload: PaymentPayload, requirements: PaymentRequirements
    ) -> VerifyResponse:
        print("✅ Payment Verified! (Not Really)")
        return VerifyResponse(
            isValid=True,
            payer="0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            invalidReason=None,
        )

    @override
    async def settle_payment(
        self, payload: PaymentPayload, requirements: PaymentRequirements
    ) -> SettleResponse:
        print("✅ Payment Settled! (Not Really)")
        return SettleResponse(success=True, network="mock-network")

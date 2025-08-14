from dataclasses import dataclass

@dataclass
class CostModel:
    fee_bps: float = 0.5
    slippage_bps: float = 1.0

    def apply(self, price: float, qty: int) -> float:
        notional = abs(price * qty)
        fee = notional * (self.fee_bps / 10_000)
        slip = notional * (self.slippage_bps / 10_000)
        return fee + slip

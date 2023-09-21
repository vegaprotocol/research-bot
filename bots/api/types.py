from dataclasses import dataclass


@dataclass
class Account:
    owner: str
    balance: int
    asset: str
    market_id: str
    type: str

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from systems.core.event_bus import EventBus
from systems.core.event_types import EventType
from systems.economy.credit_manager import CreditManager

logger = logging.getLogger("codebreak.economy")

SHOP_ITEMS_PATH = Path("data/shop_items.json")


@dataclass(frozen=True)
class ShopItem:
    item_id: str
    name: str
    cost: int
    category: str


def load_shop_catalog(path: Path = SHOP_ITEMS_PATH) -> dict[str, ShopItem]:
    if not path.exists():
        logger.warning("Shop catalog not found at %s, using an empty catalog", path)
        return {}

    with path.open("r", encoding="utf-8") as f:
        raw_items = json.load(f)

    return {entry["item_id"]: ShopItem(**entry) for entry in raw_items}


class ShopManager:
    def __init__(
        self,
        event_bus: EventBus,
        credit_manager: CreditManager,
        catalog: Optional[dict[str, ShopItem]] = None,
    ) -> None:
        self._event_bus = event_bus
        self._credit_manager = credit_manager
        self.owned_item_ids: set[str] = set()
        self.catalog = catalog if catalog is not None else load_shop_catalog()

    def purchase(self, item_id: str) -> None:
        if item_id in self.owned_item_ids:
            raise ValueError("Item already owned")
        item = self.catalog[item_id]
        self._credit_manager.spend(item.cost)
        self.owned_item_ids.add(item_id)
        self._event_bus.publish(EventType.PURCHASE_MADE, item_id=item_id, cost=item.cost)

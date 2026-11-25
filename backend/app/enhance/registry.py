from typing import Dict, List, Optional
from app.enhance.base import Enhancer


class StageRegistry:
    """
    Central registry for enhancement pipeline stages.
    Enables pluggable discovery of classical and deep restoration engines.
    """

    def __init__(self):
        self._stages: Dict[str, Enhancer] = {}

    def register(self, enhancer: Enhancer) -> None:
        self._stages[enhancer.name] = enhancer

    def get_stage(self, name: str) -> Optional[Enhancer]:
        return self._stages.get(name)

    def list_available(self) -> Dict[str, bool]:
        return {name: stage.is_available for name, stage in self._stages.items()}

    def get_all_stages(self) -> List[Enhancer]:
        return list(self._stages.values())


registry = StageRegistry()

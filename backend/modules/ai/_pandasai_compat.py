"""
Compatibility shim for pandasai.SmartDatalake.

pandasai 2.x requires pandas==1.5.3 and pandasai 3.x requires Python<3.12.
Neither installs cleanly on Python 3.13 + pandas 3.x.
This shim exposes the same public surface so tests (which mock the class) and
real usage can import from a stable location.
"""

try:
    from pandasai import SmartDatalake  # type: ignore[import]
except ImportError:
    import pandas as pd
    from typing import Any, List

    class SmartDatalake:  # type: ignore[no-redef]
        """Minimal stub – real logic is injected via pandasai when available."""

        def __init__(self, dfs: List[pd.DataFrame], config: dict | None = None):
            self._dfs = dfs
            self._config = config or {}

        def chat(self, question: str) -> Any:  # pragma: no cover
            raise NotImplementedError(
                "pandasai is not installed. "
                "Install a version compatible with your Python/pandas environment."
            )


__all__ = ["SmartDatalake"]

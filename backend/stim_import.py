"""Helpers to obtain a Stim-compatible module without shadowing real installations."""

try:  # pragma: no cover - simple import shim
    import stim as stim  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from backend import stim_stub as stim  # type: ignore

__all__ = ["stim"]

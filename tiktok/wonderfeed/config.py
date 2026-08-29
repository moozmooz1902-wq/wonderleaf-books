"""Configuration loading. Secrets come from the environment, never from YAML."""

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


class ConfigError(RuntimeError):
    pass


def _load_yaml(path, example_path):
    if not path.exists():
        raise ConfigError(
            f"Missing {path.relative_to(ROOT)}. Copy the example first:\n"
            f"  cp {example_path.relative_to(ROOT)} {path.relative_to(ROOT)}"
        )
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_settings(path=None):
    path = Path(path) if path else ROOT / "config" / "settings.yaml"
    return _load_yaml(path, ROOT / "config" / "settings.example.yaml")


def load_products(path=None):
    path = Path(path) if path else ROOT / "config" / "products.yaml"
    data = _load_yaml(path, ROOT / "config" / "products.example.yaml")
    products = data.get("products") or []
    if not products:
        raise ConfigError("No products defined in products.yaml")
    for p in products:
        for field in ("id", "name", "description"):
            if not p.get(field):
                raise ConfigError(f"Product {p.get('id', '?')} is missing '{field}'")
        if not p.get("angles"):
            raise ConfigError(f"Product {p['id']} has no angles - nothing to rotate through")
    return products


def secret(name, required=True):
    """Read a secret from the environment."""
    val = os.environ.get(name, "").strip()
    if not val and required:
        raise ConfigError(
            f"Environment variable {name} is not set. "
            f"Export it locally or add it as a GitHub Actions secret."
        )
    return val


def resolve_path(rel):
    """Resolve a config-relative path against the project root."""
    p = Path(rel)
    return p if p.is_absolute() else ROOT / p

"""Configuration loading. Secrets come from the environment, never from YAML."""

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path=None):
    """Read ROOT/.env into the environment.

    The desktop app is launched by double-clicking a script, which inherits no
    shell exports, so keys have to come from a file. Existing environment
    variables always win, so CI secrets are never overridden.
    """
    path = Path(path) if path else ROOT / ".env"
    if not path.exists():
        return {}
    loaded = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value
            loaded[key] = value
    return loaded


load_dotenv()


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
            f"{name} is not set. Put it in tiktok/.env as:\n"
            f"    {name}=your-key-here\n"
            f"(or export it, or add it as a GitHub Actions secret)"
        )
    return val


def resolve_path(rel):
    """Resolve a config-relative path against the project root."""
    p = Path(rel)
    return p if p.is_absolute() else ROOT / p

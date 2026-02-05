import tomllib
from pathlib import Path


def get_version_from_toml() -> str:
    """ Gets version from pyproject.toml file """
    with Path(Path(__file__).parent.parent / 'pyproject.toml').open('rb') as f:
        data = tomllib.load(f)

    version = data.get('project', {}).get('version') or \
              data.get('tool', {}).get('poetry', {}).get('version')

    return version

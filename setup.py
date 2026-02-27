from setuptools import setup, find_packages
from src import __version__

setup(
    name="codearon",
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "mlx-lm",
        "typer[all]",
        "rich",
        "gitpython",
        "pydantic",
        "pydantic-settings",
        "tree-sitter",
        "tree-sitter-languages",
        "questionary",
        "sqlmodel",
        "psutil",
        "prompt_toolkit",
        "fastembed",
        "qdrant-client",
        "Pillow",
    ],
    entry_points={
        "console_scripts": [
            "aron=src.main:app",
        ],
    },
)

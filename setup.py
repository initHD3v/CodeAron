from setuptools import setup, find_packages

setup(
    name="codearon",
    version="0.1.0",
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
    ],
    entry_points={
        "console_scripts": [
            "aron=src.main:app",
        ],
    },
)

from setuptools import setup

setup(
    name="local-reviewer",
    version="0.1.0",
    py_modules=["main", "scanner", "reviewer"],
    install_requires=[
        "rich",
        "ollama"
    ],
    entry_points={
        'console_scripts': [
            'review=main:cli_entrypoint', 
        ],
    },
)
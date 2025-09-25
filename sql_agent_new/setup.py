from setuptools import setup, find_packages

setup(
    name="sql_agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pymssql",
        "pandas",
        "matplotlib",
        "seaborn",
        "sqlalchemy",
        "python-dotenv",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "sql-cli=sql_agent.cli.sql_cli:main",
        ],
    },
)

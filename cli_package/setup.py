from setuptools import setup, find_packages

setup(
    name="task-monitor",
    version="1.0.0",
    description="Task Monitor CLI for multi-project task queue management",
    packages=["cli"],  # We'll move cli.py there
    install_requires=[],
    entry_points={
        'console_scripts': [
            'task-monitor=cli:main',
        ],
    )

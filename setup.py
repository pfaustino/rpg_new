"""
Setup configuration for rpg_modules package.
"""

from setuptools import setup, find_packages

setup(
    name="rpg_modules",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.6.0"
    ],
    author="RPG Game Developer",
    description="A collection of modules for building RPG games with Pygame",
    python_requires=">=3.7"
) 
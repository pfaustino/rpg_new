from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rpg-modules",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A collection of reusable RPG game modules for Pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rpg-modules",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Role-Playing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pygame>=2.0.0",
    ],
    keywords="pygame, rpg, game development, inventory system, item generation",
) 
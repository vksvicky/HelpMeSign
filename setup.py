#!/usr/bin/env python3
"""
Setup script for HelpMeSign
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="helpmesign",
    version="1.0.0",
    author="HelpMeSign Team",
    author_email="support@cycleruncode.club",
    description="A simple Python GUI application built with tkinter",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/vksvicky/helpmesign",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "coverage>=6.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "helpmesign=helpmesign.core.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "helpmesign": ["resources/*", "resources/*/*"],
    },
    zip_safe=False,
) 
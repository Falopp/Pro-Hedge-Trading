#!/usr/bin/env python3
"""
Setup configuration for Pro Hedge Trading System
"""

from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="pro-hedge-trading",
    version="2.0.0",
    description="Enterprise-grade funding rate arbitrage system for Binance and Hyperliquid",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Falopp/pro-hedge-trading-clean",
    author="Pro Hedge Trading Team",
    author_email="dev@prohedgetrading.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="trading, arbitrage, cryptocurrency, binance, hyperliquid, funding-rates",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pro-hedge=ui.app:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Falopp/pro-hedge-trading-clean/issues",
        "Documentation": "https://falopp.github.io/pro-hedge-trading-clean/",
        "Source": "https://github.com/Falopp/pro-hedge-trading-clean",
    },
) 
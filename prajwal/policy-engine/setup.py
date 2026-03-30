"""Setup configuration for MLOps Policy Engine."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mlops-policy-engine",
    version="1.0.0",
    author="MLOps Team",
    description="Multi-cloud policy engine for MLOps resource optimization, cost management, compliance, and scheduling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mlops-policy-engine",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=5.4",
        "flask>=2.0.0",
        "click>=8.0.0",
        "tabulate>=0.8.9",
    ],
    entry_points={
        "console_scripts": [
            "policy-engine=policy_engine.api.cli:cli",
        ],
    },
)

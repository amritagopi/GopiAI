from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pocketflow_framework",
    version="0.0.1",
    packages=find_packages(),
    description="Minimalist LLM Framework in 100 Lines. Enable LLMs to Program Themselves.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/The-Pocket-World/Pocketflow-Framework-Py",
    author="Helena Zhang",
    author_email="helenaz@stanford.edu",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
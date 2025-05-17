from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="trawl-translate-novel",
    version="0.1.0",
    author="AngYang",
    description="A tool for scraping, translating, and exporting Chinese novels",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/trawl_translate_novel",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "trawl-translate=main:app",
        ],
    },
) 
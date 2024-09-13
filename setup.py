from setuptools import setup, find_packages

setup(
    name="arxiv_loader",
    version="0.1",
    description="A Python module to load and scrape papers from arXiv on demand",
    author="Priyan P",
    author_email="ppattnay@uw.edu",
    url="https://github.com/ppattnayak/arxiv_loader",
    packages=find_packages(),
    install_requires=[
        "requests",
        "tqdm"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "arxiv-loader=arxiv_loader.loader:main"
        ]
    },
)

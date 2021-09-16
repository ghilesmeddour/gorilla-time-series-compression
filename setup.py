import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gorillacompression",
    version="0.1.0",
    author="Ghiles Meddour",
    author_email="ghiles.meddour@munic.io",
    description="Gorilla Time Series Compression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ghilesmeddour/gorilla-time-series-compression",
    project_urls={
        "Bug Tracker":
        "https://github.com/ghilesmeddour/gorilla-time-series-compression/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "bitarray",
    ],
)

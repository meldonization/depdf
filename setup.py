import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="depdf",
    version="0.0.1.dev1",
    author="Melton",
    author_email="mengzy1989@gmail.com",
    description="PDF table & paragraph extractor ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meldonization/depdf",
    packages=setuptools.find_packages(),
    install_requires=[
        "pdfplumber",
        "beautifulsoup4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)
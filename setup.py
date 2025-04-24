from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="html_transfer_md",
    version="0.1.0",
    author="lrs33",
    author_email="aslongrushan@gmail.com",
    description="A package to convert HTML tables to Markdown format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/charlie3go/html_transfer_md",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4>=4.9.0',
        'html2text>=2020.1.16',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

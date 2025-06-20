from setuptools import setup, find_packages
from pygoose.__version__ import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pygoose",
    version=__version__,
    author="Hydromel Victor Doledji",
    author_email="victorvaddely@gmail.com",
    description="ODM Python élégant pour MongoDB inspiré de Mongoose",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hydromelvictor/pygoose",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pymongo>=4.0.0",
        "python-dateutil>=2.8.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords="mongodb, odm, database, nosql, mongoose",
    project_urls={
        "Bug Reports": "https://github.com/hydromelvictor/pygoose/issues",
        "Source": "https://github.com/hydromelvictor/pygoose",
        "Documentation": "https://pymongoose.readthedocs.io/",
    },
)

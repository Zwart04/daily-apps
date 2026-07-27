from setuptools import setup, find_packages

setup(
    name="catatan-cepat",
    version="1.0.0",
    description="Catat apapun dari terminal dengan cepat. Gantungan kunci catatan buat programmer.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Daily App Builder",
    url="https://github.com/zwart-ops/20260705-catatan-cepat",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "catatan-cepat=src.cli:main",
        ],
    },
)

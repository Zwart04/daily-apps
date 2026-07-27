from setuptools import setup, find_packages

setup(
    name="pembersih-duplikat",
    version="1.0.0",
    description="Cari dan bersihkan file duplikat di komputer Anda",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Daily Apps",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "pembersih-duplikat=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
        "Topic :: System :: Filesystems",
    ],
)

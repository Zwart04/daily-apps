from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ctx",
    version="1.0.0",
    description="Codebase Context Extractor for AI coding assistants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zwart",
    author_email="zwart@qzz.io",
    url="https://github.com/zwart04/ctx",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "ctx=ctx.cli:main",
        ],
    },
    python_requires=">=3.10",
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
)

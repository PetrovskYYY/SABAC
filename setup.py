import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sabac",
    version="0.1.0",
    author="Yuriy Petrovskiy",
    author_email="yuriy.petrovskiy@gmail.com",
    description="Simple Attribute Based Access Control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Petrovskiy/SABAC",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sabac",
    version="0.0.1a",
    author="Yuriy Petrovskiy",
    author_email="yuriy.petrovskiy@gmail.com",
    description="Simple Attribute Based Access Control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PetrovskYYY/SABAC",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
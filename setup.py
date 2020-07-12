import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dotboy",
    version="0.1.4",
    author="Ben Buhse",
    author_email="ben@buhses.com",
    description="A Python script to help with dot file management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/bwbuhse/dotboy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'GitPython',
    ]
)

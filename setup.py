import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymazda",  # Replace with your own username
    version="0.0.8",
    author="bdr99",
    author_email="brandonrothweiler@gmail.com",
    description="An API client for interacting with the MyMazda (Mazda Connected Services) API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bdr99/pymazda",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["aiohttp", "pycryptodome"]
)

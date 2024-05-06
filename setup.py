import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async_api_caller",
    version="0.0.1",
    author="Amentum Scientific",
    author_email="team@amentum.space",
    description="Easily make asynchronous API web calls in Pythons",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amentumspace/async_api_caller.git",
    packages=setuptools.find_packages(),
    install_requires=['aiohttp', 'asyncio'],
)


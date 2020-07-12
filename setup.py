from setuptools import setup


# load the README file and use it as the long_description for PyPI
with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="rInject",
    description="An annotation-first dependency injection library for Python 3.",
    long_description=readme,
    long_description_content_type="text/markdown",
    version="0.1.0",
    author="Steve McCartney",
    author_email="python@reconvergent.com",
    url="https://github.com/stevemccartney/rinject",
    packages=["rinject"],
    include_package_data=True,
    python_requires=">=3.8.*",
    extras_require={"dev": ["pytest"]},
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="dependency injection inject injector di dic",
)

from setuptools import setup, find_packages

setup(
    name="fact-atomizer",
    version="0.1.0",
    description="AI-powered fact atomizer — decompose text into independently verifiable atomic claims",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Estimate Project",
    packages=find_packages(),
    install_requires=["openai>=1.0.0"],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
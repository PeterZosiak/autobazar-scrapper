from setuptools import setup, find_packages

setup(
    name="autobazar-screpper",
    version="0.1",
    packages=find_packages(),
    install_requires=["beautifulsoup4", "phonenumbers", "selenium", "validate_email"],
    entry_points={
        "console_scripts": [
            "autobazar-screpper = autobazar_screpper.screpper:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)

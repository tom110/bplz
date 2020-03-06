import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bplz",
    version="0.0.19",
    author="tom",
    author_email="tomyeying@gmail.com",
    description="http://www.giseden.xyz/?p=324",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tom110/bplz",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'bs4',
        'selenium',
        'psutil',
    ],
    entry_points={
        'console_scripts': [
            'bplz=bplz:__main__'
        ]
    },
    python_requires='>=3.6',
)

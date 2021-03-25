from setuptools import setup, find_packages
import re

version = '0.1.0'


with open('README.md', encoding='utf-8') as f:
    readme = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = [r.strip() for r in f]

setup(
    name = 'jsoneditor',
    version = version,
    py_modules=['jsoneditor'],
    url = 'https://github.com/dermasmid/py-jsoneditor',
    license = 'MIT',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    author = 'Cheskel Twersky',
    author_email= 'twerskycheskel@gmail.com',
    description = 'Visualize and edit JSON',
    keywords = 'python3 JSON jsoneditor',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = requirements,
    python_requires='>=3.6'
)
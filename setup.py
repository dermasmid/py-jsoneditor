from jsoneditor import __version__
from setuptools import setup
import pathlib



HERE = pathlib.Path(__file__).parent

with open(HERE / 'README.md', encoding='utf-8') as f:
    readme = f.read()

with open(HERE / 'requirements.txt', encoding='utf-8') as f:
    requirements = [r.strip() for r in f]

setup(
    name = 'jsoneditor',
    version = __version__,
    packages = ['jsoneditor'],
    include_package_data = True,
    url = 'https://github.com/dermasmid/py-jsoneditor',
    license = 'MIT',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    author = 'Cheskel Twersky',
    author_email = 'twerskycheskel@gmail.com',
    description = 'Visualize and edit JSON',
    keywords = 'python3 json jsoneditor api gui editor csv',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = requirements,
    python_requires = '>=3.6',
    entry_points = {
        'console_scripts': ['jsoneditor = jsoneditor:main']
    }
)

from setuptools import setup
from codecs import open
from os import path

__version__ = '0.0.1'

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = [x.strip() for x in f.readlines()]

setup(
    name='gdocs_converter',
    version='0.0.1',
    keywords='converter google docs microsoft office',
    author='Stenio Araujo',
    author_email='stenio@hiaraujo.com',
    description=(
        'gdocs-converter is a Python CLI used to convert Google Documents '
        '(.gdoc, .gsheet, .gslides) to Microsoft Office Documents '
        '(docx, xlsx, and pptx files).'),
    long_description=long_description,
    url='https://github.com/stenioaraujo/gdocs-converter',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    install_requires=install_requires,
    py_modules=['gdocs_converter'],
    entry_points={
        'console_scripts': ['gdocs-converter=gdocs_converter:main']}
)

"""
hypnofunk: A Python package for sleep analysis and hypnogram processing
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read version from __init__.py
def get_version():
    init_path = os.path.join('hypnofunk', '__init__.py')
    with open(init_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

setup(
    name='hypnofunk',
    version=get_version(),
    author='Rahul Venugopal',
    author_email='',
    description='A Python package for sleep analysis and hypnogram processing',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/rahulvenugopal/hypnofunk',
    packages=find_packages(exclude=['tests', 'examples']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy>=1.20.0',
        'pandas>=1.3.0',
        'matplotlib>=3.3.0',
    ],
    extras_require={
        'full': [
            'antropy>=0.1.4',
            'yasa>=0.6.0',
            'mne>=1.0.0',
        ],
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
            'mypy>=0.900',
        ],
    },
    keywords='sleep analysis hypnogram polysomnography sleep-stages transitions',
    project_urls={
        'Bug Reports': 'https://github.com/rahulvenugopal/hypnofunk/issues',
        'Source': 'https://github.com/rahulvenugopal/hypnofunk',
    },
)

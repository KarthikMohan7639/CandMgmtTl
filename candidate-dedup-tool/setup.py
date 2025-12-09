from setuptools import setup, find_packages

setup(
    name='candidate-dedup-tool',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'openpyxl',
        'fuzzywuzzy',
        'python-Levenshtein',
        'PyQt5',
    ],
    entry_points={
        'console_scripts': [
            'candidate-dedup-tool=app.main:main',
        ],
    },
    author='Your Name',
    description='Candidate Data Management & Deduplication Tool',
)

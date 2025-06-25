from setuptools import setup, find_packages

setup(
    name='python-ayristirici',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[],
    author='Your Name',
    description='Python ve C# kod ayrıştırıcı',
    entry_points={
        'console_scripts': [
            'ayristirici=main:terminal_arayuz',
        ],
    },
)

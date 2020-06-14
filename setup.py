"""The setup script."""

from setuptools import setup, find_packages

requirements = [
    'pandas',
    'quandl',
    'xlrd',
]

setup(
    name='expat_fatcat',
    version='0.1.0',
    description=(
        "expat-fatcat helps US taxpayers living abroad file their tax returns"
    ),
    long_description='',
    author="Paul Larsen",
    author_email='munichpavel@gmail.com',
    url='https://github.com/munichpavel/expat_fatcat',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='expat_fatcat',
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
)

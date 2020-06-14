"""The setup script."""

from setuptools import setup, find_packages

description = """
``expat-fatcat`` helps US taxpayers living abroad file their tax returns to
comply with the IRS and
FATCA (https://en.wikipedia.org/wiki/Foreign_Account_Tax_Compliance_Act).
A significant pain point in this process is that all foreign payments (income
or deductions) must be converted to USD with a valid rate on the date of
payment. This can readily add up to 40+ historical FX-rates to look up and
then paste into the usual Excel accounting madness. Some people may consider a
little copy-paste drudge work once a year a minor annoyance, but what are
programming and APIs for if not injecting some fun into an otherwise dreary
task?

The core functionality of ``expat-fatcat`` is an historical FX-rate lookup with
smoothing in case of a missing exhange rate. Currently, we use the FX-service
Quandl (https://www.quandl.com/) in ``QuandlRateCoverterToUSD``, which is a
sub-class of ``AbsRateConverterTo``. Other FX-rate services could be readily
integrated as required.
"""

requirements = [
    'quandl',
    'pandas',

]

setup(
    name='expat_fatcat',
    version='0.2.4',
    description=(
        "expat-fatcat helps US taxpayers living abroad with FX coversions "
        "for their tax returns."
    ),
    long_description=description,
    author="Paul Larsen",
    author_email='munichpavel@gmail.com',
    url='https://github.com/munichpavel/expat_fatcat',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=False,
    python_requires='>3.6',
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='expat_fatcat',
)

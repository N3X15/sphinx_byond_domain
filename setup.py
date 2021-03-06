# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = ''''''

requires = ['Sphinx>=0.6']

setup(
    name='sphinxcontrib-byonddomain',
    version='0.1',
    url='http://bitbucket.org/birkenfeld/sphinx-contrib',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-byond_domain',
    license='BSD',
    author='Rob "N3X15" Nelson',
    author_email='nexisentertainment@gmail.com',
    description='Sphinx domain for BYOND .dm scripts.',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)

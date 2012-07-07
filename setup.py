from setuptools import setup

version='1.0'

setup(
    name='proxychecker',
    version=version,
    description='Check proxies anonymity',
    author='Fabien Reboia',
    author_email='srounet@gmail.com',
    maintainer='Fabien Reboia',
    license='BEARWARE',
    url='http://github.com/srounet/qsys',
    packages=['proxychecker'],
    entry_points={
        'console_scripts': [
            'proxychecker = proxychecker.script:test_proxy',
        ]
    },
    install_requires=[],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
)

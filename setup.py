from distutils.core import setup

setup(
    name='EXbee',
    version='1.0',
    author='Esmairi Adel',
    author_email='esmairi.adel@gmail.com',
    packages=['EXbee'],
    url='http://code.google.com/p/python-xbee/',
    license='LICENSE.txt',
    description='Python tools for working with XBee radios',
    long_description=open('README.txt').read(),
    requires=['serial']
)

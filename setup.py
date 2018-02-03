import os
import sys

from setuptools import setup, find_packages

PROJECT_NAME = 'zmail'
MODULE_NAME = 'zmail'

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python3 setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

setup(
    name='zmail',
    version='0.0.3',

    author='ZYunH',
    author_email='workvl@163.com',

    description='None',
    long_description='None',
    keywords='',

    url='https://github.com/ZYunH/zmail',
    license="MIT Licence",

    platforms='all',

    packages=find_packages(),
    include_package_data=True,

)

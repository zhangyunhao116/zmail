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
    version='0.0.7',

    author='ZYunH',
    author_email='workvl@163.com',

    description='Zmail allows you to send and get emails as possible as it can be in python',
    long_description='Zmail allows you to send and get emails as possible as it can be in python.There is no need to check server address or make your own MIME string.With zmail, you only need to care about your mail content.',
    keywords='email python3 package',

    url='https://github.com/ZYunH/zmail',
    license="MIT Licence",

    platforms='all',

    packages=find_packages(),
    include_package_data=True,

)

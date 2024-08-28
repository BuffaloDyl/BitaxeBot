from setuptools import setup, find_packages
from setuptools.command.install import install as _install
import subprocess

class InstallWithPostInstall(_install):
    def run(self):
        _install.run(self)
        subprocess.call(['python3', 'post_install.py'])

setup(
    name='BitaxeBot-python',
    version='0.3',
    packages=find_packages(),
    py_modules=['BitaxeBot'],
    install_requires=[
        'requests',
        'telebot',
        'configparser',
    ],
    entry_points={
        'console_scripts': [
            'BitaxeBot = BitaxeBot:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    cmdclass={'install': InstallWithPostInstall},
)
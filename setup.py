from setuptools import setup, find_packages

setup(
    name='BitaxeBot',
    version='0.4',
    packages=find_packages(),
    py_modules=['BitaxeBot'],
    install_requires=[
        'requests',
        'telebot',
        'configparser',
        'secp256k1',
    ],
    entry_points={
        'console_scripts': [
            'BitaxeBot = BitaxeBot:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
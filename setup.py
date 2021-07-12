from setuptools import setup

setup (
    name='Security Group Search',
    version='1.0',
    py_modules=['secsearch'],
    install_requires=[
        'Click',
        'Rich'
    ],
    entry_points='''
        [console_scripts]
        secsearch=secsearch:cli
    '''
)
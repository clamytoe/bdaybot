from setuptools import find_packages, setup

import bdaybot

VERSION = bdaybot.__version__
AUTHOR = bdaybot.__author__
EMAIL = bdaybot.__email__

setup(
    name='bdaybot',
    version=VERSION,
    packages=find_packages(),
    url='https://github.com/clamytoe/bdaybot',
    license='MIT',
    author=AUTHOR,
    author_email=EMAIL,
    description='Birthday Slack Bot',
    install_requirements=[
        'APScheduler',
        'arrow',
        'flake8',
        'isort',
        'pylint',
        'pytest',
        'python-dateutil',
        'slackclient',
        'SQLAlchemy',
        'tox',
        'tox-travis',
    ],
    entry_points='''
        [console_scripts]
        bdaybot=bdaybot.bdaybot:run_bot
    ''',
)

print('\n\n\t\t    BDayBot version {} installation succeeded.\n'.format(VERSION))

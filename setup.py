from setuptools import setup, find_packages

setup(
    name='tnmake', # Thumbnail!MAKER
    version='0.2.0',
    license='GPLv3+',
    description='Thumbnail!MAKER creates for you customisable thumbnails with some additional tech information',
    package_dir={'':'src'},
    packages=find_packages(where='src'),
    author='nschepsen',
    author_email='schepsen@web.de',
    url='https://github.com/nschepsen/thumbnail-maker',
    keywords='library, video, tools',
    entry_points={
        'console_scripts': ['tnmake=tnmake.main:main']},
    classifiers=[
        'Development Status :: 4 - Beta'
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Natural Language :: English',
        'Natural Language :: German',
        'Natural Language :: Italian',
        'Natural Language :: Russian',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Desktop Environment',
        'Topic :: Home Automation',
        'Topic :: Multimedia :: Video :: Display', 'Topic :: Utilities'
        ]
)

# Thumbnail!MAKER creates customisable thumbnails and adds some tech details in the picture's header
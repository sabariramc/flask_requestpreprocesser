__author__ = "sabariram"
__version__ = "1.0"

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='Flask-RequestPreProcessor',
      version='0.2.0',
      python_requires='>=3.6',
      description='Request preprocessor for flask requests',
      url='https://github.com/sabariramc/flask_requestpreprocesser',
      author='Sabariram',
      author_email='c.sabariram@gmail.com',
      license='MIT Licence',
      packages=['flask_requestpreprocessor'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      install_requires=[
          'Flask>=1.1.*',
          'funcargpreprocessor==0.10.*'
      ],
      zip_safe=False, classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Environment :: Web Environment',
    ]
      )

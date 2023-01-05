from setuptools import setup, find_packages

setup(
    name='rafafun',
    version='1.0.2',
    license='MIT',
    author="Rafael G. Figueira",
    author_email='rafaelgfigueira@hotmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/rafaelgfig/rafafun',
    keywords='rafafun',
    install_requires=[
          'pandas',
		  'numpy',
		  'datetime'
      ],

)
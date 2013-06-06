from setuptools import setup, find_packages

from giphypop import __version__

setup(name='giphypop',
      version=__version__,
      description=("Python wrapper for Giphy API"),
      long_description=open('README.rst').read(),
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      keywords='python giphy api',
      author='Shaun Duncan',
      author_email='shaun.duncan@gmail.com',
      url='http://www.github.com/shaunduncan/giphypop/',
      license='MIT',
      packages=find_packages(),
      py_modules=['giphypop'],
      )


from distutils.core import setup
from Cython.Build import cythonize

setup(
		    ext_modules = cythonize("Main_Classification.pyx")
		    )

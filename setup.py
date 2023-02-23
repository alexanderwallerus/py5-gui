#this file enables pip installing the package under the provided name
import setuptools

if __name__ == "__main__":
    setuptools.setup(name='py5gui',
                     version='0.1',
                     py_modules=['py5gui'],
                     packages=setuptools.find_packages())
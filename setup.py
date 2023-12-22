#this file enables pip installing the package under the provided name
import setuptools

if __name__ == "__main__":
    setuptools.setup(name='py5gui',
                     version='0.1',
                     py_modules=['py5gui', 'utils.plot'],
                     packages=setuptools.find_packages(),
                     package_data={'fonts/roboto': ['*.ttf', '*.txt']}, # all .tff and .txt files
                     include_package_data=True,
                     install_requires=['pynput',]
                     )
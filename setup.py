#this file enables pip installing the package under the provided name
import setuptools

if __name__ == "__main__":
    setuptools.setup(name='py5gui',
                     version='0.1',
                     packages=setuptools.find_packages(),
                     # packages=['py5gui', 'py5gui.utils'],
                     
                     # include data files
                     package_dir={'py5gui': 'py5gui'},
                     package_data={'py5gui': ['fonts/roboto/*.txt', 'fonts/roboto/*.ttf']},
                     # include_package_data=True, #include data files defined in MANIFEST.in
                     
                     install_requires=['pynput']
                     )

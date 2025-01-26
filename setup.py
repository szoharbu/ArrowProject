
from setuptools import setup, find_packages

setup(
    name='Arrow',
    version='0.1.0',
    packages=find_packages(where='Arrow'),  # Ensures it looks in the right directory
    package_dir={'': 'Arrow'},  # Root directory for packages
    python_requires='>=3.12',
    install_requires=[
        'requests',  # Add your actual dependencies
        'numpy',
        'streamlit',
        #'pandas',  # Example additional dependency
    ],
    entry_points={
        'console_scripts': [
            'arrow = Arrow.cli:main',  # Replace with your CLI entry point
        ],
    },
    author='Zohar Buchris',
    author_email='szoharbu@gmail.com',
    description='An architecture-agnostic stimuli generator for architectural and micro-architectural contexts',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/szoharbu/ArrowProject.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)

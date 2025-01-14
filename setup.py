from setuptools import setup, find_packages

setup(
    name='desktop-compose',
    version='0.0.1',
    author='Sean May',
    author_email='sean.may.developer@gmail.com',
    description='A tool for setting up templates for virtual desktops on Windows 11',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sean-P-May/desktop-compose",
    packages=find_packages(),  # Find other packages (if applicable)
    entry_points={
        'console_scripts': [
            'desktop-compose=bin.desktop_compose:app',  # Entry point references main() in bin/desktop_compose.py
        ],
    },
    include_package_data=True,
    install_requires=[
        "pyvda",
        "pywin32",
        "pyYAML",
        ""# Add other dependencies as needed
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)

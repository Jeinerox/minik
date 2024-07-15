from setuptools import setup, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="minik",
    version="0.1",
    author="jeinerox",
    description="A command-line tool to manage Minecraft servers using tmux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jeinerox/Minik.git",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'click',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'mc-manager=cli:cli',
        ],
    },
    data_files=[
        ('/etc/systemd/system', ['services/minecraft.service']),
    ],
    include_package_data=True,
    scripts=['scripts/start_servers.sh', 'install_services.sh'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
)
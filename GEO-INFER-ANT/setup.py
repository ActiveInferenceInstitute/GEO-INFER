"""
Setup configuration for GEO-INFER-ANT package.

This module provides the setup configuration for installing the GEO-INFER-ANT
swarm intelligence and complex adaptive systems framework.
"""

from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
def get_version():
    """Get version from package __init__.py."""
    init_file = os.path.join(os.path.dirname(__file__), 'src', 'geo_infer_ant', '__init__.py')
    with open(init_file, 'r') as f:
        content = f.read()

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if version_match:
        return version_match.group(1)
    return '1.0.0'

# Read README for long description
def get_long_description():
    """Get long description from README."""
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='geo-infer-ant',
    version=get_version(),
    author='GEO-INFER Development Team',
    author_email='dev@geo-infer.org',
    description='Swarm Intelligence and Complex Adaptive Systems for Geospatial Analysis',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/GEO-INFER/GEO-INFER-ANT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='swarm intelligence, complex adaptive systems, active inference, geospatial analysis, ant colony optimization, particle swarm optimization',
    python_requires=">=3.11",
    install_requires=[
        'numpy>=1.21.0',
        'scipy>=1.7.0',
        'matplotlib>=3.5.0',
        'networkx>=2.8',
        'geopandas>=0.10.0',
        'h3>=4.0.0',
        'scikit-learn>=1.1.0',
        'pyyaml>=6.0',
        'jsonschema>=4.0.0',
        'asyncio-mqtt>=0.11.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.18.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'myst-parser>=0.17.0',
        ],
        'integration': [
            'geo-infer-act>=1.0.0',
            'geo-infer-space>=1.0.0',
            'geo-infer-agent>=1.0.0',
            'geo-infer-math>=1.0.0',
            'geo-infer-time>=1.0.0',
        ],
        'visualization': [
            'plotly>=5.0.0',
            'folium>=0.12.0',
            'seaborn>=0.11.0',
            'bokeh>=2.4.0',
        ],
        'performance': [
            'numba>=0.56.0',
            'cython>=0.29.0',
            'ray>=2.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'geo-infer-ant-demo=geo_infer_ant.examples.swarm_intelligence_demo:main',
        ],
    },
    include_package_data=True,
    package_data={
        'geo_infer_ant': [
            'config/*.yaml',
            'config/*.json',
            'docs/*.md',
            'examples/*.py',
            'tests/**/*.py',
        ]
    },
    zip_safe=False,
    project_urls={
        'Documentation': 'https://geo-infer.readthedocs.io/en/latest/modules/ant.html',
        'Source': 'https://github.com/GEO-INFER/GEO-INFER-ANT',
        'Tracker': 'https://github.com/GEO-INFER/GEO-INFER-ANT/issues',
        'Funding': 'https://opencollective.com/geo-infer',
    },
)

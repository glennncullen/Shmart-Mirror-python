import sys
sys.path.insert(0, 'app')

from setuptools import setup

setup(
    name='shmart_mirror',
    packages=[
		'app', 
		'app.mqtt', 
		'app.mirror'
		],
    version="1.5",
    author='Glenn Cullen',
    description='Home Smart Mirror application',
    install_requires=[
		'feedparser', 
		'requests>=2.20.0', 
		'Pillow', 
		'python-firebase', 
		'google-cloud-storage'
		]
    )

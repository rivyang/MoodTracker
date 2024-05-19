from setuptools import setup, find_packages

setup(
    name='moodtracker',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==2.0.1',
        'Flask-SQLAlchemy==2.5.1',
        'pytest==6.2.2',
        'Jinja2==3.0.1'
    ],
)

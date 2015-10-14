try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='paddingoracle',
    author='Marcin Wielgoszewski',
    author_email='marcin.wielgoszewski@gmail.com',
    version='0.2.1',
    url='https://github.com/mwielgoszewski/python-paddingoracle',
    py_modules=['paddingoracle'],
    description='A portable, padding oracle exploit API',
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python'
    ]
)

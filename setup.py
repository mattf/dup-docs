import setuptools

setuptools.setup(
    name="minhash",
    version="0.1.1",
    author="Matthew Farrellee",
    author_email="matt@cs.wisc.edu",
    description="A playground minhash implementation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mattf/minhash",
    py_modules=['minhash'],
    install_requires=['numpy', 'gensim', 'mfoops'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

import setuptools

setuptools.setup(
    name="diffhest",
    version="0.0",
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires=">=3.9",
    install_requires=[
        'phabricator',
        'requests',
        'tornado',
    ],
    entry_points=dict(
        console_scripts=[
            'diffhest = diffhest.__main__:main',
        ]
    ),
    extras_require={
        # 'test': [
        #     'pytest',
        #     'pytest-cov',
        # ],
    }
)

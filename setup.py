from setuptools import setup

setup(
    name='virtual_copernicus_ng',
    version='1.0',
    packages=['virtual_copernicus_ng'],
    package_data={'virtual_copernicus_ng': ['images_copernicus/*.png']},
    include_package_data=True,
    install_requires=[
        'gpiozero == 1.5.1',
        'numpy == 1.19.4',
        'Pillow == 8.0.1',
        'scipy == 1.5.4',
        'sounddevice == 0.4.1',
    ],
)

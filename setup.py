from setuptools import setup, find_packages

setup(
    name='exnavy',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'safetensors==0.3.1',
        'requests==2.31.0',
        'tqdm==4.65.0',
        'PyYAML==6.0',
        'gdown==4.7.1',
        'toml==0.10.2',
        'rarfile==4.0',
        'xmltodict==0.13.0',
        'pydantic==1.10.9'
    ],
    author='Revaldo',
    author_email='revaldoanjennurillifanderson@gmail.com',
    description='A utility library for Other Notebook',
    url='https://github.com/Hplayfree25/exnavy',
)

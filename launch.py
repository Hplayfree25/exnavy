from setuptools import setup, find_packages

setup(
    name='exnavy',
    version='0.0.1',
    description='Paket ini dirancang untuk memastikan operasi Stable Diffusion yang mulus di berbagai platform notebook.',
    author='Revaldo',
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
    author_email='revaldoanjennurillifanderson@gmail.com',
    url='https://github.com/Hplayfree25/exnavy',
    keywords='ExNavy',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.8',
    ],
)
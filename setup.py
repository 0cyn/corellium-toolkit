from setuptools import setup

setup(name='corellium-toolkit',
      version='0.1.0',
      description='Corellium Tookit',
      long_description='file: README.md',
      long_description_content_type='text/markdown',
      author='kat',
      url='https://github.com/kritantadev/corellium-toolkit',
      install_requires=['requests'],
      packages=['kcorellium'],
      package_dir={
            'kcorellium': 'src/kcorellium',
      },
      classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent'
      ],
      scripts=['bin/cachebuilder', 'bin/corctl']
      )

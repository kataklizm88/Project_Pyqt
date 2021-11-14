from setuptools import setup, find_packages

setup(name="kataklizm_msg_client",
      version="0.0.1",
      description="kataklizm_msg_client",
      author="Vlad Mityushov",
      author_email="mitelenager@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
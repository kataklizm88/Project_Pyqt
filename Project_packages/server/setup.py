from setuptools import setup, find_packages

setup(name="kataklizm_msg_server",
      version="0.0.1",
      description="kataklizm_msg_server",
      author="Vlad Mityushov",
      author_email="mitelenager@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )

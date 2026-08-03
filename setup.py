from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Mx-Scanner-Wifi",
    version="1.0.0",
    author="Falconmx1",
    author_email="falconmx1@example.com", # Reemplaza con tu email
    description="Una herramienta avanzada para escanear y analizar redes WiFi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Falconmx1/Mx-Scanner-Wifi",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking :: Monitoring",
        "Intended Audience :: System Administrators",
    ],
    python_requires='>=3.7',
    install_requires=[
        "scapy",
        "wifi",
        "colorama",
        "tabulate",
        "netifaces",
    ],
    entry_points={
        "console_scripts": [
            "mx-scanner=src.main:main",  # Crea un comando ejecutable
        ],
    },
)

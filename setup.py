from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).resolve().parent
README = (here / "README.txt").read_text(encoding="utf-8")
CHANGES = (here / "CHANGES.txt").read_text(encoding="utf-8")
REQUIREMENTS = [
    line.strip()
    for line in (here / "requirements.txt").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.strip().startswith("#")
]

setup(
    name="bireme-opentrials",
    version="1.0.17",
    packages=find_packages(),
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
    python_requires=">=3.8,<4",
    keywords="open-trials clinical-trial health application bireme",
    author="BIREME/OPAS/OMS",
    author_email="opentrials-dev@listas.bireme.br",
    url="http://reddes.bvsalud.org/projects/clinical-trials/",
    license="LGPL v2.1 (http://www.gnu.org/licenses/lgpl-2.1.txt)",
    install_requires=REQUIREMENTS,
    test_suite="opentrials",
    tests_require=["nose"],
)

"""doc-structure-router setup"""
from setuptools import setup, find_packages

setup(
    name="doc-structure-router",
    version="0.1.0",
    description="文档结构智能路由 - 自动检测文档结构，选择最佳切分策略",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="violetlength",
    author_email="",
    url="https://github.com/violetlength/doc-structure-router",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "pdf": ["pdfplumber>=0.10.0", "PyPDF2>=3.0.0"],
        "ocr": [
            "paddlepaddle>=2.5.0",
            "paddleocr>=2.7.0",
            "PyMuPDF>=1.23.0",
        ],
        "ocr-tesseract": [
            "pytesseract>=0.3.10",
            "Pillow>=10.0.0",
            "PyMuPDF>=1.23.0",
        ],
        "all": [
            "pdfplumber>=0.10.0",
            "PyPDF2>=3.0.0",
            "paddlepaddle>=2.5.0",
            "paddleocr>=2.7.0",
            "PyMuPDF>=1.23.0",
        ],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="document splitter chunking vector-database rag",
)

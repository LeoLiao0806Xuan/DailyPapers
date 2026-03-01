from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dailypapers",
    version="1.0.0",
    description="自动抓取高引用论文并推送至GitHub Issue",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your-email@example.com",
    url="https://github.com/yourusername/dailypapers",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0,<3.0",
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "feedparser>=6.0.0"
    ],
    extras_require={
        "proxy": ["PySocks>=1.7.1"]
    },
    entry_points={
        "console_scripts": [
            "dailypapers = dailypapers.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8"
)

from setuptools import setup, find_packages

setup(
    name="adaptive_learning_ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open("requirements.txt") 
        if line.strip() and not line.startswith("#")
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="ИИ-ассистент адаптивного обучения",
    keywords="education, adaptive learning, ai, llm, personalization",
    url="https://github.com/username/adaptive-learning-ai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
)
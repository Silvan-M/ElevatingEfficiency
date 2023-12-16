# Sphinx Documentation
To update the documentation, run the following command in the terminal from the project directory:
```bash
cd docs
sphinx-apidoc -o . .. ../main.py
make html
```
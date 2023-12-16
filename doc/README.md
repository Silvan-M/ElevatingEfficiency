# Sphinx Documentation
To update the documentation, run the following command in the terminal from the project directory:
```bash
cd doc
sphinx-apidoc -o . .. ../main.py
make html
```

And then simply push. The documentation will be automatically updated on GitHub Pages via the GitHub Action.
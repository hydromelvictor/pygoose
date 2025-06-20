#!/bin/bash
python -m build
python -m twine check dist/*

# scripts/publish-test.sh
#!/bin/bash
python -m twine upload --repository testpypi dist/*

# scripts/publish.sh
#!/bin/bash
python -m twine upload dist/*

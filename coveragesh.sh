#!/bin/bash

# pytest --collect-only
# pytest --ignore-glob=*test_ui* -vv
# pytest -v test_cases/test_scoringboard.py 
coverage run --source=. -m pytest
#coverage run -m pytest
coverage html
cd htmlcov/
firefox mcst_py.html

#!/bin/bash

# pytest --collect-only
# pytest --ignore-glob=*test_ui* -vv
#coverage run --source=. -m pytest
coverage run -m pytest
coverage html
cd htmlcov/
firefox saving_loading_py.html

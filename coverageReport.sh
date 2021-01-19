export PYTHONPATH="venv/Scripts"
python -m unittest discover --start-directory ./tests # run all tests 
# coverage run -m unittest discover --start-directory ./tests # generate test coverage information
coverage run -m pytest ./tests # generate test coverage information
coverage report -m # Generate report
read -n1 -r -p "Press any key to continue..." key
coverage erase
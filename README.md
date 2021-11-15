# PythonAPItests

A simple api test suite to do basic api validations

## Versions

Python 3.6.8
pip 21.0.1

## Setup OR Installations
- Checkout the project
- Install python3
- Run ./setup.sh  (This is will install all the required dependancies)
- Run source venv/bin/activate
- Setup is done



## Configurations
`/plugins/configuration.py` is setup to run the tests with different configurations. `/cfg` contains the 1 configuration file containing the url localhost.

## Folder structure

The tests are added under `/tests` directory an api_helper is add in the `/lib`

## Running
pre-condition : run the sudoku java application in http://localhost:8080/
It is possible to run all tests on the local environment after following the above steps for setup with the following command :
  - `pytest --cfg cfg/config.py tests/ `

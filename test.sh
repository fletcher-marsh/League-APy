#!/bin/bash

help()
{
  echo "Using test.sh:"
  echo
  echo "The test script makes executing tests easy-peasy."
  echo "Run with no arguments from the root to run all tests:"
  echo
  echo -e "\t./test.sh"
  echo
  echo "Run with arguments to run individual test(s):"
  echo
  echo -e "\t./test.sh test.test_util.MatchUtilTestCase.test_get_champ_id  test.test_util.MatchUtilTestCase.test_get_champ_name"
  echo
  echo "To access this help message:"
  echo
  echo -e "\t./test.sh -h"
  echo
  echo "Syntax: ./test.sh [<test_case_or_method_0>, <test_case_or_method_1>, ... , <test_case_or_method_n>],"

}

if [[ $# -eq 0 ]]
then
  python3 -m unittest discover .
elif [[ "$1" = "-h" || "$1" = "--help" || "$1" = "help" ]]
then
  help
else
  for test_case in "$@"
  do
    echo "Running $test_case..."
    python3 -m unittest "$test_case"
    echo
    echo
  done
fi
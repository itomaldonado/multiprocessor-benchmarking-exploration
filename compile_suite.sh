#!/bin/bash 

# clean old compilations
make clean

# Create the './bin' directory if it doesn't exist
mkdir -p ./bin

# compile suite
make suite
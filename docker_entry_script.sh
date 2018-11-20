#!/bin/bash

set -e
set -x
compiler=$1
version=$2

pip install meson --upgrade
pip install ninja --upgrade


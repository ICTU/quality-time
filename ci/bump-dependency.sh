#!/bin/bash

# Update a specific direct dependency: $ ci/bump-dependency.sh <file type> <old spec> <new spec>
# For example: $ ci/bump-dependency.sh toml pip==1.2.3 pip==1.2.4
#
# To look for current versions of packages: $ ci/bump-dependency.sh <file type> <(part of) old spec>
# For example: $ ci/bump-dependency.sh toml pip

PATH="$PATH:ci"
source base.sh

if [[ "$3" == "" ]]; then
    run git ls-files | grep "$1\$" | xargs grep $2
else
    run git ls-files | grep "$1\$" | xargs sed -i "" "s/$2/$3/g"
fi

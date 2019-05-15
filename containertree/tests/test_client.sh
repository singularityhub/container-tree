#!/bin/bash

# Include help functions
. helpers.sh

echo
echo "************** START: test_client.sh **********************"

# Create temporary testing directory
echo "Creating temporary directory to work in."
tmpdir=$(mktemp -d)
output=$(mktemp ${tmpdir:-/tmp}/containertree_test.XXXXXX)

echo "Testing help commands..."

runTest 0 $output containertree --help
for command in templates generate;
    do
    runTest 0 $output containertree $command --help 
done

echo "Testing version command..."
runTest 0 $output containertree --version

echo "#### Testing generate command"
runTest 0 $output containertree generate --output $tmpdir vanessa/salad
runTest 0 $output test -f "$tmpdir/index.html"
runTest 0 $output test -f "$tmpdir/data.json"
runTest 0 $output containertree generate vanessa/salad --print index.html
runTest 0 $output containertree generate vanessa/salad --print data.json

echo "#### Testing templates command"
runTest 0 $output containertree templates
runTest 0 $output containertree generate --output $tmpdir vanessa/salad --template tree

echo "Finish testing basic client"
rm -rf ${tmpdir}

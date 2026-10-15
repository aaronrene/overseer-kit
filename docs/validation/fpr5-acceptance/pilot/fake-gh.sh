#!/bin/sh
set -eu
printf "%s\n" "$*" >> /private/tmp/overseer-fpr5-integrated-pilot-20261015/evidence/fake-gh-argv.txt
case "$2" in
 view) printf "%s\n" '{"number":17,"url":"https://github.com/pilot-fixture/overseer-integrated/pull/17","state":"OPEN","mergeable":"MERGEABLE","mergeStateStatus":"CLEAN"}';;
 checks) printf "pilot-local\tpass\t1s\thttps://example.invalid/fake-check\n";;
 *) exit 97;;
esac

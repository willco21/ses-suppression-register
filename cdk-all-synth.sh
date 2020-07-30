#!/bin/bash -ex

IFS=$'\n'
for stack in $(cdk ls)
do
cdk synth $stack > ./output_template/$stack.yml
done

git add ./output_template/*
#!/bin/bash

git fetch --depth 1
git reset --hard origin/master
git clean -dfx

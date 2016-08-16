#!/bin/bash
scss --watch --sourcemap=none $(dirname $0)/.. --style expanded

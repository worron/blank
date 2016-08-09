#!/bin/bash
scss --watch --sourcemap=none $(dirname $0)/../gtk-3.0 --style expanded

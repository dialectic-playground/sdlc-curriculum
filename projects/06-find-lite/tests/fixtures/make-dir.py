"""Test helper for dp-find -exec: create the directory named by the argument."""
import os
import sys

os.mkdir(sys.argv[1])

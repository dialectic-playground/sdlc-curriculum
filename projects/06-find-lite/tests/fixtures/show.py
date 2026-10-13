"""Test helper for dp-find -exec: print the arguments this process received."""
import sys

line = "show.py:" + "".join(" [" + arg + "]" for arg in sys.argv[1:]) + "\n"
sys.stdout.buffer.write(line.encode("utf-8"))

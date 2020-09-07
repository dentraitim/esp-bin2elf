#!/usr/bin/env python3
import sys
flash_bin = open(sys.argv[1], "rb")
flash_bin.seek(0x10000)
user_bin = open(sys.argv[2], "wb")
user_bin.write(flash_bin.read())
user_bin.close()
flash_bin.close()
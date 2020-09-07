#!/usr/bin/env python3
# https://github.com/esp8266/esp8266-wiki/wiki/Memory-Map
import sys
# sys.path.append("/home/user/.local/bin/esptool.py") # `which esptool.py`
from esp_elf import XtensaElf, ElfSection
import esptool

if len(sys.argv) == 1:
    print('Usage: ./user_bin_to_elf.py user_app.bin\r\n\r\nThis tool will generate user_app.bin.elf')
    exit(1)

image = esptool.LoadFirmwareImage("", sys.argv[1])
out_elf_file = sys.argv[1] + '.elf'
elf = XtensaElf(out_elf_file, image.entrypoint)

print('Image version: %d' % image.version)
print('Entry point: 0x%08x' % image.entrypoint if image.entrypoint != 0 else 'Entry point not set')
print('%d segments' % len(image.segments))
idx = 0
for seg in image.segments:
    idx += 1
    seg_name = ", ".join([seg_range[2] for seg_range in image.ROM_LOADER.MEMORY_MAP if seg_range[0] <= seg.addr < seg_range[1]])
    print('Segment %d: %r [%s]' % (idx, seg, seg_name))

    elf_section = ElfSection(seg_name, seg.addr, seg.data, seg_name[0] == 'I')
    elf.add_section(elf_section, True)

elf.generate_elf()
elf.write_to_file(out_elf_file)
print("Wrote: %s" % (out_elf_file))

# Checksum
calc_checksum = image.calculate_checksum()
print('Checksum: %02x (%s)' % (image.checksum,
                               'valid' if image.checksum == calc_checksum else 'invalid - calculated %02x' % calc_checksum))
try:
    digest_msg = 'Not appended'
    if image.append_digest:
        is_valid = image.stored_digest == image.calc_digest
        digest_msg = "%s (%s)" % (hexify(image.calc_digest).lower(),
                                  "valid" if is_valid else "invalid")
        print('Validation Hash: %s' % digest_msg)
except AttributeError:
    pass  # ESP8266 image has no append_digest field

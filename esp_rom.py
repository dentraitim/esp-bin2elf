# esp-bin2elf written by Joel Sandin <jsandin@gmail.com>
#
# MIT licence

# references:
#   - https://github.com/espressif/esptool/wiki/Firmware-Image-Format
#   - https://www.pushrate.com/blog/articles/esp8266_boot

from esp_memory_map import find_region_for_address

from io import BytesIO
from struct import pack, unpack


class EspRom(object):
    def __init__(self, rom_name, rom_bytes_stream, flash_layout, offset=0):
        self.name = rom_name
        self.sections = []
        self.contents = rom_bytes_stream.read()
        rom_bytes_stream.seek(offset)

        self.header = EspRomHeader.get_header(rom_bytes_stream)
        if isinstance(self.header, EspRomE4Header) or isinstance(self.header, EspRomEAHeader):
            # .irom0.text is directly after, followed by a secondary 0xe9 header
            irom_size = self.header.length
            irom_text_contents = rom_bytes_stream.read(irom_size)
            if len(irom_text_contents) != irom_size:
                raise RomParseException(
                    "EspRom.init(): unexpected .irom0.text size - %d != %d." %
                    (len(irom_text_contents), irom_size))
            self.header = EspRomE9Header(rom_bytes_stream)
        else:
            # read the irom0.text section from flash, non-OTA case.
            irom_section = flash_layout['.irom0.text']
            irom_size = irom_section.size * 1024
            limit = irom_section.offset + irom_size
            irom_text_contents = self.contents[irom_section.offset:limit]

        # add .irom0.text section
        irom_address = 0x40200000
        section = EspRomSection(BytesIO(irom_text_contents), irom_address, irom_size)
        self.sections.append(section)

        for i in range(0, self.header.sect_count):
            section = EspRomSection(rom_bytes_stream)
            self.sections.append(section)

    def __str__(self):
        rep = "EspRom("
        rep += "name: %s, " % self.name
        rep += "header: %s, " % self.header
        rep += "len(sections): %d, " % len(self.sections)
        rep += "len(contents): %d)" % len(self.contents)

        return rep


class EspRomHeader(object):
    @staticmethod
    def get_header(rom_bytes_stream):
        header_type = rom_bytes_stream.read(1)[0]
        rom_bytes_stream.seek(-1, 1)    # relative position

        if header_type == 0xea:
            return EspRomEAHeader(rom_bytes_stream)
        elif header_type == 0xe9:
            return EspRomE9Header(rom_bytes_stream)
        elif header_type == 0xe4:
            return EspRomE4Header(rom_bytes_stream)
        else:
            raise RomParseException(
                "EspRomHeader.get_header: Unrecognized magic_number 0x%02x" % header_type)


class EspRomE9Header(EspRomHeader):
    MAGIC = 0xe9
    ROM_HEADER_SIZE = 8

    def __init__(self, rom_bytes_stream):
        # typedef struct {
        #     uint8 magic;
        #     uint8 sect_count;
        #     uint8 flags1;
        #     uint8 flags2;
        #     uint32 entry_addr;
        # } rom_header;

        rom_header_bytes = rom_bytes_stream.read(EspRomE9Header.ROM_HEADER_SIZE)

        if len(rom_header_bytes) != EspRomE9Header.ROM_HEADER_SIZE:
            raise RomParseException(
                "EspRomE9Header.init(): len(rom_header_bytes) is %d bytes != %d bytes." %
                (len(rom_header_bytes), EspRomE9Header.ROM_HEADER_SIZE))

        if rom_header_bytes[0] != 0xe9:
            raise RomParseException(
                "EspRomE9Header.init(): magic_number is 0x%02x != 0x%02x." %
                (rom_header_bytes[0], self.MAGIC))

        self.magic = rom_header_bytes[0]
        self.sect_count = rom_header_bytes[1]
        self.flags1 = rom_header_bytes[2]
        self.flags2 = rom_header_bytes[3]
        self.entry_addr = unpack('<I', rom_header_bytes[4:8])[0]

        super(EspRomE9Header, self).__init__()

    def __str__(self):
        rep = "EspRomE9Header("
        rep += "magic: 0x%02x, " % self.magic
        rep += "sect_count: %d, " % self.sect_count
        rep += "flags1: 0x%02x, " % self.flags1
        rep += "flags2: 0x%02x, " % self.flags2
        rep += "entry_addr: 0x%08x)" % self.entry_addr

        return rep


class EspRomE4Header(EspRomHeader):
    ROM_HEADER_SIZE = 16

    def __init__(self, rom_bytes_stream):
        # typedef struct {
        #     uint8 magic1;
        #     uint8 magic2;
        #     uint8 config[2];
        #     uint32 entry_addr;
        #     uint8 unused[4];
        #     uint32 length;
        # } rom_header;

        rom_header_bytes = rom_bytes_stream.read(EspRomE4Header.ROM_HEADER_SIZE)

        if len(rom_header_bytes) != EspRomE4Header.ROM_HEADER_SIZE:
            raise RomParseException(
                "EspRomE4Header.init(): len(rom_header_bytes) is %d bytes != 16 bytes." % len(rom_header_bytes))

        if rom_header_bytes[0] != 0xe4:
            raise RomParseException(
                "EspRomE4Header.init(): magic1 is 0x%02x != 0xe4." % rom_header_bytes[0])

        if rom_header_bytes[1] != 0x04:
            raise RomParseException(
                "EspRomE4Header.init(): magic2 is 0x%02x != 0x04." % rom_header_bytes[1])

        self.magic1 = rom_header_bytes[0]
        self.magic2 = rom_header_bytes[1]
        self.config = unpack('<BB', rom_header_bytes[2:4])
        self.entry_addr = unpack('<I', rom_header_bytes[4:8])[0]
        self.unused = unpack('<BBBB', rom_header_bytes[8:12])
        self.length = unpack('<I', rom_header_bytes[12:16])[0]

        super(EspRomE4Header, self).__init__()

    def __str__(self):
        rep = "EspRomE4Header("
        rep += "magic1: 0x%02x, " % self.magic1
        rep += "magic2: 0x%02x, " % self.magic2
        rep += "config: %d, " % self.config
        rep += "entry_addr: 0x%08x, " % self.entry_addr
        rep += "unused: 0x%02x, " % self.unused
        rep += "length: %d)" % self.length

        return rep


class EspRomEAHeader(EspRomHeader):
    MAGIC = 0xea
    SIZE = 16

    def __init__(self, rom_bytes_stream):
        # typedef struct {
        #     uint8 magic;
        #     uint8 unused1;    // always 4
        #     uint8 flags1;
        #     uint8 flags2;
        #     uint32 entry_addr;
        #     uint32 unused2;   // always 0
        #     uint32 length;
        # } rom_header;

        header = rom_bytes_stream.read(self.SIZE)
        if len(header) != self.SIZE:
            raise RomParseException(
                "EspRomEAHeader.init(): len(rom_header_bytes) is %d bytes != %d bytes." %
                (len(header), self.SIZE))

        self.magic = header[0]
        if self.magic != self.MAGIC:
            raise RomParseException(
                "EspRomEAHeader.init(): magic_number is 0x%02x != 0x%02x." %
                (header[0], self.MAGIC))

        if header[1] != 4:
            raise RomParseException(
                "EspRomEAHeader.init(): unexpected unused1 value - 0x%02x != 4." % header[1])

        unused2 = unpack('<I', header[8:12])[0]
        if unused2 != 0:
            raise RomParseException(
                "EspRomEAHeader.init(): unexpected unused2 value - %d != 0." % unused)

        self.flags1 = header[2]
        self.flags2 = header[3]
        self.entry_addr = unpack('<I', header[4:8])[0]
        self.length = unpack('<I', header[12:16])[0]

        super(EspRomEAHeader, self).__init__()

    def __str__(self):
        rep = "EspRomEAHeader("
        rep += "magic: 0x%02x, " % self.magic
        rep += "flags1: 0x%02x, " % self.flags1
        rep += "flags2: 0x%02x, " % self.flags2
        rep += "entry_addr: 0x%08x, " % self.entry_addr
        rep += "length: %d)" % self.length

        return rep


class EspRomSection(object):
    SECTION_HEADER_SIZE = 8

    def __init__(self, rom_bytes_stream, address=None, length=None):
        # typedef struct {
        #     uint32 address;
        #     uint32 length;
        # } sect_header;

        if not address or not length:
            section_header_bytes = rom_bytes_stream.read(EspRomSection.SECTION_HEADER_SIZE)

            if len(section_header_bytes) != EspRomSection.SECTION_HEADER_SIZE:
                raise RomParseException(
                    "EspRomSection.init(): section_header_bytes is %d bytes != %d bytes." %
                    (len(section_header_bytes), EspRomSection.SECTION_HEADER_SIZE))

            self.address = unpack('<I', section_header_bytes[0:4])[0]
            self.length = unpack('<I', section_header_bytes[4:8])[0]

        else:
            # support specified length and address for non-OTA case and new header
            self.address = address
            self.length = length

        self.contents = rom_bytes_stream.read(self.length)

        if len(self.contents) != self.length:
            raise RomParseException(
                "EspRomSection.init(): self.contents is %d bytes != self.length %d." %
                (len(self.contents), self.length))

    def __str__(self):
        rep = "EspRomSection("
        rep += "address: 0x%08x, " % self.address
        rep += "length: %d)" % self.length

        return rep


class RomParseException(Exception):
    pass

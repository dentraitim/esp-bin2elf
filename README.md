### esp-bin2elf

Converts a flash dump from an esp8266 device into an ELF executable file for analysis and reverse engineering.

esp-bin2elf will create sections for each of the sections in the flash dump.  For convenience, esp-bin2elf also creates a flash section at 0x40200000 (**.irom0.text**) containing the SDK from flash, a section at 0x40000000 containing the bootrom (**.bootrom.text**), and includes all SDK symbols.

Tested in IDA Pro with the excellent [Xtensa processor plugin](https://github.com/themadinventor/ida-xtensa) from Fredrik Ahlberg.

Once you have your ELF loaded, you can + should leverage the [rizzo IDA plugin](https://github.com/devttys0/ida) to identify common functions from the SDK and RTOS examples.

Alternatively, the ELF can be used with [Radare2](https://rada.re/) and/or [Cutter](https://cutter.re/).

### Requirements:

- Python 3
- `elffile` - https://pypi.org/project/elffile/

The original `elffile` project seems abandoned, but a fork is available here: https://github.com/slorquet/elffile2

### Usage:

```python
import esp_bin2elf
import flash_layout

# Load image
flash_layout = flash_layout.layout_without_ota_updates
rom = esp_bin2elf.parse_rom('flashdump.bin', 'path/to/flashdump.bin', flash_layout)

print(rom)
for section in rom.sections:
    print(section)

# Generate ELF
section_names = esp_bin2elf.name_sections(rom)
elf = esp_bin2elf.convert_rom_to_elf(rom, section_names, 'flash_bin.elf')
```

Run the code and make sure things look ok.

### Feedback and issues:

Feel free to report an issue on github or contact me privately if you prefer.

### Thanks:

* Richard Burton for:
  * image format details: http://richard.burtons.org/2015/05/17/esp8266-boot-process/
  * rBoot: https://github.com/raburton/rboot
* Max Filippov (**jcmvbkbc**) for bootrom.bin: https://github.com/jcmvbkbc/esp-elf-rom
* Fredrik Ahlberg (**themadinventor**) for the IDA plugin and esptool.

### esp-bin2elf

Converts a flash dump from an esp8266 device into an ELF executable file for analysis and reverse engineering.

esp-bin2elf will create sections for each of the sections in the flash dump.  For convenience, esp-bin2elf also creates a flash section at 0x40200000 (**.irom0.text**) containing the SDK from flash, a section at 0x40000000 containing the bootrom (**.bootrom.text**), and includes all SDK symbols.

Tested in IDA Pro with the excellent [Xtensa processor plugin](https://github.com/themadinventor/ida-xtensa) from Fredrik Ahlberg.

Once you have your ELF loaded, you can + should leverage the [rizzo IDA plugin](https://github.com/devttys0/ida) to identify common functions from the SDK and RTOS examples.

Alternatively, the ELF can be used with [Radare2](https://rada.re/) and/or [Cutter](https://cutter.re/).

### Requirements:

- Python 3
- `esptool.py` - https://github.com/espressif/esptool
- `elffile` - https://pypi.org/project/elffile/

The original `elffile` project seems abandoned, but a fork is available here: https://github.com/slorquet/elffile2

### Usage:
#### Dump flash
- Connect usb cable to esp8266
```sh
./dump_flash.sh
```
- This will generate flash_4M.bin

#### Extract flash to user application and convert to elf file
```sh
./esp_extract_flash.sh flash_4M.bin out_user_irom.bin
```
- This will generate out_user_irom.bin (User Application), out_user_irom.bin.elf (Elf file)

### Feedback and issues:

Feel free to report an issue on github or contact me privately if you prefer.

### Thanks:

* Richard Burton for:
  * image format details: http://richard.burtons.org/2015/05/17/esp8266-boot-process/
  * rBoot: https://github.com/raburton/rboot
* Max Filippov (**jcmvbkbc**) for bootrom.bin: https://github.com/jcmvbkbc/esp-elf-rom
* Fredrik Ahlberg (**themadinventor**) for the IDA plugin and esptool.

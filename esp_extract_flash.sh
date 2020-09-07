#!/usr/bin/env bash
if [ -z "$1" ] || [ -z "$2" ]; then
  echo 'Usage:' $0' flash_dump.bin out_user_irom.bin'
  echo 'Will write user_irom from flash_dump.bin to out_user_irom.bin'
  exit 1
fi
echo 'Flash bin:' $1
esptool.py image_info "$1"

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

"${DIR}/image2user_bin.py" "$1" "$2"
echo -ne "\n\n\n"
echo '=================='
echo -ne "\n\n\n"
echo 'USER bin:' $2
esptool.py image_info "$2"
echo -ne "\n\n\n"
echo '=================='
echo -ne "\n\n\n"
echo 'USER elf:' $2.elf
"${DIR}/user_bin_to_elf.py" "$2"
echo -ne "\n\n\n"
file "$2".elf
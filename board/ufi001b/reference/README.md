# UFI001B reference inputs

This directory contains metadata extracted from the already bootable
HandsomeMod image. It intentionally does not contain the original boot image,
DTB, eMMC backup, or proprietary firmware.

Run `scripts/extract-reference-boot.py` against the local private boot image to
reproduce the metadata and, when needed, extract the appended DTB into a
temporary/private build directory.


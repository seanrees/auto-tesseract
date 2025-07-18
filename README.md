![build and tests](https://github.com/seanrees/auto-tesseract/actions/workflows/build.yml/badge.svg)

# auto-tesseract

## What

This is a Python3 service to detect (via Linux's inotify()) new PDFs in --in_dir, and
automatically rewrite them as searchable PDFs in --out_dir. This is particularly useful if,
for example, you have a scanner that outputs PDFs onto a fileserver (as we do :-)).

This program uses [Tesseract OCR](https://opensource.google/projects/tesseract)'s to produce
the text. This program also uses [ImageMagick](http://www.imagemagick.org) to convert the
original PDF to TIFF format, for use by Tesseract. In both cases, the program relies on the
command-line tools from these packages.

This package also depends on Linux's inotify() system call.

## Usage

This program has two main arguments: --in_dir and --out_dir. Any PDF copied or moved into
--in_dir will automatically trigger the process, and a searchable version of the PDF will
appear shortly in --out_dir. The original is untouched.

```sh
% ./auto_tesseract.py --in_dir=input --out_dir=output
```

This program will also backfill missing work. If there are files in the input directory that
_do not_ exist in the output directory, auto-tesseract will automatically OCR them immediately
upon startup.

## Build

This package is deployed with Docker, and the build is driven with the `Makefile`.

To build (, test, and lint) the `auto-tesseract:dev` tag:
```sh
% make
```

To build the "release" image, tagged as `auto-tesseract:latest`:
```sh
% make release
```

#!/usr/bin/env python3
# Author: Andrey Kolomatskiy
# 7/10/2021
# MIT license -- free to use as you want, cheers.

"""
Simple python wrapper script to use libreoffice function to convert doc(x) and ppt(x) to PDF files.

Dependency: Libreoffice.

On Linux install via command line:
sudo add-apt-repository ppa:libreoffice/ppa
sudo apt update
sudo apt install libreoffice
"""

import argparse
import subprocess
import os.path
import sys


def convert(conversion_type, input_file_path, output_dir):
    export_type = {
        'doc2pdf': 'pdf:writer_pdf_Export',
        'ppt2pdf': 'pdf:impress_pdf_Export',
    }
    
    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        raise Exception("Error: invalid path for input PDF file")
        sys.exit(1)

    # Check if file is a doc(x) or ppt(x) by extension
    if input_file_path.split('.')[-1].lower() not in ['doc', 'docx', 'ppt', 'pptx']:
        raise Exception("Error: Filetype is not supported")
        sys.exit(1)

    subprocess.call(['libreoffice', '--headless', '--convert-to', export_type[conversion_type],
                     input_file_path, '--outdir', output_dir]
    )
    

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input', help='Relative or absolute path of the input file')
    parser.add_argument('output', help='Relative or absolute path of the output directory')
    parser.add_argument('-c', '--convert', help='Conversion type: doc2pdf or ppt2pdf')
    args = parser.parse_args()

    # Run
    convert(conversion_type=args.convert, input_file_path=args.input, output_dir=args.output)

if __name__ == '__main__':
    main()
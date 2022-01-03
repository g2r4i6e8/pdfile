import os

from PyPDF2 import PdfFileMerger, PdfFileWriter, PdfFileReader
from PIL import Image
from zipfile import ZipFile
import re

from app.tools import libreoffice_converter, pdf_compressor


# invalid format checker
def check_invalid_format(file_name, function):
    format_functions = {'compress': ['pdf'], 'merge': ['pdf'], 'split': ['pdf'],
                        'delete': ['pdf'], 'ppt2pdf': ['ppt', 'pptx', 'odp'],
                        'img2pdf': ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'WebP', 'bmp'],
                        'doc2pdf': ['odt', 'doc', 'docx']}
    if file_name.split('.')[-1].lower() not in format_functions[function]:
        return True, format_functions[function]
    else:
        return False, format_functions[function]


# basic function to create range from string
def create_range(x, num_of_pages):
    result = []
    for part in x.split(','):
        if '-' in part or ':' in part:
            a, b = re.split('[-:]', part)
            if b == '': b = num_of_pages
            a, b = int(a), int(b)
            result.extend(range(a, b + 1))
        else:
            a = int(part)
            result.append(a)
    return result


# compress document(s)
def compress(list_of_files, output_folder):
    if len(list_of_files) > 1:
        output_path = os.path.join(output_folder, 'documents_compressed.zip')
        zipObj = ZipFile(output_path, 'w')
        for file_path in list_of_files:
            fname = os.path.join(os.path.basename(file_path).replace('.pdf', ''))
            filename = os.path.join('{}_compressed.pdf'.format(fname))
            pdf_compressor.compress(file_path, os.path.join(output_folder, filename))
            zipObj.write(os.path.join(output_folder, filename), filename)
            os.remove(os.path.join(output_folder, filename))
        zipObj.close()

    elif len(list_of_files) == 1:
        file_path = list_of_files[0]
        fname = os.path.join(os.path.basename(file_path).replace('.pdf', ''))
        output_path = os.path.join(output_folder, '{}_compressed.pdf'.format(fname))
        try:
            pdf_compressor.compress(file_path, output_path)
        except:
            return None

    return output_path


# merge multiple documents into one
def merge(list_of_files, output_folder):
    merger = PdfFileMerger()
    for file_path in list_of_files:
        input_file = open(file_path, 'rb')
        pdf_reader = PdfFileReader(input_file, strict=False)
        merger.append(pdf_reader)
    output_path = os.path.join(output_folder, 'document_merged.pdf')
    with open(output_path, 'wb') as outputStream:
        merger.write(outputStream)
    return output_path


# split pdf document into one or into separate files page by page
def split(file_path, split_range_string, output_folder, separate_pages=False):
    input_file = open(file_path, 'rb')
    pdf_reader = PdfFileReader(input_file, strict=False)
    split_range = create_range(split_range_string, pdf_reader.getNumPages())
    fname = os.path.join(os.path.basename(file_path).replace('.pdf', ''))
    if separate_pages:
        output_path = os.path.join(output_folder, '{}-pages_{}.zip'.format(fname, split_range_string))
        zipObj = ZipFile(output_path, 'w')
        for i in split_range:
            splitter = PdfFileWriter()
            splitter.addPage(pdf_reader.getPage(i - 1))
            filename = os.path.join('{}-page_{}.pdf'.format(fname, i))
            with open(os.path.join(output_folder, filename), 'wb') as outputStream:
                splitter.write(outputStream)
            zipObj.write(os.path.join(output_folder, filename), filename)
            os.remove(os.path.join(output_folder, filename))
        zipObj.close()
        input_file.close()
        return output_path
    else:
        output_path = os.path.join(output_folder, '{}-pages_{}.pdf'.format(fname, split_range_string))
        splitter = PdfFileWriter()
        for i in split_range:
            splitter.addPage(pdf_reader.getPage(i - 1))
        with open(output_path, 'wb') as outputStream:
            splitter.write(outputStream)
        input_file.close()
        return output_path


# convert image(s) to pdf
def img2pdf(list_of_files, output_folder):
    output_path = os.path.join(output_folder, 'document_fromImages.pdf')
    list_of_images = []
    for file_path in list_of_files:
        image = Image.open(file_path).convert('RGB')
        list_of_images.append(image)
    list_of_images[0].save(output_path, save_all=True, resolution=100.0, append_images=list_of_images[1:])
    return output_path


# delete pages from pdf
def delete(file_path, delete_range_string, output_folder):
    input_file = open(file_path, 'rb')
    pdf_reader = PdfFileReader(input_file, strict=False)
    pages_to_delete = create_range(delete_range_string, pdf_reader.getNumPages())
    pages_to_keep = [p for p in range(pdf_reader.getNumPages()) if p + 1 not in pages_to_delete]
    keeper = PdfFileWriter()
    fname = os.path.join(os.path.basename(file_path).replace('.pdf', ''))
    output_path = os.path.join(output_folder, '{}-without_{}.pdf'.format(fname, delete_range_string))
    for i in pages_to_keep:
        keeper.addPage(pdf_reader.getPage(i))
    with open(output_path, 'wb') as outputStream:
        keeper.write(outputStream)
    input_file.close()
    return output_path


# convert doc(x) to pdf
def doc2pdf(list_of_files, output_folder):
    if len(list_of_files) > 1:
        output_path = os.path.join(output_folder, 'documents_one-by-one.zip')
        zipObj = ZipFile(output_path, 'w')
        for file_path in list_of_files:
            fname = os.path.join(os.path.basename(file_path))
            filename = '{}.pdf'.format(''.join(fname.split('.')[:-1]))
            libreoffice_converter.convert('doc2pdf', file_path, output_folder)
            zipObj.write(os.path.join(output_folder, filename), filename)
            os.remove(os.path.join(output_folder, filename))
        zipObj.close()

    elif len(list_of_files) == 1:
        file_path = list_of_files[0]
        fname = os.path.join(os.path.basename(file_path))
        filename = '{}.pdf'.format(''.join(fname.split('.')[:-1]))
        output_path = os.path.join(output_folder, filename)
        try:
            libreoffice_converter.convert('doc2pdf', file_path, output_folder)
        except:
            return None
    return output_path


# convert ppt(x) to pdf
def ppt2pdf(list_of_files, output_folder):
    if len(list_of_files) > 1:
        output_path = os.path.join(output_folder, 'documents_one-by-one.zip')
        zipObj = ZipFile(output_path, 'w')
        for file_path in list_of_files:
            fname = os.path.join(os.path.basename(file_path))
            filename = '{}.pdf'.format(''.join(fname.split('.')[:-1]))
            libreoffice_converter.convert('ppt2pdf', file_path, output_folder)
            zipObj.write(os.path.join(output_folder, filename), filename)
            os.remove(os.path.join(output_folder, filename))
        zipObj.close()

    elif len(list_of_files) == 1:
        file_path = list_of_files[0]
        fname = os.path.join(os.path.basename(file_path))
        filename = '{}.pdf'.format(''.join(fname.split('.')[:-1]))
        output_path = os.path.join(output_folder, filename)
        try:
            libreoffice_converter.convert('ppt2pdf', file_path, output_folder)
        except:
            return None
    return output_path

"""
Created on Wed Sep 29 12:21:01 2021

@author: kolomatskiy
"""

import os
from pdfile import tools



def run_tests():
    #test merge
    list_of_files = ['test_files/SML-LX23YC-TR-1.pdf', 'test_files/SML-LX23YC-TR-2.pdf']
    output_folder = os.path.join('test_results')
    os.makedirs('test_results', exist_ok=True)
    output_path = tools.merge(list_of_files, output_folder)
    if os.path.isfile(output_path):
        print('Merged successfully')
    else:
        print('Files are not merged. Something went wrong')
        
    #test split range in one file
    FILE_PATH = 'test_files/OHCHRreport2020.pdf'
    split_range = '1, 403-405'
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.split(FILE_PATH, split_range, output_folder)
    if os.path.isfile(output_path):
        print('Splitted in one file successfully')
    else:
        print('File is not splitted. Something went wrong')
    
    #test split range in separate files
    FILE_PATH = 'test_files/OHCHRreport2020.pdf'
    split_range = '1, 403-405'
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.split(FILE_PATH, split_range, output_folder, separate_pages = True)
    if os.path.isfile(output_path):
        print('Splitted in separate files successfully')
    else:
        print('File is not splitted. Something went wrong')
    
    #test convert images to pdf
    list_of_files = ['test_files/HPIM0899.JPG', 'test_files/HPIM0948.JPG', 'test_files/HPIM3205.JPG']
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.img2pdf(list_of_files, output_folder)
    if os.path.isfile(output_path):
        print('Image(s) converted to pdf successfully')
    else:
        print('Something went wrong converting image(s) to pdf')
        
    #test delete pages from pdf
    FILE_PATH = 'test_files/OHCHRreport2020.pdf'
    split_range = '220-'
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.delete(FILE_PATH, split_range, output_folder)
    if os.path.isfile(output_path):
        print('Page(s) deleted successfully')
    else:
        print('Page(s) are not deleted. Something went wrong')
    
    #test compress one file
    list_of_files = ['test_files/OHCHRreport2020.pdf']
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.compress(list_of_files, output_folder)
    if os.path.isfile(output_path):
        print('File compressed successfully')
    else:
        print('File is not compressed. Something went wrong')
        
    #test compress multiple files
    list_of_files = ['test_files/OHCHRreport2020.pdf']
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.compress(list_of_files, output_folder)
    if os.path.isfile(output_path):
        print('Files compressed successfully')
    else:
        print('Files are not compressed. Something went wrong')
        
    #test convert single doc to pdf
    list_of_files = ['test_files/OHCHRreport2020.pdf']
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.doc2pdf(list_of_files, output_folder)
    if os.path.isfile(output_path):
        print('File compressed successfully')
    else:
        print('File is not compressed. Something went wrong')
        
    #test convert multiple docs in separate files
    list_of_files = ['test_files/OHCHRreport2020.pdf']
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.doc2pdf(list_of_files, output_folder, separate_files = False)
    if os.path.isfile(output_path):
        print('File compressed successfully')
    else:
        print('File is not compressed. Something went wrong')
        
    #test convert single doc to pdf
    list_of_files = ['test_files/OHCHRreport2020.pdf']
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.ppt2pdf(list_of_files, output_folder)
    if os.path.isfile(output_path):
        print('File compressed successfully')
    else:
        print('File is not compressed. Something went wrong')
        
    #test convert multiple docs in separate files
    list_of_files = ['test_files/OHCHRreport2020.pdf']
    output_folder = os.path.join('test_results')
    os.makedirs(output_folder, exist_ok=True)
    output_path = tools.ppt2pdf(list_of_files, output_folder, separate_files = False)
    if os.path.isfile(output_path):
        print('File compressed successfully')
    else:
        print('File is not compressed. Something went wrong')


if __name__ == '__main__':
    run_tests()
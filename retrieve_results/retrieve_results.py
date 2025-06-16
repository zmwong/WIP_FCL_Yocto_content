import os
import subprocess
import socket
import time
import copy_result_files
import re

## Overall Process flow:
## Host: host_fetch_results.py  --> SUT: interfacer_stuff.py --> SUT: obtain_file_details --> return to host_fetch_results.py


def count_0B_after_summary(file_path):
    # Extract the portion after "RESULT SUMMARY"
    with open(file_path, 'r') as file:
        content = file.read()
    summary_start = content.find("# RESULT SUMMARY")
    if summary_start == -1:
        return -1

    summary_text = content[summary_start:]
    # Count occurrences of "0B"
    count_0B = len(re.findall(r'\b0B\b', summary_text))
    return count_0B


def search_string_in_file(file_path, string_to_search, string_to_fail, test_type):
    """Return True if the string is found in the file, else return False."""
    completed_loops = 0
    with open(file_path, 'r') as read_obj:
    
        # if 3dmark
        if test_type == 1:
            for line in read_obj:
                if string_to_fail in line:
                    return 'Fail '+str(completed_loops)+'/9'
                elif string_to_search in line:
                    completed_loops += 1
            if completed_loops >= 9:
                return 'Pass'
            return 'Fail '+str(completed_loops)+'/9'
            
        # if memrunner - check for 0B failure
        if test_type == 2:
            ZeroBytesCount = count_0B_after_summary(file_path)
            if ZeroBytesCount >= 1:
                return 'ZeroBytes'
            elif ZeroBytesCount < 0:
                return 'DNF'
            for line in read_obj:
                if string_to_fail in line:
                    return 'Fail'
                elif string_to_search in line:
                    return 'Pass'
       
       # if solar
        if test_type == 3:
            for line in read_obj:
                if string_to_fail in line:
                    return 'Fail'
                elif string_to_search in line:
                    return 'Pass'
    return 'Fail'

platform_name = socket.gethostname()
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)

# Fetch latest files details
f1_name, f2_name, f3_name, file1_dt, file2_dt, file3_dt = copy_result_files.main()
time.sleep(2)

file1_date = file1_dt[:-9]
file2_date = file2_dt[:-9]
file3_date = file3_dt[:-9]

file1_time = file1_dt[11:]
file2_time = file2_dt[11:]
file3_time = file3_dt[11:]

print(f"\n\n==================\nSampled log files\n==================\n3DMark - {f1_name} {file1_date} {file1_time}")
print(f"Memrunner - {f2_name} {file2_date} {file2_time}")
print(f"Solar - {f3_name} {file3_date} {file3_time}")

# relies on 18/18 detection
file_path = f'{script_dir}\Latest_Results\{f1_name}'
string_to_search = 'Benchmark completed.'
string_to_fail = 'benchmark ended in error, exiting'
ThreeDMark_result = search_string_in_file(file_path, string_to_search, string_to_fail, test_type = 1)

# How to cover for 0 bytes issue?
file_path = f'{script_dir}\Latest_Results\{f2_name}'
string_to_search = '| Data Corruptions        |           0 |           0           0           0           0           0           0           0|'
string_to_fail = 'FAILED'
Memrunner_result = search_string_in_file(file_path, string_to_search, string_to_fail, test_type = 2)

# Will detect Hang
file_path = f'{script_dir}\Latest_Results\{f3_name}'
string_to_search = 'SAGV finished with result: Pass EC: 0x0'
string_to_fail = 'Unexpected Hang'
Solar_result = search_string_in_file(file_path, string_to_search, string_to_fail, test_type = 3)

#os.remove(f'{script_dir}\\temp.txt')
print(f"\n===========================\nResults for {platform_name}\n===========================\n3DMark: {ThreeDMark_result}\nMemrunner: {Memrunner_result}\nSolar: {Solar_result}")
cmd = r'powershell -Command "Get-CimInstance -ClassName Win32_PhysicalMemory | Select-Object DeviceLocator, Capacity, Manufacturer, PartNumber, Speed, DataWidth, SerialNumber"'
#wmic memorychip get Devicelocator, Capacity, Manufacturer, PartNumber, Speed, DataWidth, SerialNumber
dimm_details = subprocess.check_output(cmd, shell=True)
dimm_details = dimm_details.decode("utf-8")

print(f"\n\n\n#################################################################################################\n{dimm_details}")

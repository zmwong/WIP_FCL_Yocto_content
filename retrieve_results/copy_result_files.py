import os
import subprocess
import socket
import time
import shutil
from datetime import datetime

def main():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    TempFile_path = os.path.join(script_directory, 'temp.txt')
    folder_path = os.path.join(script_directory, 'Latest_Results')

    if os.path.isfile(TempFile_path):
        os.remove(TempFile_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Directory 'Latest_Results' created")
    else:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"Deleted {filename}")

    print(f"\n\n")            
    # Directories of log files are located
    logDirectory1=r"C:\validation\windows-test-content\memory\mtl_s\Log\3DMark"
    logDirectory2=r"C:\validation\windows-test-content\memory\mtl_s\Log\Memrunner"
    logDirectory3=r"C:\validation\windows-test-content\memory\mtl_s\Log\Solar"

    # Look for specific file names
    #targetString1=r"_firestrike_extreme"
    targetString1=r"_timespy_performance"
    targetString2=r"memrunner_20"
    targetString3=r".csv"  

    file_names = []
    timestamps = []
    
    for filename in os.listdir(logDirectory1):
        if targetString1 in filename:
            source_file_path = os.path.join(logDirectory1, filename)
            destination_file_path = os.path.join(folder_path, filename)
            mod_time = os.path.getmtime(source_file_path)
            readable_time = datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S')
            file_names.append(filename)
            timestamps.append(readable_time)    
            shutil.copy(source_file_path, destination_file_path)
            print(f"\n{filename}: Last modified on {readable_time}")
            print(f"Copied '{filename}' to \n'{folder_path}'")
        
    for filename in os.listdir(logDirectory2):
        if targetString2 in filename and 'thread' not in filename:
            source_file_path = os.path.join(logDirectory2, filename)
            destination_file_path = os.path.join(folder_path, filename)
            mod_time = os.path.getmtime(source_file_path)
            readable_time = datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S')
            file_names.append(filename)
            timestamps.append(readable_time)    
            shutil.copy(source_file_path, destination_file_path)
            print(f"\n{filename}: Last modified on {readable_time}")
            print(f"Copied '{filename}' to \n'{folder_path}'")
        
    for filename in os.listdir(logDirectory3):
        if targetString3 in filename and 'html' not in filename and 'json' not in filename:
            source_file_path = os.path.join(logDirectory3, filename)
            destination_file_path = os.path.join(folder_path, filename)
            mod_time = os.path.getmtime(source_file_path)
            readable_time = datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S')
            file_names.append(filename)
            timestamps.append(readable_time)    
            shutil.copy(source_file_path, destination_file_path)
            print(f"\n{filename}: Last modified on {readable_time}")
            print(f"Copied '{filename}' to \n'{folder_path}'\n\n")
                   
    file_name1, file_name2, file_name3 = file_names[:3]
    timestamp1, timestamp2, timestamp3 = timestamps[:3]
    return file_name1, file_name2, file_name3, timestamp1, timestamp2, timestamp3


if __name__ == "__main__":
    x = main()
    print(x)

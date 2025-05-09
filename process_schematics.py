#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil

def process_schematic(filename, use_libname):
    """Processes a single schematic file and puts the PDF in the 'pdf' directory."""
    try:
        print(f"Processing: {filename}")

        # Extract desired name portion
        comma_count = filename.count(',')
        if comma_count >= 2:
            name_parts = filename.split(',')
            pdf_name = name_parts[1]
        else:
            pdf_name = os.path.splitext(filename)[0]  # Use original filename without extension

        # Rename the file to temp_filename
        temp_filename = "tempfile"
        shutil.copyfile(filename, temp_filename)

        # eps2eps
        process = subprocess.Popen(["eps2eps", temp_filename, f"{temp_filename}.eps"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, "eps2eps", stderr)
        temp_filename = f"{temp_filename}.eps" # Change filename for subsequent calls.

        # epstool --bbox --copy
        process = subprocess.Popen(["epstool", "--bbox", "--copy", temp_filename, "temp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, "epstool", stderr)

        # mv temp <temp_filename>
        process = subprocess.Popen(["mv", "temp", temp_filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, "mv", stderr)

        # epstopdf
        os.makedirs("pdf", exist_ok=True) # Create 'pdf' directory if it doesn't exist.
        process = subprocess.Popen(["epstopdf", temp_filename, f"pdf/{pdf_name}.pdf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, "epstopdf", stderr)

        os.remove(temp_filename) #remove tempfile

        print(f"Processed: {filename}")

    except subprocess.CalledProcessError as e:
        print(f"Error processing {filename}: {e}")
        if e.stderr:
            print(f"Standard Error:\n{e.stderr.decode()}")
        else:
            print("Standard error was empty.")
    except FileNotFoundError as e:
        print(f"Error: Required tool not found: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    use_libname = "-uselibname" in sys.argv

    if use_libname:
        sys.argv.remove("-uselibname") #remove flag from list of args

    # Check for remaining arguments after removing flags
    if len(sys.argv) > 1:
        # Process a single file from the command line argument
        filename = sys.argv[1]
        if os.path.isfile(filename) and not filename.endswith((".py", ".pdf", ".swp")) and not filename.startswith(".") and filename != "tempfile":
            process_schematic(filename, use_libname)
        else:
            if not os.path.isfile(filename):
                print(f"Error: File '{filename}' not found.")
            else:
                print(f"Error: File '{filename}' is excluded.")
    else:
        # Process all files in the current directory, excluding specified files
        for filename in os.listdir():
            if os.path.isfile(filename) and not filename.endswith((".py", ".pdf", ".swp")) and not filename.startswith(".") and filename != "tempfile":
                process_schematic(filename, use_libname)
        os.remove("tempfile")


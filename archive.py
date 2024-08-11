import sys
import os
import string

import time

class Database:
    # function to create type(aka relation)
    def create_type(self, type_name, num_fields, primary_key_index, *fields):
        # create field dictionary from the input with fields and their types
        field_dict = {fields[i]: fields[i + 1] for i in range(0, len(fields), 2)}
        
        # create the type folder if it doesn't exist
        if not os.path.exists(type_name):
            os.makedirs(type_name)
            # create pages under the type folder with <type_name>....txt
            # create pages with the letters of English alphabet(a-z) for str primary keys
            for i in string.ascii_lowercase:
                # create 2 pages per letter 
                for j in range(1, 3):
                    filename = f"{type_name}/{type_name}{i}{j}.txt"
                    with open(filename, 'w') as f:
                        # initialize the page header with type name , current records of the page, primary key index
                        f.write(f"{type_name} 0 {primary_key_index} \n")

            # create pages with the numbers (0-9) for int primary keys
            for k in range(10):
                # create 2 pages per number
                for l in range(1, 3):
                    filename = f"{type_name}/{type_name}{k}{l}.txt"
                    with open(filename, 'w') as f:
                        # initialize the page header with type name , current records of the page, primary key index
                        f.write(f"{type_name} 0 {primary_key_index}\n")
            # create log.txt after the first run
            with open('log.txt', 'a') as log_file:
                log_file.write(f"{int(time.time())}, create type {type_name} {num_fields} {primary_key_index} {' '.join(fields)}, success\n")
            return True
        
        else:
            with open('log.txt', 'a') as log_file:
                log_file.write(f"{int(time.time())}, create type {type_name} {num_fields} {primary_key_index} {' '.join(fields)}, failure\n")


    # function to create record
    def create_record(self, type_name, *values):
        type_folder = os.path.join(os.getcwd(), type_name)

        primary_key_index = None
        # get the primary key index from page header of the first file in the folder (primary key index is the same for all pages in a type)
        first_file = next(iter(os.listdir(type_folder)), None)
        if first_file:
            # Construct the path to the first file
            first_file_path = os.path.join(type_folder, first_file)
            # read the header to get the primary key index
            with open(first_file_path, 'r') as f:
                header = f.readline().strip().split()
                if len(header) == 3 and header[0] == type_name:
                    primary_key_index = int(header[2])

        if primary_key_index is None:
            with open('log.txt', 'a') as log_file:
                log_file.write(f"{int(time.time())}, create record {type_name} {' '.join(values)}, failure\n")
            return False
        # get the primary key
        primary_key = values[primary_key_index - 1]  

        # determine the correct file based on the primary key's first character
        # if the first char is a digit, place under <type_name>[0-9][1-2].txt
        if primary_key[0].isdigit():
            first_char = primary_key[0]
            file_prefixes = [f"{type_name}{first_char}{j}" for j in range(1, 3)]
        else:
            first_char = primary_key[0].lower()
            file_prefixes = [f"{type_name}{first_char}{j}" for j in range(1, 3)]

        # check the previously existing primary keys in the page
        # !!!! here we only check corresponding pages beginning with the same char of the primary key !!!!
        for prefix in file_prefixes:
            filename = os.path.join(type_folder, f"{prefix}.txt")
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    lines = f.readlines()[1:]  
                    existing_primary_keys = [line.strip().split()[primary_key_index - 1] for line in lines]
                    # if the primary key already exists in the table, it is a failure (duplicate primary key in a table is not allowed)
                    if primary_key in existing_primary_keys:
                        with open('log.txt', 'a') as log_file:
                            log_file.write(f"{int(time.time())}, create record {type_name} {' '.join(values)}, failure\n")
                        return False

        # add the record to the appropriate file
        for prefix in file_prefixes:
            filename = os.path.join(type_folder, f"{prefix}.txt")
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write(f"{type_name} 0 {primary_key_index}\n")

            # read the header of the page to get the current number of lines and check for primary key
            with open(filename, 'r') as f:
                lines = f.readlines()
                header = lines[0].strip().split()
                num_lines = int(header[1])
                existing_primary_keys = [line.split(" ")[primary_key_index - 1] for line in lines[1:]]

            if primary_key in existing_primary_keys:
                with open('log.txt', 'a') as log_file:
                    log_file.write(f"{int(time.time())}, create record {type_name} {' '.join(values)}, failure\n")
                return False

            # check if the page is full (including 10 records)
            if num_lines >= 10:
                continue

            # write the new record to the page and update the page header
            lines.append(' '.join(values) + '\n')
            lines[0] = f"{type_name} {num_lines + 1} {primary_key_index}\n"  

            with open(filename, 'w') as f:
                f.writelines(lines)

            # log success
            with open('log.txt', 'a') as log_file:
                log_file.write(f"{int(time.time())}, create record {type_name} {' '.join(values)}, success\n")
            return True

        # If all files are full or primary key already exists in all files
        with open('log.txt', 'a') as log_file:
            log_file.write(f"{int(time.time())}, create record {type_name} {' '.join(values)}, failure\n")
        return False
    
    # function to delete the record
    def delete_record(self, type_name, primary_key):
        type_folder = os.path.join(os.getcwd(), type_name)
        if not os.path.exists(type_folder):
            with open('log.txt', 'a') as log_file:
                log_file.write(f"{int(time.time())}, delete record {type_name} {primary_key}, failure\n")
            return False

        primary_key_index = None
        # get the primary key index from the first file in the type folder
        first_file = next(iter(os.listdir(type_folder)), None)
        if first_file:
            first_file_path = os.path.join(type_folder, first_file)
            # read the header of the first file to get the primary key index
            with open(first_file_path, 'r') as f:
                header = f.readline().strip().split()
                if len(header) == 3 and header[0] == type_name:
                    primary_key_index = int(header[2])

        if primary_key_index is None:
            with open('log.txt', 'a') as log_file:
                log_file.write(f"{int(time.time())}, delete record {type_name} {primary_key}, failure\n")
            return False

        # determine the correct file prefixes based on the primary key
        if primary_key[0].isdigit():
            first_char = primary_key[0]
            file_prefixes = [f"{type_name}{first_char}{j}" for j in range(1, 3)]
        else:
            first_char = primary_key[0].lower()
            file_prefixes = [f"{type_name}{first_char}{j}" for j in range(1, 3)]

        record_found = False

        for prefix in file_prefixes:
            filename = os.path.join(type_folder, f"{prefix}.txt")
            if not os.path.exists(filename):
                continue

            with open(filename, 'r+') as f:
                lines = f.readlines()

                # read the page header
                header = lines[0].strip().split()
                num_lines = int(header[1])

                # check if the record is present in the type
                for i, line in enumerate(lines[1:], 1):
                    fields = line.strip().split(" ")
                    if fields[primary_key_index - 1] == primary_key:
                        record_found = True
                        del lines[i]
                        break

                if record_found:
                    # update the header with the new number of lines
                    lines[0] = f"{type_name} {num_lines - 1} {primary_key_index}\n"
                    
                    # write the updated lines back to the file
                    f.seek(0)
                    f.writelines(lines)
                    f.truncate()

                    # Log success
                    with open('log.txt', 'a') as log_file:
                        log_file.write(f"{int(time.time())}, delete record {type_name} {primary_key}, success\n")
                    return True

        # If the record was not found in any of the files, return and log failure
        with open('log.txt', 'a') as log_file:
            log_file.write(f"{int(time.time())}, delete record {type_name} {primary_key}, failure\n")
        return False

    # function to search record
    def search_record(self, type_name, primary_key):
        type_folder = os.path.join(os.getcwd(), type_name)

        if not os.path.exists(type_folder):
            with open('log.txt', 'a') as log_file:
                log_file.write(f"{int(time.time())}, search record {type_name} {primary_key}, failure\n")
            return False

        primary_key_index = None
        # get the primary key index from the first file in the type folder
        first_file = next(iter(os.listdir(type_folder)), None)
        if first_file:
            
            first_file_path = os.path.join(type_folder, first_file)
            # read the header of the first file to get the primary key index
            with open(first_file_path, 'r') as f:
                header = f.readline().strip().split()
                if len(header) == 3 and header[0] == type_name:
                    primary_key_index = int(header[2])

        if primary_key_index is None:
            with open('log.txt', 'a') as log_file:
                log_file.write(f"{int(time.time())}, search record {type_name} {primary_key}, failure\n")
            return False

        # determine the correct file prefixes based on the primary key
        if primary_key[0].isdigit():
            first_char = primary_key[0]
            file_prefixes = [f"{type_name}{first_char}{j}" for j in range(1, 3)]
        else:
            first_char = primary_key[0].lower()
            file_prefixes = [f"{type_name}{first_char}{j}" for j in range(1, 3)]

        for prefix in file_prefixes:
            filename = os.path.join(type_folder, f"{prefix}.txt")
            if not os.path.exists(filename):
                continue

            with open(filename, 'r') as f:
                lines = f.readlines()

            for line in lines[1:]: 
                fields = line.strip().split()
                if fields[primary_key_index - 1] == primary_key:
                    with open('output.txt', 'a+') as out:
                        out.write(line)
                    
                    # Log success
                    with open('log.txt', 'a') as log_file:
                        log_file.write(f"{int(time.time())}, search record {type_name} {primary_key}, success\n")
                    return True

        # If the record was not found in any of the files, log failure
        with open('log.txt', 'a') as log_file:
            log_file.write(f"{int(time.time())}, search record {type_name} {primary_key}, failure\n")
        return False



def main():
    if os.path.exists('output.txt'):
        with open('output.txt', 'w') as out:
            pass

    if len(sys.argv) != 2:
        print("Usage: python3 archive.py <input.txt_path>")
        return

    input_file_path = sys.argv[1]

    db = Database()

    # read the input file line by line
    with open(input_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            command = parts[0]
            # split the command according to the input format given in the description
            if command == "create" and parts[1] == "type":
                type_name = parts[2]
                num_fields = int(parts[3])
                primary_key_index = int(parts[4])
                fields = parts[5:5 + num_fields * 2]
                db.create_type(type_name, num_fields, primary_key_index, *fields)
            elif command == "create" and parts[1] == "record":
                type_name = parts[2]
                values = parts[3:]
                db.create_record(type_name, *values)
            elif command == "delete" and parts[1] == "record":
                type_name = parts[2]
                primary_key = parts[3]
                db.delete_record(type_name, primary_key)
            elif command == "search" and parts[1] == "record":
                type_name = parts[2]
                primary_key = parts[3]
                db.search_record(type_name, primary_key)
            else:
                print(f"Unknown command: {line}")

if __name__ == "__main__":
    main()

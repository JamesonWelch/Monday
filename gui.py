def print_source_code():
    def file_selection(file_loc):
        with open(file_loc, "r") as f:
            files = f.read().splitlines()
        return files

    for line in file_selection("redundancies/monday_copy.py"):
        print(line.strip())
        time.sleep(.15)
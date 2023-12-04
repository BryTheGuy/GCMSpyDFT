import re

import molecule


def combine_lines(line1: str, line2: str):
    match = re.search(r"\d{2,}", line1)  # find end of molecule name on line one
    mol_start: str = line1[:match.start()].lstrip().replace("  ", " ")
    trail: str = line1[match.start():]
    return mol_start + line2.strip() + "  " + trail


def check_next_line(line1: str, line2: str):
    return line2 == line1


def find_cas_molecule(line: str):
    if "(CAS)" in line:  # found "(CAS)" molecule
        mol_id = line[:line.find(" (CAS)")].strip()
    elif "$$" in line:  # incase " (CAS)" isn't found. Should never execute
        mol_id = line[:line.find(" $$")].strip()
    else:
        return False
    return mol_id


def find_single_line_mol(line: str):
    if match := re.search(r"\d{2,}", line):  # only one molecule name proposed
        return line[:match.start()].strip()
    else:
        return False


def guess_parser(lines: list):
    """
    Collects all guesses into a list.

    :param lines: Lines of a peak
    :return: A list of guessed molecule names in one guess
    """
    while lines:
        current_line = lines.pop()
        cas_line_length = len(lines[0])
        guesses = []
        while len(lines):
            guesses.append(current_line)
            current_line = lines.pop(0)
            if len(current_line) != cas_line_length:
                continue
            else:
                lines.insert(0, current_line)
                break
        return guesses
    return []


def guess_agg(lines):
    guesses = []
    while lines:
        guesses.append(guess_parser(lines))
    return guesses


class Peak:
    peak_num: int
    retention_time: float
    percent_area: float
    library: str
    ID: list[list[str]]         # list of proposed molecule names per reference number
    molecules: list[molecule]   # accepted molecules and their structures
    reference_num: list[int]    # list of all reference numbers in peak
    cas_num: list[int]          # list of all CAS numbers in peak
    quality: list[int]          # list of all qualities in peak

    def trailing_values(self, line: str):
        if match := re.search(r"\d{2,}", line):  # only one molecule name proposed
            (self.reference_num,
             self.cas_num,
             self.quality) = line[match.start():].split()
            return True
        else:
            return False

    def peak_header(self, block: list[str]):
        peak_line = block.pop(0)
        (self.peak_num,
         self.retention_time,
         self.percent_area,
         self.library) = peak_line.split()


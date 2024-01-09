from io import TextIOWrapper
from pprint import pprint


def read_to_list(input_file: TextIOWrapper) -> list:
    """  Reads a file to a list and returns the list.  """
    # lines: list
    # with open(input_file) as f:
    #     lines = f.read().splitlines()
    lines = input_file.read().splitlines()
    return lines


def content_finder(lines: list, sep: str = "___") -> int:
    """  Scans list for a separator line and returns the index or -1 of not found.  """
    for line in lines:
        if sep in line:
            return lines.index(line)
    return -1


def trim_header(lines: list, sep_index: int) -> list:
    """  Removes sep_index lines from head of list and returns a new list.  """
    if sep_index < 0:
        raise IndexError("Make sure file contains header.")
    return lines[sep_index + 1:]


def is_peak_line(line: str) -> bool:  # TODO: Make more robust
    """  Checks if second char is a digit and returns the bool.  """
    if len(line) > 2:
        return line[2].isdigit()
    else:
        return False


def peak_blocker(lines: list) -> list[str]:
    """
    Collects all lines in a peak into a list.

    :param lines: Lines to read from to create a peak block.
    :return: A list of lines in one peak.
    """
    while lines:
        current_line = lines.pop(0)
        if is_peak_line(current_line):  # *Should* be always true
            peak = []
            while len(lines):
                peak.append(current_line)
                current_line = lines.pop(0)
                if not is_peak_line(current_line):
                    continue
                else:
                    lines.insert(0, current_line)
                    break
            return peak
    return []


def peak_agg(lines: list) -> list[list[str]]:  # TODO: Might switch to a recursive
    """
    Collects peak blocks into a list.

    :param lines: Lines to read from to create list of blocks.
    :return: List of peak block lists.
    """
    blocks = []
    while lines:
        blocks.append(peak_blocker(lines))
    return blocks


if __name__ == '__main__':
    read_lines = read_to_list("test/test_file.txt")
    trimmed_lines = trim_header(read_lines, content_finder(read_lines))
    # peak_blocks = peak_blocker(trimmed_lines)
    peak_blocks = peak_agg(trimmed_lines)

    pprint(peak_blocks)

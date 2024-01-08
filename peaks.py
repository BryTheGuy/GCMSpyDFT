import logging
import re
from typing import Callable

# import molecule
from config import cfg

peak_logger = logging.getLogger('GCMSpyDFT.peak')


class Peak:
    def __init__(self, peak_lines: list[str]):
        """
        Uses a list of lines that should represent a GC-MS peak to initialize the class.

        :param peak_lines: List of lines in the peak.
        """
        self.logger = logging.getLogger('GCMSpyDFT.peak.Peak')
        self.logger.info('Creating new peak instance.')

        self.peak_block = peak_lines         # list of all lines in peak
        self.peak_num: int = 0              # position of peak
        self.retention_time: float = 0.0    # retention time of peak
        self.percent_area: float = 0.0      # percent area of peak
        self.library: str = ''              # Library used for peak
        self.possible_IDs: int = 0          # total number of guess made in peak
        self.ID: list[str] = []             # list of unique proposed molecule names in peak
        self.reference_nums: list[int] = []  # list of all reference numbers in peak
        self.cas_nums: list[int] = []        # list of all CAS numbers in peak
        self.qualities: list[int] = []        # list of all qualities in peak

    def __str__(self) -> str:
        """
        The string representation of the class, excluding the values of peak_block and logger.

        :return: string key and values of class attributes.
        """
        return str(self.__class__) + '\n' + '\n'.join(
            f'{item} = {self.__dict__[item]}'
            if item not in ['peak_block', 'logger'] else item
            for item in self.__dict__)

    def peak_header(self) -> None:
        """
        Looks at first line of peak and parses 'PK#', 'RT', 'Area%', and 'Library' into
        peak_num, retention_time, percent_area, and library class attributes.
        """
        block = self.peak_block
        pn, rt, pa, lib = block[0].split()
        self.peak_num = int(pn)
        self.retention_time = float(rt)
        self.percent_area = float(pa)
        self.library = lib

    def left_align(self) -> None:
        """
        Tries to strip leading whitespace for all lines until char position at the end of Area%.
        This is to try and preserve spaces on lines with a space in molecule names appears at the start of the line.
        """
        block = self.peak_block
        # could add logic for cfg.mol_id_start
        _pn, _rt, percent_area, _lib = block[0].split()
        line_indent = block[0].rfind(percent_area) + len(percent_area)
        block[0] = block[0].strip()
        for i, line in enumerate(block[1:]):
            # edit block in place
            block[i + 1] = line[line_indent:]

    def add_separator(self, separator: str = ' @ ', id_stop: int = None, ref_start: int = None) -> None:
        """
        Will guess where to add a separator between molecule ids and tailing values on each reference line if no
        configuration setting or id_stop and ref_start parameters are found.

        Guessing is done by checking the first line for the index of a reference 3 digits long then updating the
        index whenever a smaller reference number index is found.

        :param id_stop: Length to cut molecule IDs to.
        :param ref_start: Position of reference number and start of tailing values.
        :param separator: The character used to distinguish between molecule IDs and tailing values.
        """
        # copy block
        block = self.peak_block

        # TODO: find better way to use params when present. Maybe overload?quality
        if id_stop is not None and ref_start is None:
            raise ValueError('Value for ref_start must be passed if a value for id_stop is passed')
        elif ref_start is not None and id_stop is None:
            raise ValueError('Value for id_stop must be passed if a value for ref_start is passed')
        elif ref_start is not None and id_stop is not None:
            cfg.ref_num_start, cfg.mol_id_stop = ref_start, id_stop
        # if column values are specified in config instance
        if cfg.ref_num_start and cfg.mol_id_stop:
            self.logger.info("Found config values.")
            # could add logic for cfg.mol_id_start
            ref_start = cfg.ref_num_start
            id_stop = cfg.mol_id_stop

            for i, line in enumerate(block[1:]):
                if len(line) > id_stop:
                    # strip in place
                    block[i + 1] = line[:id_stop] + separator + line[ref_start:]
                else:
                    # extend in place
                    block[i + 1] = line.ljust(id_stop)
        else:
            self.logger.info("Didn't find config values, using first line as guess.")

            ref_start, id_stop = 0, 0

            # looks for three digits in a row
            ref_index_start: Callable[[str], int] = lambda test_line: re.search(r"\d{3,}", test_line).start()
            # looks for whitespace
            id_index_stop: Callable[[str], int] = lambda test_line: re.search(r"\s*$", test_line).start()

            for i, line in enumerate(block[1:]):
                if len(line) > ref_start:
                    ref_start = ref_index_start(line)
                    id_stop = id_index_stop(line[:ref_start])
                    # strip in place
                    block[i + 1] = line[:id_stop] + separator + line[ref_start:]

                elif id_stop > len(line):
                    # extend in place
                    block[i + 1] = line.ljust(id_stop)

            cfg.ref_num_start, cfg.mol_id_stop = ref_start, id_stop  # I don't think I need this here

    def combine_lines(self, seperator: str = ' @ ') -> None:
        """
        Combines all proposed molecule IDs for each guess in the peak list into a single string and append tailing
        values.

        :param seperator: Character used to determine the start of each guess and what to append as tail.
        """
        lines = self.peak_block
        indices = []

        for n, line in enumerate(lines):
            if seperator in line:
                indices.append(n)

        indices.append(None)
        lines[1:] = [lines[indices[i]:indices[i + 1]] for i in range(len(indices) - 1)]

        for i, line in enumerate(lines[1:]):
            line[0], tail = line[0].split(seperator)
            combined_lines = ''.join(line)
            # for line in part:
            #     comb_lines += line
            lines[i + 1] = combined_lines + seperator + tail

        self.possible_IDs = len(lines)

    def trailing_values(self, line: str, seperator: str = ' @ ') -> None:
        """
        Looks for values after seperator and parse 'Ref#', 'CAS#', 'Qual' into reference_num, cas_num, and quality.

        :param line: String to scrape of tailing values.
        :param seperator: The charactor used to denote tailing values.
        """
        ref, cas, qual = line[line.find(seperator) + len(seperator):].split()
        self.reference_nums.append(int(ref))
        self.cas_nums.append(int(cas.replace('-', '')))
        self.qualities.append(int(qual))

    def parse_lines(self, keyword: str = "(CAS)", delimiter: str = "$$", seperator: str = '@') -> None:
        """
        Uses peak list along with the keyword, delimiter, and seperator to determine the molecule ID for each guess
        in the peak. duplicates are not considered.

        Molecule IDs immediately before the keyword are prioritized. If there is no keyword the first molecule ID
        before a delimiter is used, else the entire string before the seperator is used.

        :param keyword: String used to denote the best potential molecule ID.
        :param delimiter: String used to denote different molecule IDs.
        :param seperator: Charactor used to denote the end of all molecule IDs.
        """
        lines = self.peak_block

        for line in lines:
            if seperator in line:
                candidate = line.split(seperator)[0]

                if keyword in line:
                    candidate = line[:line.find(keyword)]
                    self.logger.debug(f"{keyword} candidate: {candidate}")

                    if delimiter in candidate:
                        candidate = candidate[candidate.index(delimiter) + len(delimiter):]
                        self.logger.debug(f"{delimiter} candidate: {candidate}")

                else:
                    candidate = candidate[:candidate.find(delimiter)]
                    self.logger.debug(f"Behind {delimiter} candidate: {candidate}")

                candidate = candidate.lower().strip()
                if candidate not in self.ID:
                    self.ID.append(candidate)
                    self.trailing_values(line)
        # del self.peak_block

    def find_molecule(self):
        pass


if __name__ == '__main__':
    test_block = ['  1   3.474  0.00 C:\\Database\\WILEY275.L',
                  '                 2-Propenal (CAS) $$ Acrolein $$ NS    401 000107-02-8  4',
                  '                 C 8819 $$ Aqualin $$ Propenal $$ A',
                  '                 crylaldehyde $$ Allyl aldehyde $$ ',
                  '                 2-Propen-1-one $$ Prop-2-en-1-al $',
                  '                 $ trans-Acrolein $$ Acrylic aldehy',
                  '                 de $$ Magnacide H $$ Acroleine $$ ',
                  '                 CH2=CHCHO $$ Acraldehyde $$ 2-Prop',
                  '                 enal (Acrylaldehy',
                  '                 2-Propenal $$ Acrolein (CAS) $$ NS    400 000107-02-8  4',
                  '                 C 8819 $$ Aqualin $$ Propenal $$ A',
                  '                 crylaldehyde $$ Allyl aldehyde $$ ',
                  '                 2-Propen-1-one $$ Prop-2-en-1-al $',
                  '                 $ trans-Acrolein $$ Acrylic aldehy',
                  '                 de $$ Magnacide H $$ Acroleine $$ ',
                  '                 CH2=CHCHO $$ Acraldehyde $$ 2-Prop',
                  '                 enal (Acrylaldehy',
                  '                 2-Butene, (E)- (CAS) $$ trans-2-Bu    1429 000624-64-6  3',
                  '                 tene $$ (E)-2-Butene $$ trans-Bute',
                  '                 ne $$ 2-trans-Butene $$ trans-1,2-',
                  '                 Dimethylethylene $$ (E)-2-C4H8',
                  '                 ISO BUTYRALDEHYDE                    1475 000078-84-2 72',
                  '                 11-Oxatricyclo(5.4.1.0)dodecan-9-o  64703 073274-37-0 37',
                  '                 ne']
    p = Peak(peak_lines=test_block)
    p.peak_header()
    p.left_align()
    p.add_separator()
    p.combine_lines()
    p.parse_lines()
    print(p.peak_block)
    # del p.peak_block
    print(p)

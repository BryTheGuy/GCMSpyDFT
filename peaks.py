import logging
import re
from typing import Callable

# import molecule
from config import cfg

peak_logger = logging.getLogger('GCMSpyDFT.peak')


class Peak:
    def __init__(self, peak_block: list[str]):
        self.logger = logging.getLogger('GCMSpyDFT.peak.Peak')
        self.logger.info('Creating new peak instance.')

        self.peak_block = peak_block  # list of all lines in peak
        self.peak_num = None  # position of peak
        self.retention_time = None  # retention time of peak
        self.percent_area = None  # percent area of peak
        self.library = None  # Library used for peak
        self.possible_IDs = None  # total number of guess made in peak
        self.ID = []  # list of unique proposed molecule names in peak
        self.reference_num = []  # list of all reference numbers in peak
        self.cas_num = []  # list of all CAS numbers in peak
        self.quality = []  # list of all qualities in peak

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(
            f'{item} = {self.__dict__[item]}'
            if item not in ['peak_block', 'logger'] else item
            for item in self.__dict__)

    def peak_header(self):
        block = self.peak_block
        pn, rt, pa, lib = block[0].split()
        self.peak_num = int(pn)
        self.retention_time = float(rt)
        self.percent_area = float(pa)
        self.library = lib

    def left_align(self):
        block = self.peak_block
        # could add logic for cfg.mol_id_start
        _pn, _rt, percent_area, _lib = block[0].split()
        line_indent = block[0].rfind(percent_area) + len(percent_area)
        block[0] = block[0].strip()
        for i, line in enumerate(block[1:]):
            # edit block in place
            block[i + 1] = line[line_indent:]

    def add_separator(self, separator: str = ' @ '):
        # copy block
        block = self.peak_block
        # if column values are specified in config instance
        if cfg.ref_num_start and cfg.mol_id_stop:
            self.logger.info("Found config values.")
            # could add logic for cfg.mol_id_start
            ref_num_start = cfg.ref_num_start
            mol_id_stop = cfg.mol_id_stop

            for i, line in enumerate(block[1:]):
                if len(line) > mol_id_stop:
                    # strip in place
                    block[i + 1] = line[:mol_id_stop] + separator + line[ref_num_start:]
                else:
                    # extend in place
                    block[i + 1] = line.ljust(mol_id_stop)
        else:
            self.logger.info("Didn't find config values, using first line as guess.")

            ref_num_start, mol_id_stop = 0, 0

            # looks for three digits in a row
            ref_index_start: Callable[[str], int] = lambda test_line: re.search(r"\d{3,}", test_line).start()
            # looks for whitespace
            id_index_stop: Callable[[str], int] = lambda test_line: re.search(r"\s*$", test_line).start()

            for i, line in enumerate(block[1:]):
                if len(line) > ref_num_start:
                    ref_num_start = ref_index_start(line)
                    mol_id_stop = id_index_stop(line[:ref_num_start])
                    # strip in place
                    block[i + 1] = line[:mol_id_stop] + separator + line[ref_num_start:]

                elif mol_id_stop > len(line):
                    # extend in place
                    block[i + 1] = line.ljust(mol_id_stop)

            cfg.ref_num_start, cfg.mol_id_stop = ref_num_start, mol_id_stop

    def combine_lines(self, seperator: str = ' @ '):
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

    def trailing_values(self, line: str, seperator: str = ' @ '):
        ref, cas, qual = line[line.find(seperator) + len(seperator):].split()
        self.reference_num.append(int(ref))
        self.cas_num.append(int(cas.replace('-', '')))
        self.quality.append(int(qual))

    def parse_lines(self, keyword: str = "(CAS)", delimiter: str = "$$", seperator: str = '@'):
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
    p = Peak(peak_block=test_block)
    p.peak_header()
    p.left_align()
    p.add_separator()
    p.combine_lines()
    p.parse_lines()
    print(p.peak_block)
    # del p.peak_block
    print(p)

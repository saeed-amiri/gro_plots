import re
import sys
import typing
import pandas as pd
from colors_text import TextColor as bcolors


class Doc:
    """plot energy output of GROMACS from command li:
    `gmx_mpi energy -f npt_rerun.edr -o XXXX.xvg`
    Input:
    Any number of input file with xvg extensions
    """


class GetXvg:
    """reading *.xvg files and return data in dataframe style"""
    def __init__(self,
                 fname: str  # Name of the input file
                 ) -> None:
        self.__read_xvg(fname)

    def __read_xvg(self,
                   fname: str  # Name of the input file
                   ) -> pd.DataFrame:
        self.__get_header(fname)

    def __get_header(self,
                     fname: str  # Name of the xvg 25
                     ) -> dict[str, str]:
        """read header of xvg file, lines which started with `@`"""
        Maxlines: int = 30  # should not be more then 26
        linecount: int = 0  # Tracking number of lines with `@`
        labels_dict: dict = dict()  # Contains all the labels from xvg file
        with open(fname, 'r') as f:
            while True:
                linecount += 1
                line: str = f.readline()
                if not line.strip().startswith('@'):
                    pass
                else:
                    self.__process_line(line.strip())
                if linecount > Maxlines:
                    print(f'{bcolors.OKCYAN}{self.__class__.__name__}:\n'
                          f'\tNumber of lines with `@` in "{fname}" is '
                          f'{linecount}{bcolors.ENDC}')
                    break
                if not line:
                    exit()

    def __process_line(self,
                       line: str  # Line start with `@`
                       ) -> tuple[str]:
        """get labels from the lines"""
        l_line: list[str]  # Breaking the line
        l_line = line.split('@')[1].split(' ')
        l_line = [item for item in l_line if item]
        axis: str = None  # Label of the axis
        if 'label' in l_line:
            if 'xaxis' in l_line:
                axis = 'xaxis'
            if 'yaxis' in l_line:
                axis = 'yaxis'
            label = re.findal('"([^"]*)"', line)[0]
        return (axis, label)


if __name__ == "__main__":
    xvg = GetXvg(sys.argv[1])

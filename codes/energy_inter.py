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
        data_dict: dict[str, typing.Any] = self.__get_header(fname)
        self.__read_data(data_dict['nHeader'], data_dict['data'])

    def __read_data(self,
                    nHeader: int,  # Number of lines in the header to scape
                    data: list[str]  # Unbrocken lines of data
                    ) -> pd.DataFrame:
        time: list[float]  # 1st column of the data file
        energy: list[float]  # 2nd column of the data file
        for item in data:
            tmp_list = [i for i in item.split(' ') if i]

    def __get_header(self,
                     fname: str  # Name of the xvg 25
                     ) -> dict[str, typing.Any]:
        """read header of xvg file, lines which started with `@`"""
        print(f'{bcolors.OKBLUE}{self.__class__.__name__}:\n'
              f'\tReading file : {fname}\n{bcolors.ENDC}')
        Maxlines: int = 30  # should not be more then 26
        linecount: int = 0  # Tracking number of lines with `@`
        header_line: int = 0  # Number of header lines
        data_dict: dict = dict()  # Contains all the labels from xvg file
        data: list[str] = []  # Lines contains numberic data
        with open(fname, 'r') as f:
            while True:
                linecount += 1
                line: str = f.readline()
                if line.startswith('#') or line.startswith('@'):
                    header_line += 1
                    if line.strip().startswith('@'):
                        axis, label = self.__process_line(line.strip())
                        if axis:
                            if axis in ['xaxis', 'yaxis', 'legend']:
                                data_dict[axis] = label
                else:
                    if line:
                        data.append(line.strip())

                if linecount > Maxlines and len(data_dict) < 3:
                    print(f'{bcolors.OKCYAN}{self.__class__.__name__}:\n'
                          f'\tNumber of lines with `@` in "{fname}" is '
                          f'{linecount}{bcolors.ENDC}')
                    break
                if not line:
                    break
        data_dict['nHeader'] = header_line
        data_dict['fname'] = fname
        data_dict['data'] = data
        return data_dict

    def __process_line(self,
                       line: str  # Line start with `@`
                       ) -> tuple[str]:
        """get labels from the lines"""
        l_line: list[str]  # Breaking the line
        l_line = line.split('@')[1].split(' ')
        l_line = [item for item in l_line if item]
        axis: str = None  # Label of the axis
        label: str = None  # Label of the axis
        if 'label' in l_line:
            if 'xaxis' in l_line:
                axis = 'xaxis'
            if 'yaxis' in l_line:
                axis = 'yaxis'
            label = re.findall('"([^"]*)"', line)[0]
        elif 'legend' in l_line:
            if 's0' in l_line:
                label = re.findall('"([^"]*)"', line)[0]
                axis = 'legend'
        return axis, label


if __name__ == "__main__":
    xvg = GetXvg(sys.argv[1])

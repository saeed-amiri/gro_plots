"""plot energy output of GROMACS from command line:
    `gmx_mpi density -s npt.tpr -f npt.trr -n index.ndx'
    Input:
    Any number of input file with xvg extensions
    """

import re
import sys
import typing
import numpy as np
import pandas as pd
from colors_text import TextColor as bcolors
import matplotlib.pylab as plt
import matplotlib as mpl


def set_sizes(width, fraction=1):
    """set figure dimennsion"""
    fig_width_pt = width*fraction
    inches_per_pt = 1/72.27
    golden_ratio = (5**0.5 - 1)/2
    fig_width_in = fig_width_pt * inches_per_pt
    fig_height_in = fig_width_in * golden_ratio
    fig_dim = (fig_width_in, fig_height_in)
    return fig_dim

# Update the rcParams with the desired configuration settings
mpl.rcParams['axes.prop_cycle'] = \
    plt.cycler('color', ['k', 'r', 'b', 'g']) + \
                plt.cycler('ls', ['-', '--', ':', '-.'])
mpl.rcParams['figure.figsize'] = (3.3, 2.5)
mpl.rcParams['figure.dpi'] = 600
mpl.rcParams['font.size'] = 8
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = 'Times'

width = 426.79135
fig, ax = plt.subplots(1, figsize=set_sizes(width))

# Set axis style
plt.grid(True, linestyle='--', linewidth=0.5)
plt.tick_params(direction='in')

average: bool = False  # If write average on the legend
transparent: bool = True # If the figure wants to be transparent
savefig_kwargs = {'fname': 'output.png',
                  'dpi': 300,
                  'bbox_inches': 'tight'
                  }
if transparent:
    savefig_kwargs['transparent'] = 'true'


class GetXvg:
    """reading *.xvg files and return data in dataframe style"""
    def __init__(self,
                 fname: str  # Name of the input file
                 ) -> None:
        self.data: dict = self.__read_xvg(fname)

    def __read_xvg(self,
                   fname: str  # Name of the input file
                   ) -> dict:
        data_dict: dict = self.__get_header(fname)
        data_arr: np.array  # Array of data
        data_arr = self.__read_data(data_dict['data'])
        data_dict['data'] = data_arr
        data_dict['average']: float = self.get_average(data_dict['data'])
        return data_dict

    def __read_data(self,
                    data: list  # Unbrocken lines of data
                    ) -> np.array:
        data_arr: np.array  # Array to save data
        data_arr = np.zeros((2, len(data)))
        for ind, item in enumerate(data):
            tmp_list = [i for i in item.split(' ') if i]
            data_arr[0][ind] = float(tmp_list[0])
            data_arr[1][ind] = float(tmp_list[1])
            del tmp_list
        # data_arr[1,:] = self.__normalize(data_arr[1,:])
        return data_arr

    def __normalize(self,
                    data: typing.Any  # Data to normalize to one
                    ) -> typing.Any:
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    def __get_header(self,
                     fname: str  # Name of the xvg 25
                     ) -> dict:
        """read header of xvg file, lines which started with `@`"""
        print(f'{bcolors.OKBLUE}{self.__class__.__name__}:\n'
              f'\tReading file : {fname}\n{bcolors.ENDC}')
        Maxlines: int = 30  # should not be more then 26
        linecount: int = 0  # Tracking number of lines with `@`
        header_line: int = 0  # Number of header lines
        data_dict: dict = dict()  # Contains all the labels from xvg file
        data: list = []  # Lines contains numberic data
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
                       ) -> tuple:
        """get labels from the lines"""
        l_line: list  # Breaking the line
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

    def get_average(self,
                    x: np.array  # Data to get average from
                    ) -> float:
        return np.average(x)


if __name__ == "__main__":
    xvg_files: list = sys.argv[1:]
    for f in xvg_files:
        xvg = GetXvg(f)
        label = f'{xvg.data["fname"]}'
        if average:
            label += f', ave={xvg.data["average"]:.3f}'

        ax.plot(xvg.data['data'][0],
                    xvg.data['data'][1],
                    label=label)
    plt.xlabel(xvg.data['xaxis'])
    plt.ylabel(xvg.data['yaxis'])

    # Adjust tick label font size and style if needed
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.legend()
    plt.savefig(**savefig_kwargs)
    # plt.show()

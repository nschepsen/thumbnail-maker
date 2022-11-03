from argparse import ArgumentParser, ArgumentTypeError
from os.path import abspath, exists
from sys import exc_info as debug
from traceback import extract_tb as traceback

from tnmake.logging import get_basic_logger

logger = get_basic_logger()  # stdout only
from tnmake import __project__, __version__
from tnmake.tnmake import Thumbnail # thumbnail class


def apt_path_exists(path: str) -> str:
    '''
    check if passed path to Argsparser exists
    :return: path or ArgumentTypeError
    '''
    if not exists(path):

        raise ArgumentTypeError('No such file or directory')

    return abspath(path) # return absolute path

def main():

    '''
    Here is the ENTRYPOINT for `pip` and `standalone` versions
    '''

    parser = ArgumentParser(description=f'{__project__} creates customisable thumbnails with some additional information')
    # add cli arguments
    parser.add_argument(
        '-i', '--input',
        required=True, # pass a filepath
        help=f'set video file\'s path ',
        metavar='path',
        type=apt_path_exists) # movie
    parser.add_argument(
        '-o', '--output',
        help='set custom output filename',
        metavar='filename')
        # type=abspath,
        # default=getcwd()) # use a current working directory as default
    parser.add_argument(
        '-q', '--quality',
        type=int,
        help='set output image quality (default: 100)',
        metavar='percentage',
        default=100) # quality gets over the space usage
    parser.add_argument(
        '-w', '--width',
        type=int,
        help='set width of output image',
        metavar='px',
        default=1150)
    parser.add_argument(
        '-c', '--comment',
        type=str,
        help='add a comment as a thumbnail annotation',
        metavar='annotation',
        default='') # let it empty if you won't left any commments
    parser.add_argument(
        '-g', '--grid',
        type=str,
        help='set layout of a resulting thumbnail',
        metavar='layout',
        default='3x8') # predefined layout consists of 3 cols & 8 rows
    parser.add_argument(
        '-e', '--extension',
        help='choose the output extension (default: "jpg")',
        choices=['bmp', 'jpg', 'png'],
        default='jpg')
    parser.add_argument(
        '-f', '--font',
        type=str,
        help='set path to a fontfile (default: "Mono Input Condensed (Light, Italic)")',
        metavar='path')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        default=False,
        help='enable verbose mode')
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'{__project__} v{__version__}')
    args = parser.parse_args() # evaluate all arguments and pass 'em through
    if args.verbose:
        logger.setLevel(10)
    options = {
        'font': args.font, # set defaults in class itself
        'layout': args.grid, # 3x8
        'comment': args.comment,
        'ext': args.extension,
        'width': args.width, # 1150
        'quality': args.quality # 100 is preferable for quality purpose
        }
    try:
        Thumbnail(options).perform(args.input, args.output) # Run `pip` version
    except Exception as e:
        position = traceback(debug()[2])[-1]
        print(f'Exception: {"".join(str(e).split(chr(10)))} (see@{position[2]}:{position[1]})')

# Thumbnail!MAKER creates customisable thumbnails and adds some tech details in the picture's header

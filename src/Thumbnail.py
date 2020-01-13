#!/usr/bin/python3

from datetime import timedelta
from operator import floordiv, truediv
from os import getcwd, remove
from os.path import dirname, isfile, join, realpath
from random import randrange
from subprocess import call, check_output
from sys import argv
from sys import exc_info as debug
from traceback import extract_tb as traceback

from rapidjson import loads

__VERSION__ = '0.1.0'
__BUILD__ = '20200113'

def next(element: str, arr: list, callback = lambda x: x):

    '''
    Get the next element and execute a callback function
    '''
    try:
        index = arr.index(element) + 1
    except ValueError:
        return None

    return callback(arr[index]) if index < len(arr) else None

def humanreadable(value: int) -> str:

    for unit in ['bytes', 'KiB', 'MiB', 'GiB', 'TiB']:
        if value < 1024:
            return f'{value:0.1f} {unit}'
        value = truediv(value, 1024)
    return f'{value:0.1f} PiB' # pebibyte 1024^5 = 1125899906842624 bytes

gcd = lambda a, b: a if b == 0 else not a % b and b or gcd(b, a % b)

def help():

    print (
        f'\n'
        f'Attention: Don\'t forget to install these additional apps\n'
        f'\n'
        f' > ffmpeg, imagemagick\n'
        f'\n'
        f'USAGE: python3 {__file__.split("/")[-1]} [-i infile] [OPTIONS], where options are\n'
        f'\n'
        f' -i, --input\n  set the path to the file you want to pass to Thumbnail!MAKER\n'
        f' -q, --quality\n  set the output image quality (recommended: 75)\n'
        f' -o, --output\n  set the output filename\n'
        f' -h, --help\n  show this help message and exit\n'
        f' -w, --width\n set the width of the output image\n'
        f' -c, --comment\n add a comment to the thumbnail annotation\n'
        f' -d, --dimension\n set the number of cols&rows, the dimension\n'
        f'\n'
        f'Thumbnail!MAKER v{__VERSION__}.{__BUILD__} (Check for updates @ GitHub)\n'
    )

class Thumbnailer:

    def __init__(self, options: dict):

        self.path = dirname(realpath(__file__))

        self.options = {
            'fontsize': 16,
            'font': options.get('font', join(self.path, join('fonts', 'ColabLig.otf'))),
            'dimension': options.get('dimension', f'3x8'),
            'comment': options.get('comment', None),
            'width': options.get('width', 1150),
            'quality': options.get('quality', 100)
        }

    def perform(self, video:str, output = None):

        filename = '.'.join(video.split(chr(47))[-1].split('.')[:-1])
        ext = video.split('.')[-1]
        id3tags = loads(
            check_output(['ffprobe',
                '-v', 'error',
                '-show_entries',
                'format=duration,size:stream=codec_name,codec_long_name,profile,codec_type,bit_rate,sample_rate,width,height,display_aspect_ratio,r_frame_rate,level,channels:stream_tags=language',
                '-of', 'json', video
            ]))
        duration = int(float(id3tags['format']['duration']))
        streams = [[],[]]
        size = int(id3tags['format']['size'])
    # Fetch all required id3 meta tags
        for stream in id3tags['streams']:
        # codec name
            codec = stream.get('codec_long_name', 'unknown').split(chr(47))[0].strip()
        # bitrate
            bitrate = floordiv(int(stream['bit_rate']), 1000)
            if stream['codec_type'] == 'video':
            # resolution
                resolution = f'{stream["width"]}x{stream["height"]}'
            # display aspect ratio, e.g. 16:9
                ratio = stream.get(
                    'display_aspect_ratio',
                    (lambda w, h: f'{floordiv(w, gcd(w, h))}:{floordiv(h, gcd(w, h))}')(stream['width'], stream['height'])
                )
            # frames per second
                fps = (lambda x: truediv(x[0], x[1]))(list(map(int, stream['r_frame_rate'].split(chr(47)))))
            # encode profile
                profile = stream['profile']
                level = (lambda x: f'{x[:1]}.{x[1:]}')(str(stream['level']))
            # add a description to the stream list
                streams[0].append(
                    f'Video: {codec}, {bitrate} kbps, {resolution} ({ratio}), at {fps:0.3f} fps ({profile}@{level})'
                )
            else:
            # audio stream language
                lang = {
                    'eng': 'English',
                    'deu': 'German',
                    'fre': 'French',
                    'ita': 'Italian',
                    'rus': 'Russian',
                    'spa': 'Spanian'
                }.get(stream['tags']['language'], 'English')
            # samplerate
                samplerate = truediv(float(stream['sample_rate']), 1000)
            # channels, e.g. 2, 5.1, stereo, etc
                channels = stream.get('channels', 'unknown')
            # Save parsed Stream as a String
                streams[1].append(f'Audio: {lang}, {bitrate} kbps, {samplerate} kHz, {channels} channels, {codec})')
    # Take Snapshots
        shots = (lambda x: x[0]*x[1])(list(map(int, self.options['dimension'].split('x'))))
        framelist = []
        thumbnail = join(getcwd(), f'{output or filename}.png')
        for i in range(shots):
            step = floordiv(duration, shots)
            if step <= 0:
                raise Exception('The delay between screenshots is zero or less!')
            frame = step * i + randrange(step)
        # Add the frame to the list
            framelist.append(join(getcwd(), f'frame{frame:06d}.png'))
            call(['ffmpeg', '-ss', str(frame), '-v', 'error', '-i', video, '-vframes', '1', framelist[-1], '-y'])
            call(['convert',
                framelist[-1],
                '-font', self.options.get('font'),
              # '-undercolor', 'white',
                '-pointsize', '200',
                '-gravity', 'South',
                '-stroke', 'rgba(0,0,0,0.50)',
              # '-strokewidth', '1',
                '-fill', 'rgba(255,255,255,0.20)',
                '-annotate', '+0+30', f'{str(timedelta(seconds=frame)).zfill(8)}',
                framelist[-1]])
        call(['montage', '-tile', self.options.get('dimension'), '-geometry', '+2+2', *framelist, thumbnail])
    # Resize the Image to w:1200 #
        call(['mogrify', '-resize', str(self.options.get('width')), thumbnail])
        annotation = (
            f'Filename: {filename}.{ext}\n{chr(10).join([*streams[0], *streams[1]])}\n'
            f'Duration: {str(timedelta(seconds=duration)).zfill(8)}, '
            f'Size: {size:,} Bytes ({humanreadable(size)})'
            f'{chr(10) + "Comment: " + self.options.get("comment") if self.options.get("comment") else ""}'
        )
    # Render Annotation #
        call(['convert',
            '-font', self.options.get('font'),
            '-density', '288',
            '-resize', '25%',
            '-pointsize', str(self.options.get('fontsize')), f'label:{annotation}', 'annotation.png']
        )
    #height = (len(streams)+2)*(self.options.get('fontsize')+2)+4
        height = (annotation.count('\n')+1)*(self.options.get('fontsize')+2)+4
        call(['convert', thumbnail, '-quality', str(self.options.get('quality')), '-splice', f'0x{height}', '-draw', 'image over 5,5 0,0 annotation.png', thumbnail])
    # Clean Up #
        for i in framelist:
            remove(i)
        remove(join(getcwd(), 'annotation.png'))

def main():

    if any(opt in argv for opt in ['-h', '--help']):
        help()
        exit()
    options, video, output = {}, None, None
    for opt in argv:
        if opt in ['-i', '--input']:
            video = next('-i', argv, lambda x: x if isfile(join(getcwd(), x)) else None)
        key = None
        if opt in ['-q', '--quality']:
            key = 'quality'
        if opt in ['-o', '--output']:
            output = next(opt, argv)
        if opt in ['-d', '--dimension']:
            key = 'dimension'
        if opt in ['-w', '--width']:
            key = 'width'
        if opt in ['-c', '--comment']:
            key = 'comment'
        if key: options[key] = next(opt, argv)
    try:
        Thumbnailer(options).perform(video, output)
    except Exception as e:
        position = traceback(debug()[2])[-1]
        print(f'\nException: {"".join(str(e).split(chr(10)))} (see@{position[2]}:{position[1]})')
        help()

if __name__ == '__main__': main()

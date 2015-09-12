#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os.path
import sys
import os

BASEURL = "http://nacr.us/media/video/game_grumps/"

def run_command(cmd):
    """Runs a given command in a shell."""
    print(cmd)
    os.system(cmd)


def get_files(filedir='./', fileext='mp4'):
    """Given a file directory, gets all the files in that directory."""
    onlyfiles = [f for f in os.listdir(filedir)\
        if os.path.isfile(os.path.join(filedir, f)) and fileext in f]

    return sorted(onlyfiles)

def get_mpg_audio_files(series_alias):
    """Returns all mp3 files."""
    mp3s = get_files(filedir='./'+series_alias+'/audio', fileext='mp3')
    mp3s = ['{}/audio/{}'.format(series_alias, mp3) for mp3 in mp3s]
    return mp3s

def get_aac_audio_files(series_alias):
    """Returns all aac files."""
    aacs = get_files(filedir='./'+series_alias+'/audio', fileext='m4a')
    aacs = ['{}/audio/{}'.format(series_alias, afile) for afile in aacs]
    return aacs

def get_complete(series_alias):
    """Returns the completely compiled audio file path."""
    complete = get_files(filedir='./'+series_alias, fileext='mp3')
    complete = ['{}/{}'.format(series_alias, mp3) for mp3 in complete]
    return complete[0]

def sizeof_fmt(num):
    """Given a number of bytes, returns human readable str representation."""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0

def strip_ext(filename):
    """Removes the extension from a filename."""
    return ''.join(filename.split('.')[:-1])

def download_series(series_url, series_alias):
    """Downloads a given youtube series."""
    download_cmd = \
    'youtube-dl --force-ipv4 -f "141/140" "{}" -o "./{}/video/%(autonumber)s__%(title)s.%(ext)s"'
    download_cmd = download_cmd.format(series_url, series_alias)

    return download_cmd

def extract_audio_command_builder(series_alias):
    """Builds the commands to be run out of the list of files."""
    ggfiles = get_files('./'+series_alias+'/video', '.m4a')

    convertcommands = []
    for index, value in enumerate(ggfiles):
        convertcommands.append('ffmpeg -i '+\
        '"./{2}/video/{1}" -vn -ac 2 -ar 44100 -ab 192k -f mp3 "./{2}/audio/{3}_192k.mp3"'\
        .format(index+1, value, series_alias, strip_ext(value)))

    return ' && '.join(convertcommands)

def build_cmd_extract_aac(series_alias):
    """Builds command to extract aac from video files."""
    vfiles = get_files('./'+series_alias+'/video')

    convertcommands = []
    for vid in vfiles:
        convertcommands.append('ffmpeg -i '+\
        '"./{1}/video/{0}" -vn -acodec copy "./{1}/audio/{2}.m4a"'.format(\
            vid, series_alias, strip_ext(vid)))
    return ' && '.join(convertcommands)

def build_concat_aac(series_alias):
    """Concatenates aac files. Right now this doesn't work, I don't know why."""
    afiles = get_aac_audio_files(series_alias)
    command = 'ffmpeg -i "concat:{}" -acodec copy {}/complete_{}.m4a'
    command = command.format('|'.join(afiles), series_alias, series_alias)
    return command


def concat_audio_cmd_builder(series_alias):
    """Concatenates all mp3 files in a directory together."""
    mp3s = get_mpg_audio_files(series_alias)
    print(mp3s)

    command = 'ffmpeg -i "concat:{}" -acodec copy {}/complete_{}.mp3'
    command = command.format('|'.join(mp3s), series_alias, series_alias)
    
    return command

def create_dirs(series_alias):
    """Creates the proper directory structure based on series alias."""
    dirlist = [
        './{}/',
        './{}/video/',
        './{}/audio'
    ]

    dirlist = [dirct.format(series_alias) for dirct in dirlist]

    for dirct in dirlist:
        if not os.path.exists(dirct):
            os.makedirs(dirct)

    return

def seperate_mp3_format(series_alias, series_full_name=''):
    """Builds markdown for the separate mp3s"""
    # output = ""
    ziplocation = series_alias+'/audio/'+series_alias+'.zip'
    fmt = u"""
    - [All *{0}* separate audio files in one zip ]({1}{2}) -- {3}
    - [List of individual audio files for *{0}*]({1}{4})

    """.format(\
        series_full_name, BASEURL, ziplocation,\
        sizeof_fmt(os.path.getsize(ziplocation)), series_alias+'/audio/')
    # for afile in get_mpg_audio_files(series_alias):
    #     output += fmt.format(strip_ext(os.path.basename(afile)),\
    #         BASEURL, afile, sizeof_fmt(os.path.getsize(afile)))

    return fmt



def build_markdown(series_alias, series_full_name=''):
    """Creates markdown for information about the series."""

    if not series_full_name:
        series_full_name = series_alias

    # Note, there are non-breaking spaces
    info = u"""
## {0}

- Single MP3
    - `Download URL:` [{1}{2}]({1}{2})
    - `Filesize    :` {3}
- Seperate MP3s"""

    info = info.format(series_full_name,\
        BASEURL, get_complete(series_alias),\
        sizeof_fmt(os.path.getsize(get_complete(series_alias))))
    info += seperate_mp3_format(series_alias, series_full_name)

    return info

def zip_separate(series_alias):
    """Zips up all the separately created audio files."""
    cmdstr = 'zip "{0}/audio/{0}.zip" {0}/audio/*.mp3'.format(series_alias)
    return cmdstr


def main():
    """Controls flow of program through procedure."""
    if len(sys.argv) < 3:
        print("Need series name and series url. Exiting")
        exit()
    elif len(sys.argv) > 3 and sys.argv[3] == 'print':
        run_command(zip_separate(sys.argv[1]))
        print(build_markdown(sys.argv[1]))
        return
    else:
        series_alias, series_url = sys.argv[1], sys.argv[2]

    # Make the directories
    create_dirs(series_alias)
    
    run_command(download_series(series_url, series_alias))
    run_command(extract_audio_command_builder(series_alias))
    run_command(concat_audio_cmd_builder(series_alias))
    run_command(zip_separate(series_alias))

    # run_command(build_cmd_extract_aac(series_alias))
    # run_command(build_concat_aac(series_alias))
    
    print(build_markdown(series_alias))


if __name__ == '__main__':
    main()

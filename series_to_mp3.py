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


def seperate_mp3_format(series_alias, series_full_name=''):
    """Builds markdown for the separate mp3s"""

    if not series_full_name: series_full_name = series_alias

    ziplocation = series_alias+'/audio/'+series_alias+'.zip'
    fmt = u"""
    - [All *{0}* separate audio files in one zip ]({1}{2}) -- {3}
    - [List of individual audio files for *{0}*]({1}{4})

    """.format(\
        series_full_name, BASEURL, ziplocation,\
        sizeof_fmt(os.path.getsize(ziplocation)), series_alias+'/audio/')
    return fmt


def build_markdown(series_alias, series_full_name=None):
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


def create_dirs(series_alias):
    """Based on the given series_alias, creates the proper cooresponding directory structure."""
    dirlist = [
        './{}/',
        './{}/video/',
        './{}/audio'
    ]

    dirlist = [given_dir.format(series_alias) for given_dir in dirlist]

    # Create a the directories (if they don't exist)
    for given_dir in dirlist:
        if not os.path.exists(given_dir):
            os.makedirs(given_dir)


def download_series(series_url, series_alias):
    """Downloads a given youtube series into the `series_alias/video/` folder."""
    download_cmd = \
    'youtube-dl --force-ipv4 -f "141/140" "{}" -o "./{}/video/%(autonumber)s__%(title)s.%(ext)s"'
    download_cmd = download_cmd.format(series_url, series_alias)
    return download_cmd


def transcode_source_to_new_audio(series_alias, audio_fmt='mp3'):
    """Creates shell command to derive mp3 audio from existing downloaded media."""
    ggfiles = get_files('./'+series_alias+'/video', '.m4a')

    convertcommands = []
    def mpg_transcode(value, series_alias):
        cmd = 'ffmpeg -i '+\
        '"./{series_alias}/video/{source_file}" '+\
        '-vn -ac 2 -ar 44100 ab 192k -f mp3 '+\
        '"./{series_alias}/audio/{source_file_name}_192k.mp3"'

        cmd = cmd.format(source_file=value,
                         series_alias=series_alias,
                         source_file_name=strip_ext(value))

        return cmd
    def aac_copy(value, series_alias):
        cmd = 'cp "./{series_alias}/video/{source_file}" '+\
        '"./{series_alias}/audio/{source_file}"'
        cmd = cmd.format(source_file=value, series_alias=series_alias)
        return cmd
    for index, value in enumerate(ggfiles):
        delegate = { 'mp3': mpg_transcode,
                     'aac': aac_copy
                   }[audio_fmt]
        convertcommands.append(delegate(value, series_alias))

    return ' && '.join(convertcommands)


def concat_audio_cmd_builder(series_alias):
    """Concatenates all mp3 files in a directory together."""
    mp3s = get_mpg_audio_files(series_alias)
    print(mp3s)

    command = 'ffmpeg -i "concat:{}" -acodec copy {}/complete_{}.mp3'
    command = command.format('|'.join(mp3s), series_alias, series_alias)

    return command


def zip_separate(series_alias):
    """Zips up all the separately created audio files."""
    cmdstr = 'zip "{0}/audio/{0}.zip" {0}/audio/*'.format(series_alias)
    return cmdstr


def create_audio_for_series(series_alias, series_url, audio_format='mp3'):
    """Creates an audio series for the given youtube series."""
    # Make the directories
    create_dirs(series_alias)

    run_command(download_series(series_url, series_alias))
    run_command(transcode_source_to_new_audio(series_alias, audio_format))
    run_command(zip_separate(series_alias))
    run_command(concat_audio_cmd_builder(series_alias))

    return

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

    create_audio_for_series(series_alias, series_url, audio_format='mp3')
    print(build_markdown(series_alias))


if __name__ == '__main__':
    main()

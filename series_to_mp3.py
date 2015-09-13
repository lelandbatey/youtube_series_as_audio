#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import subprocess
import argparse
import os.path
import sys
import os

BASEURL = "http://nacr.us/media/video/game_grumps/"

def run_command(cmd):
    """Runs a given command in a shell."""
    print(cmd)
    subprocess.call(cmd, shell=True, executable='/bin/bash')


def get_files(filedir='./', fileext='mp4'):
    """Given a file directory, gets all the files in that directory."""
    onlyfiles = [f for f in os.listdir(filedir)\
        if os.path.isfile(os.path.join(filedir, f)) and fileext in f]
    return sorted(onlyfiles)


def get_audio_files(series_alias, ext):
    """Returns full path of files with given extension within series_alias"""
    files = get_files(filedir='./'+series_alias+'/audio', fileext=ext)
    return ['{}/audio/{}'.format(series_alias, afile) for afile in files]


def full_path_for_audio(series_alias, ext):
    """Returns the completely compiled audio file path."""
    complete = get_files(filedir='./'+series_alias, fileext=ext)
    complete = ['{}/{}'.format(series_alias, afile) for afile in complete]
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


def markdown_links_individual_files(series_alias, series_full_name=''):
    """Builds markdown for links to directory of individual audio files and zip."""

    if not series_full_name: series_full_name = series_alias

    ziplocation = series_alias+'/audio/'+series_alias+'.zip'
    fmt = u"""
    - [All *{0}* separate audio files in one zip ]({1}{2}) -- {3}
    - [List of individual audio files for *{0}*]({1}{4})

    """.format(\
        series_full_name, BASEURL, ziplocation,\
        sizeof_fmt(os.path.getsize(ziplocation)), series_alias+'/audio/')
    return fmt


def build_markdown(series_alias, audio_format='mp3', series_full_name=None):
    """Creates markdown for information about the series."""

    if not series_full_name:
        series_full_name = series_alias

    # Note, there are non-breaking spaces
    info = u"""
## {0}

- Single audio file
    - `Download URL:` [{1}{2}]({1}{2})
    - `Filesize    :` {3}
- Seperate audio files"""

    info = info.format(series_full_name,\
        BASEURL, full_path_for_audio(series_alias, audio_format),\
        sizeof_fmt(os.path.getsize(full_path_for_audio(series_alias, audio_format))))
    info += markdown_links_individual_files(series_alias, series_full_name)

    return info


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
    vid_dir = "./{}/audio/".format(series_alias)
    vid_files = get_files(vid_dir, '.')
    print(vid_files)
    #exit()
    if len(vid_files) > 1 and ('m4a' in vid_files[1] or 'mp4' in vid_files[1]):
        return "echo 'Source files have already been downloaded'"

    download_cmd = \
    'youtube-dl --force-ipv4 -f "141/140" "{}" -o "./{}/video/%(autonumber)s__%(title)s.%(ext)s" --restrict-filenames'
    download_cmd = download_cmd.format(series_url, series_alias)
    return download_cmd


def transcode_source_to_new_audio(series_alias, audio_fmt='mp3'):
    """Creates shell command to derive mp3 audio from existing downloaded media."""
    ggfiles = get_files('./'+series_alias+'/video', '.m4a')

    convertcommands = []
    def mpg_transcode(value, series_alias):
        cmd = 'ffmpeg -i '+\
        '"./{series_alias}/video/{source_file}" '+\
        '-vn -ac 2 -ar 44100 -ab 192k -f mp3 '+\
        '"./{series_alias}/audio/{source_file_name}_192k.mp3"'

        cmd = cmd.format(source_file=value,
                         series_alias=series_alias,
                         source_file_name=strip_ext(value))
        return cmd

    def aac_copy(value, series_alias):
        cmd = 'mv "./{series_alias}/video/{source_file}" '+\
        '"./{series_alias}/audio/{source_file}"'
        cmd = cmd.format(source_file=value, series_alias=series_alias)
        return cmd

    for index, value in enumerate(ggfiles):
        delegate = { 'mp3': mpg_transcode,
                     'm4a': aac_copy
                   }[audio_fmt]
        convertcommands.append(delegate(value, series_alias))

    return ' && '.join(convertcommands)


def concat_audio_cmd_builder(series_alias, format='mp3'):
    """Concatenates all mp3 files in a directory together."""
    afiles = get_audio_files(series_alias, format)
    print(afiles)

    def mpg_concat(mp3s):
        command = 'ffmpeg -i "concat:{}" -acodec copy {}/complete_{}.mp3'
        command = command.format('|'.join(mp3s), series_alias, series_alias)
        return command
    def aac_concat(afiles):
        command = 'ffmpeg -f concat -i <(for f in {series_alias}/audio/*.m4a; do echo "file \'$(realpath "$f")\'"; done;) -acodec copy {series_alias}/complete_{series_alias}.m4a'
        command = command.format(series_alias=series_alias)
        return command

    delegate = { 'mp3': mpg_concat,
                 'm4a': aac_concat
               }[format]

    return delegate(afiles)


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
    run_command(concat_audio_cmd_builder(series_alias, audio_format))


def main():
    """Controls flow of program through procedure."""

    series_alias = None
    series_url = None

    parser = argparse.ArgumentParser(description='Create an audiobook/podcast from a YouTube series')
    parser.add_argument('--alias', required=True, help='a "shortname" for the YouTube series. Used as name of folder for storing audio for this series.')
    parser.add_argument('--url', help='the URL to the YouTube playlist with all videos in desired series.')
    parser.add_argument('--print', help='attempt to generate markdown summary for an existing series.')
    parser.add_argument('--format', help='the output audio format. Either "mp3" or "m4a". Default is "mp3"', default='mp3')
    args = parser.parse_args()

    if args.alias:
        series_alias = args.alias
    if args.url:
        series_url = args.url

    if args.print and series_alias:
        build_markdown(series_alias)
        return

    if not (series_alias and series_url):
        print('Alias and url need to be provided')

    create_audio_for_series(series_alias, series_url, audio_format=args.format)
    print(build_markdown(series_alias, audio_format=args.format))


if __name__ == '__main__':
    main()

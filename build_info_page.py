from __future__ import print_function
from pprint import pprint
import markdown
import json
import csv
import sys

sys.path.append("../") 
sys.path.append("../youtube_series_mp3/") 

import series_to_mp3 as sm

def jdump(val):
    """Turns json object into pretty-formated string."""
    return json.dumps(val, sort_keys=True, indent=4, separators=(',', ': '))

def jp(val):
    """Prints out pretty-formated string of object."""
    print(jdump(val))

def is_valid_char(char):
    """Checks if a character is valid in a video/playlist id."""
    inc_range = lambda start, end: range(start, end+1)
    if (ord(char) in inc_range(48, 57) or
        ord(char) in inc_range(65, 90) or
        ord(char) in inc_range(97, 122) or char == '_' or char == '-'):
        return True
    return False

def extract_id(vurl, splt_str, template):
    """Extracts the video/playlist id, and applies it to given template."""
    yt_id = ''
    for char in vurl.split(splt_str)[1]:
        if is_valid_char(char):
            yt_id += char
        else:
            break
    template = template.format(yt_id)
    return yt_id, template

def parse_playlist_url(vurl):
    """Given the url to a playlist, extract it's id and create embed."""
    template = '<iframe width="480" height="270" src="//www.youtube.com/embed/videoseries?list={}" frameborder="0" allowfullscreen></iframe>'
    return extract_id(vurl, 'list=', template)

def parse_video_url(vurl):
    """Given the url to a video, extract it's id and create embed."""
    template = '<iframe width="480" height="270" src="//www.youtube-nocookie.com/embed/{}" frameborder="0" allowfullscreen></iframe>'
    return extract_id(vurl, 'v=', template)


class YoutubeVid(object):
    """Handles creating youtube embed videos"""
    def __init__(self, vurl):
        # super(YoutubeVid, self).__init__()
        self.vurl = vurl

        if 'list' in vurl:
            self.yt_id, self.embed = parse_playlist_url(self.vurl)
        else:
            self.yt_id, self.embed = parse_video_url(self.vurl)

    def __repr__(self):
        """Returns string representation of a youtube video."""
        return '<p><a href="{}"><img src="{}" alt="Link to YouTube video"</a></p>'.format(self.vurl)

import urllib2
import socket
import time
def get_youtube_thumbnail(playlist_url):
    host = socket.gethostbyname('youtube.com')
    playlist_url = playlist_url.replace('www.youtube.com', 'youtube.com')
    url = playlist_url.replace('youtube.com', host)
    print(url)
    # time.sleep(5)
    r = urllib2.urlopen(url).read()
    r = r.decode('UTF-8')
    r = r.encode('ascii', 'replace')
    r = r.split('pl-header-thumb')[1]
    r = r.split('<a')[0]
    r = r.split('//')[1]
    r = r.split('jpg')[0]
    r = "http://"+r+"jpg"
    return r

def youtube_embed(vurl):
    image_url = get_youtube_thumbnail(vurl)
    rv = '<p><a href="{}"><img src="{}" alt="Link to YouTube video"></a></p>'
    rv = rv.format(vurl, image_url)
    return rv



def csv_dict_reader(f_obj, delim='\t'):
    """Function will read our tsv/csv file into a list of dictionaries."""
    reader = csv.DictReader(f_obj, delimiter=delim)
    to_return = []
    for line in reader:
        to_return.append(line)
    return to_return


def load_csv(fname='names.tsv'):
    """Loads csv into list of dicts."""
    if not fname:
        if len(sys.argv) > 1:
            fname = sys.argv[1]

    with open(fname) as f_obj:
        series_info = csv_dict_reader(f_obj)

    return series_info

def build_page():
    """Builds the html page of series information."""
    series_info = load_csv()

    for item in series_info:
        item['markdown'] = sm.build_markdown(\
            item['series_alias'], item['series_full_name'])
        item['markdown'] += youtube_embed(item['youtube_url'])


    page = u'''<!DOCTYPE html><html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>Game Grump - Audio Edition!</title>
        <style type="text/css">
body {{
    background-color: white;
}}

#content {{
    width: 50%;
    margin-top: 0px;
    margin-bottom: 0px;
    margin-left: auto;
    margin-right: auto;
}}

        </style>
    </head><body><div id="content">
    <h1>Game Grumps as Audiobooks/Podcasts</h1>
    <p>Ever wanted to be able to listen to the humor and fun of Game Grumps while out and about? Now you can! This page links to mp3 versions of your favorite Game Grumps series, all free!</p>
    <p>You can download a series as a zip file containing each episode's audio, or you can download all the episodes of that series as one giant mp3 for continuous listening!</p>
    {}</div></body></html>'''

    page = page.format(
        ''.join([markdown.markdown(s['markdown']) for s in series_info]))
    return page.encode('utf-8')


    
if __name__ == '__main__':
    build_page()
    # print(build_page())



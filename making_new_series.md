Making a new series:
====================

To make a new MP3 series out of a Youtube playlist, as well as re-build the page listing all the videos, there's a simple two step process:

1. Download and create the new series with the program Python file `series_to_mp3.py`
2. Use the Python file `build_info_page.py` to re-build the page listing all the downloaded series.

Downloading the series:
-----------------------

The Python file `series_to_mp3.py` is called like this:

	series_to_mp3.py [series_alias] [series_url]

The `series_url` is the Youtube URL to the playlist, while `series_alias` is the directory that will be used to store all of the downloaded videos and the created mp3 files.

For example, let's say we want to make an audio series of the Game Grumps playthrough of Mega Man 7. First, we have to get the URL of the YouTube playlist for that series. In this case, the URL would be `https://www.youtube.com/playlist?list=PLRQGRBgN_EnoMqWxMpD6EUPwHxQOZdyVu`. Then we have to decide on the "alias" for the series, which will be the folder where these videos and mp3 files will be stored. A simple example in this case is `mega_man_7`. Now that we've chosen our `series_alias` and our `series_url`, we run the command:

	# Note that we put `python` in front of the command so that the Python
	# interpreter will run the file series_to_mp3.py
	python series_to_mp3.py mega_man_7 "https://www.youtube.com/playlist?list=PLRQGRBgN_EnoMqWxMpD6EUPwHxQOZdyVu"


Updating the List of Series
---------------------------

Once we've downloaded the new series and made it into all the mp3 forms we want, we have to add it to the `series.html` page. To do that, we add this series to the `names.tsv` file.

`names.tsv` is a tab separated variable file, and it contains information about all the downloaded series. The format goes like this (the string `tab-character` means a literal tab character):

	[series_alias]<tab-character>[series_full_name]<tab-character>[youtube_url]

So for Mega Man 7, we add a line with:

	mega_man_7<tab-character>Mega Man 7<tab-character>https://www.youtube.com/playlist?list=PLRQGRBgN_EnoMqWxMpD6EUPwHxQOZdyVu

Once we've added an entry for the newly created series, we generate the new series page like this:

	python build_info_page.py > series.html

And with that, we're done!


Youtube_series_as_audio
=======================

Synopsis
--------

	youtube_series_as_audio [-h] --alias ALIAS [--url URL]
	                        [--print PRINT] [--format FORMAT]

Description
-----------

`youtube_series_as_audio` downloads audio for a given Youtube series, then converts that audio into a single audiobook-style file. User must specify an `alias` and the `url` for the desired series. The alias is simple machine-usable name for the series, and the url is the url to the Youtube playlist which includes all videos for the series you desire. The `alias` is used by the program as the name of the folder in the current directory to store all audio files within. The structure of such a folder might look like this:

	./alias/
	├── audio
	│   ├── 00001__title_192k.mp3
	│   ├── 00002__title_192k.mp3
	│   ├── 00003__title_192k.mp3
	│   └── alias.zip
	├── complete_alias.mp3
	└── video
	    ├── 00001__title.m4a
		├── 00002__title.m4a
		└── 00003__title.m4a

As you can see, the newly created mp3 files are in `./alias/audio/`, as well as a zip file containing all the individual mp3 files. In `./alias/video` are all the original source files downloaded from YouTube. At the root of `./alias/` is a single mp3 file with all the audio from the individual mp3s, but joined into on single, continuous audio file.

Selecting a format of 'm4a' instead of 'mp3' will result in the same structure, but with all the `mp3` files replaced with `m4a` files.

Examples
--------


	youtube_series_as_audio --alias music_doc --url "https://www.youtube.com/playlist?list=PL728432FF85A30B53"
	youtube_series_as_audio --alias music_doc --url "https://www.youtube.com/playlist?list=PL728432FF85A30B53" --format m4a
	youtube_series_as_audio --alias music_doc --print

See Also
--------

[FFmpeg](https://www.ffmpeg.org/), [youtube-dl](https://rg3.github.io/youtube-dl/)

Author
------

Written by [Leland Batey](http://lelandbatey.com/).

Copyright
---------

Copyright © 2015 Leland Batey. License AGPLv3+: GNU AGPL version 3 or later <http://gnu.org/licenses/agpl.html>.  
This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.





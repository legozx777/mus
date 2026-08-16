# mus

## Description
This is my yt-dlp wrapper and music metadata manager. There is no gui and no plans to implement one, only a cli.

## Dependencies

#### Required: 

[Python3](https://www.python.org/downloads/) versions 3.11+ (tested with 3.11 and 3.13), other versions may or may not work.

[yt-dlp](https://github.com/yt-dlp/yt-dlp), [dotenv](https://github.com/theskumar/python-dotenv), [mutagen](https://github.com/quodlibet/mutagen)

```
python3 -m pip install -U yt-dlp dotenv mutagen
```

[ffmpeg and ffprobe binary](https://ffmpeg.org/download.html)

#### Optional but highly recommended:

[yt-dlp-ejs](https://github.com/yt-dlp/ejs) and deno (or other js runtime see [wiki](https://github.com/yt-dlp/yt-dlp/wiki/EJS))

```
python3 -m pip install -U "yt-dlp[default]"
```

## Usage

Copy the example files to their actual paths:

```
cp example.env .env
cp example.yt-dlp.conf yt-dlp.conf
```

Fill in MUS_BASE_FOLDER in .env, MUS_DEFAULT_PLAYLIST is optional

Fill in path to ffmpeg and ffprobe binary in yt-dlp.conf. Keep all paths in yt-dlp.conf absolute and dont use ~. If you are using yt-dlp-ejs uncomment --js-runtimes in yt-dlp.conf and put the program and path to the binary.

download() and search() will be chosen based on if the first argument is part of SUB_FOLDERS.

Folder structure:
```
Base Folder
+-- subfolder 1
|   +-- file1.mp3
|   +-- file2.mp3
|   +-- other files.whatever
+-- subfolder 2
|   +-- file1.mp4
|   +-- file2.mp4
|   +-- other files.whatever
+-- other folders
|   +-- other files.whatever
+-- other files.whatever

```

### download

`python3 /path/to/mus.py <subfolder> <url> <extra yt-dlp arguments>`

Youtube videos, playlists, albums, shows, and twitch streams are all accepted. Both the full url and just the identifier work.

#### Examples:
```
# All 3 will download the same video and nothing else, everything after the first "&" is removed
$ python3 mus.py d "https://www.youtube.com/watch?v=rVs0EdiVefM&list=PL9-3uiALO7exa6aF5as-bmK5qSFg30OUo&index=20"

$ python3 mus.py d "https://www.youtube.com/watch?v=rVs0EdiVefM"

$ python3 mus.py d "rVs0EdiVefM"


# Both will download the entire playlist generating an error file in logs/
$ python3 mus.py d "https://www.youtube.com/playlist?list=PL9-3uiALO7exa6aF5as-bmK5qSFg30OUo"

$ python3 mus.py d "PL9-3uiALO7exa6aF5as-bmK5qSFg30OUo"

# only download the 1,2,3 videos in the playlist
$ python3 mus.py d "PL9-3uiALO7exa6aF5as-bmK5qSFg30OUo" "-I '1:3'"
```

### search

`python3 /path/to/mus.py <search term> <options>`
The search folder will be the first item in the MUSD_FOLDERS list. The search term is case insensitive.

#### Options:
```
t - title:        search through titles instead of file names
a - artist:       search through artists
A - album:        search through albums
R - hard remove:  remove term anywhere in the name
r - soft remove:  remove only if term is at the beginning or end
e - ends:         removes if the first and last character match
b - backup:       write every file in the folder to a file in dname/
f - found:        write every file with the search term to a file in dfound/
l - length:       calculate lengths and display at the end
s - status:       display count, would-remove count, total and average size, and total and average length if selected
```
#### Examples:
```
# searchs through file names in SUB_FOLDERS[0] for "search term" and prints them
$ python3 mus.py "search term"

# searches through titles instead of file names
$ python3 mus.py "search term" t

# removes "rep" from beginning and end of file names
$ python3 mus.py rep r
    REP_REP_stuff.mp3 -> _REP_stuff.mp3
    REP_stuff_REP.mp3 -> _stuff_.mp3

# removes "rep" from beginning and end of titles
$ python3 mus.py rep tr
    REP_REP_stuff -> _REP_stuff
    REP_stuff_REP -> _stuff_

# Also automatically removes leading or trailing spaces
$ python3 mus.py "multi word" r
    multi word something else.mp3 -> something else.mp3
    something else multi word.mp3 -> something else.mp3

# Replaces double spaces after removal with single spaces (see 2nd)
$ python3 mus.py rep R
    stuff_REP_stuff.mp3 -> stuff__stuff.mp3
    stuff REP stuff.mp3 -> stuff stuff.mp3
    REP_REP_stuff.mp3 -> __stuff.mp3
    REP_stuff_REP.mp3 -> _stuff_.mp3

$ python3 mus.py [middle_is_ignored] er
    [stuff].mp3 -> stuff.mp3
    [ stuff ].mp3 -> stuff.mp3
```

## Bugs
None that I know of. If you find one or want something added tell me in person.

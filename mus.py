import os, sys, time, re
from dotenv import load_dotenv
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB

load_dotenv()
SUB_FOLDERS = [["d", "long"], ["rand", "stream", "useful"], ["print"]]
BASE_FOLDER = os.path.realpath(os.path.expanduser(os.getenv("MUS_BASE_FOLDER", "No base folder set")))
PROGRAM_FOLDER = os.path.dirname(os.path.realpath(__file__))

if not os.path.isdir(BASE_FOLDER):
    print("Base folder does not exist or is not set")
    sys.exit()

def download(subfolder, url="", extra=""):
    subfolder = subfolder.lower()
    url = url.removeprefix("=")
    if url.find("&") != -1:
        url = url[:url.find("&")]

    args = ["yt-dlp", "--config-location", os.path.join(PROGRAM_FOLDER, "yt-dlp.conf"), "-P", os.path.join(BASE_FOLDER, subfolder)]
    BITRATE = os.getenv("MUS_BITRATE", "128k")
    match subfolder:
        case "d" | "long":
            args += ["-o", "\"%(title)s.%(ext)s\"", "-x", "--audio-format", "mp3", "--audio-quality", BITRATE]
        case "rand" | "stream" | "useful":
            args += ["-f", "\"bv*[vcodec^=avc1][ext=mp4][height<=1080]+ba[ext=m4a]/b[vcodec^=avc1][ext=mp4][height<=1080]\""]
        case "randmp3":
            args[4] = os.path.join(BASE_FOLDER, "rand")
            args += ["-x", "--audio-format", "mp3", "--audio-quality", BITRATE]
        case "print":
            args = ["yt-dlp", "--flat-playlist", "--skip-download", "--playlist-reverse", "--print-to-file", "\"%(id)s - %(title)s\"", os.path.join(PROGRAM_FOLDER, "dname", "id-"+time.strftime("%Y%m%d")+".txt")]
        case _:
            print("Subfolder error - " + subfolder)
            return

    if url == "" and subfolder == "print":
        url = os.getenv("MUS_DEFUALT_PLAYLIST", "No default playlist set")
    if "youtube.com/watch?v=" in url or "youtube.com/playlist?list=" in url or "youtube.com/show/" in url:
        args.append(url)
    elif len(url) == 11: # yt video
        args.append("https://www.youtube.com/watch?v=" + url)
    elif len(url) == 13 or len(url) == 34 or len(url) == 41: # yt (13, 34 - playlist, 41 - album)
        args.append("https://www.youtube.com/playlist?list=" + url)
    elif "twitch.tv/videos" in url:
        args.pop(1)
        args.pop(1)
        args.append(url)
    elif len(url) == 10: # twitch stream
        args.pop(1)
        args.pop(1)
        args.append("https://www.twitch.tv/videos/" + url)
    else:
        print(f"url error - len={len(url)} - url={url}")
        return

    args.append(extra)
    errFile = ""
    if "playlist" in args[-2] or "show" in args[-2]:
        errFile = os.path.join(PROGRAM_FOLDER, "logs", f"{time.strftime('%Y%m%d-%H%M')}.txt")
        args.append(f"2>{errFile}")

    print(" ".join(args))
    os.system(" ".join(args))

    if errFile and os.path.getsize(errFile) == 0:
        print(f"Removing empty error file: {errFile}")
        os.remove(errFile)


def search(rep, options=""):
    doTitle        = "t" in options
    doArtist       = "a" in options
    doAlbum        = "A" in options
    doHardRemove   = "R" in options
    doSoftRemove   = "r" in options or doHardRemove
    doEnds         = "e" in options
    doBackup       = "b" in options
    doFound        = "f" in options
    doLength       = "l" in options
    doStatus       = "s" in options or doLength
    doHelp         = "h" in options

    if doTitle and (doArtist or doAlbum) or (doArtist and doAlbum):
        print("Title, Artist, and Album cannot go together")
        return
    if doEnds and doHardRemove:
        print("Ends and HardRemove are incompatable, converting HardRemove to SoftRemove")
        doHardRemove = False
    if doBackup:
        backupFile = open(os.path.join(PROGRAM_FOLDER, "dname", f"{time.strftime('%Y%m%d')}.txt"), "x", encoding="utf-8")
    if doFound:
        foundFile = open(os.path.join(PROGRAM_FOLDER, "dfound", f"{time.strftime('%Y%m%d')}-{rep}.txt"), "x", encoding="utf-8")

    dir = os.path.join(BASE_FOLDER, SUB_FOLDERS[0][0])
    rep = rep.lower()
    searched = 0
    matched  = 0
    b_or_e   = 0
    size     = 0
    length   = 0
    noURL    = 0
    noCover  = 0

    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        if not path.endswith(".mp3"):
            print(file, " - is not a mp3")
            continue
        if doBackup:
            backupFile.write(file+"\n")

        audio = ID3(path)
        if doTitle:
            if "TIT2" not in audio.keys():
                continue
            name = audio["TIT2"].text[0]
        elif doArtist:
            if "TPE1" not in audio.keys():
                continue
            name = audio["TPE1"].text[0]
        elif doAlbum:
            if "TALB" not in audio.keys():
                continue
            name = audio["TALB"].text[0]
        else: # default -> search by file name
            name = file.removesuffix(".mp3")

        #title = audio["TIT2"].text[0]
        #artist = audio["TPE1"].text[0]
        #if title.startswith(artist) or title.endswith(artist):
        #    print(file)
        #continue

        #if "TIT2" not in audio.keys():
        #    audio.add(TIT2(encoding=3, text=file.removesuffix(".mp3")))
        #    audio.save()
        #    print(name)
        #if "TXXX:purl" not in audio.keys():
        #    noURL += 1
        #    print(name)
        #if "APIC:" not in audio.keys() and "APIC:Album cover" not in audio.keys():
        #    noCover += 1
        #    print(name)

        searched += 1
        if rep in name.lower() or (doEnds and name.startswith(rep[0]) and name.endswith(rep[-1])):
            size += os.path.getsize(path)
            matched += 1
            newName = name
            if doFound:
                foundFile.write(file+"\n")
            if doLength:
               length += MP3(path).info.length

            if doEnds and doSoftRemove:
                newName = newName[1:-1].removeprefix("　").removeprefix(" ").removesuffix("　").removesuffix(" ")
            elif doHardRemove:
                newName = newName.replace(rep, "")
            else:
                if newName.lower().startswith(rep):
                    b_or_e += 1
                    if doSoftRemove:
                        newName = newName[len(rep):].removeprefix("　").removeprefix(" ")
                if newName.lower().endswith(rep):
                    b_or_e += 1
                    if doSoftRemove:
                        newName = newName[:-len(rep)].removesuffix("　").removesuffix(" ")

            if not (doSoftRemove and newName == name):
                if doArtist:
                    print(newName + "\t->\t" + file)
                else:
                    print(newName)

            if doSoftRemove:
                if doTitle:
                    audio["TIT2"] = TIT2(encoding=3, text=newName)
                    audio.save(v2_version=3)
                elif doArtist:
                    audio["TPE1"] = TPE1(encoding=3, text=newName)
                    audio.save(v2_version=3)
                elif doAlbum:
                    audio["TALB"] = TALB(encoding=3, text=newName)
                    audio.save(v2_version=3)
                else:
                    os.rename(path, os.path.join(dir, newName+".mp3"))

    if doHardRemove:
        for file in list(os.listdir(dir)): # removes double spaces in files, titles, and artists
            if not file.endswith(".mp3"):
                continue
            path = os.path.join(dir, file)
            audio = ID3(path)
            if "TIT2" in audio.keys() and "  " in audio["TIT2"].text[0]:
                newName = re.sub(r" {2,}", " ", audio["TIT2"].text[0])
                audio["TIT2"] = TIT2(encoding=3, text=newName)
                audio.save(v2_version=3)
            if "TPE1" in audio.keys() and "  " in audio["TPE1"].text[0]:
                newName = re.sub(r" {2,}", " ", audio["TPE1"].text[0])
                audio["TPE1"] = TPE1(encoding=3, text=newName)
                audio.save(v2_version=3)
            if "TALB" in audio.keys() and "  " in audio["TALB"].text[0]:
                newName = re.sub(r" {2,}", " ", audio["TALB"].text[0])
                audio["TALB"] = TALB(encoding=3, text=newName)
                audio.save(v2_version=3)
            if "  " in file:
                newName = re.sub(r" {2,}", " ", file)
                newPath = os.path.join(dir, newName)
                os.rename(path, newPath)
    if doStatus:
        print(f"\nsearched: {searched}")
        print(f"matched: {matched}")
        print(f"beginning or end count: {b_or_e}")
        if size > 0:
            print(f"total size: {size>>30}gb - {(size>>20) - (size>>30<<10)}mb")
            aveSize = size // count
            print(f"average size: {aveSize>>20}mb - {(aveSize>>10) - (aveSize>>20<<10)}kb")
        if length > 0:
            print(f"total length: {int(length//3600)}hr - {int(length%3600//60)}min - {int(length%60)}sec")
            aveLength = length // count
            print(f"average length: {int(aveLength%3600//60)}min - {int(aveLength%60)}sec")
        if noURL > 0:
            print(f"no url in metadata: {noURL}")
        if noCover > 0:
            print(f"no cover in metadata: {noCover}")
    if doHelp:
        print("\nOPTIONS:")
        print("t - title         - search through titles instead of file names")
        print("a - artist        - search through artists instead of file names")
        print("A - album         - search through albums instead of file names")
        print("R - hard remove   - remove term anywhere in the name")
        print("r - soft remove   - remove only if term is at the beginning or end")
        print("e - ends          - remove if and only if the first and last character match")
        print("b - backup        - write every file in the folder to a file in dname/")
        print("f - found         - write every file with the search term in the folder to a file in dfound/")
        print("l - length        - calculate lengths and display at the end")
        print("s - status        - display count, would-remove count, total and average size, ")
        print("                    and total and average length if selected")
        print("h - help          - display this message")
    if doBackup:
        backupFile.close()
    if doFound:
        foundFile.close()

if len(sys.argv) == 1:
    print("No arguments")
elif any(sys.argv[1].removesuffix("mp3") in i for i in SUB_FOLDERS):
    download(*sys.argv[1:])
else:
    search(*sys.argv[1:])


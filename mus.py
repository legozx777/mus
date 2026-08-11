import os, sys, time, re
from dotenv import load_dotenv
load_dotenv()

MUSD_FOLDERS = ["d", "long", "rand", "stream", "useful", "randmp3", "print"]
folder = os.getenv("MUSD_DOWNLOAD_FOLDER")
config = os.path.dirname(os.path.realpath(__file__))

if folder == None:
    print("No download folder set")
    sys.exit()

def download(subfolder, url):
    subfolder = subfolder.lower()

    if url.find("&") != -1:
        url = url[:url.find("&")]

    url = url.removeprefix("=")
    args = ["yt-dlp", "--config-location", os.path.join(config,"yt-dlp.conf"), "-P", os.path.join(folder,subfolder)]
    match subfolder:
        case "d" | "long":
            args += ["-o", "\"%(title)s.%(ext)s\"", "-x", "--audio-format", "mp3", "--audio-quality", "128k"]
        case "rand" | "stream" | "useful":
            args += ["-f", "\"bv*[vcodec^=avc1][ext=mp4][height<=1080]+ba[ext=m4a]/b[vcodec^=avc1][ext=mp4][height<=1080]\""]
        case "randmp3":
            args[4] = os.path.join(folder,"rand")
            args += ["-x", "--audio-format", "mp3", "--audio-quality", "128k"]
        case "print":
            args = ["yt-dlp", "--flat-playlist", "--skip-download", "--playlist-reverse", "--print-to-file", "\"%(id)s - %(title)s\"", os.path.join(config,"dname/id-"+time.strftime("%Y%m%d")+".txt")]
        case _:
            print("subfolder error - " + subfolder)
            return

    if "youtube.com/watch?v=" in url or "youtube.com/playlist?list=" in url or "youtube.com/show/" in url:
        args.append(url)
    elif len(url) == 11: # yt video
        args.append("https://www.youtube.com/watch?v=" + url)
    elif len(url) == 34 or len(url) == 41: # yt (34 - playlist, 41 - album)
        args.append("https://www.youtube.com/playlist?list=" + url)
    elif "twitch.tv/videos" in url:
        args.pop(1)
        args.pop(1)
        args.append(url)
    elif len(url) == 10: # twitch stream
        args.pop(1)
        args.pop(1)
        args.append("https://www.twitch.tv/videos/" + url)
    elif url == "" and subfolder == "print":
        args.append(os.getenv("MUSD_DEFUALT_PLAYLIST"))
        if args[-1] == None:
            print("No default playlist set")
            return
    else:
        print(f"url error - len={len(url)} - url={url}")
        return
    errFile = ""
    if "playlist" in args[-1] or "show" in args[-1]:
        errFile = os.path.join(config,f"logs/{time.strftime('%Y%m%d-%H%M')}.txt")
        args.append(f"2>{errFile}")
    print(" ".join(args))
    os.system(" ".join(args))
    if errFile and os.path.getsize(errFile) == 0:
        print(f"Removing empty error file: {errFile}")
        os.remove(errFile)


def search(rep, options=""):
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TALB

    doStrictRemove = "R" in options
    doRemove       = "r" in options or doStrictRemove
    doBackup       = "b" in options
    doFound        = "f" in options
    doLength       = "l" in options
    doTitle        = "t" in options
    doArtist       = "a" in options
    doAlbum        = "A" in options
    doEnds         = "e" in options
    doStatus       = "s" in options
    if doTitle and doArtist:
        print("Title and Artist cannot go together!")
        return
    if doBackup:
        backupFile = open(os.path.join(config,f"dname/{time.strftime('%Y%m%d')}.txt"), "x", encoding="utf-8")
    if doFound:
        foundFile = open(os.path.join(config,f"dfound/{time.strftime('%Y%m%d-%H%M')}-{rep}.txt"), "x", encoding="utf-8")
    dir = os.path.join(folder,MUSD_FOLDERS[0])
    rep = rep.lower()
    count = 0
    bOrE = 0
    size = 0
    length = 0
    noURL = 0
    noCover = 0
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        if not path.endswith(".mp3"):
            print(file, " - is not a mp3!")
            continue
        #audio = ID3(path)
        #title = audio["TIT2"].text[0]
        #artist = audio["TPE1"].text[0]
        #if title.startswith(artist) or title.endswith(artist):
        #    print(file)
        #continue

        if doBackup:
            backupFile.write(file+"\n")
        if doTitle: # search through titles
            audio = ID3(path)
            name = audio["TIT2"].text[0]
        elif doArtist: # search through artists
            audio = ID3(path)
            name = audio["TPE1"].text[0]
        elif doAlbum: # search through artists
            try:
                audio = ID3(path)
                name = audio["TALB"].text[0]
            except:
                continue
        else: # default -> search by file name
            name = file.removesuffix(".mp3")
        #try:
        #    a = ID3(path)["TIT2"]
        #except:
        #    audio = ID3(path)
        #    audio.add(TIT2(encoding=3, text=file.removesuffix(".mp3")))
        #    audio.save()
        #    print(name)
        #try:
        #    a = ID3(path)["TXXX:purl"]
        #except:
        #    noURL += 1
        #    print(name)
        #try:
        #    a = ID3(path)["APIC:Album cover"]
        #except:
        #    try:
        #        a = ID3(path)["APIC:"]
        #    except:
        #        noCover += 1
        #        print(name)

        if rep in name.lower() or (doEnds and rep[0] == name[0] and rep[-1] == name[-1]):
            if doFound:
                foundFile.write(file+"\n")
            newName = name
            if doEnds and doRemove:
                newName = newName[1:-1].removeprefix("　").removeprefix(" ").removesuffix("　").removesuffix(" ")
            elif doStrictRemove:
                newName = newName.replace(rep,"")
            else:
                if name[:len(rep)].lower() == rep: # rep at the beginning
                    bOrE += 1
                    if doRemove:
                        newName = newName[len(rep):].removeprefix("　").removeprefix(" ")
                if name[-len(rep):].lower() == rep: # rep at the end
                    bOrE += 1
                    if doRemove:
                        newName = newName[:-len(rep)].removesuffix("　").removesuffix(" ")

            if not (doRemove and newName == name):
                # only dont print when remove and newName == name
                if doArtist:
                    print(newName + "\t->\t" + file)
                else:
                    print(newName)
            size += os.path.getsize(path)
            count += 1
            if doLength:
               length += MP3(path).info.length
            if doRemove:
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
    if doStrictRemove:
        for file in list(os.listdir(dir)): # removes double spaces in files, titles, and artists
            if not file.endswith(".mp3"):
                continue
            path = os.path.join(dir, file)
            audio = ID3(path)
            if "  " in audio["TIT2"].text[0]:
                newName = re.sub(r" {2,}", " ", audio["TIT2"].text[0])
                audio["TIT2"] = TIT2(encoding=3, text=newName)
                audio.save(v2_version=3)
            if "  " in audio["TPE1"].text[0]:
                newName = re.sub(r" {2,}", " ", audio["TPE1"].text[0])
                audio["TPE1"] = TPE1(encoding=3, text=newName)
                audio.save(v2_version=3)
            if "  " in file:
                newName = re.sub(r" {2,}", " ", file)
                newPath = os.path.join(dir, newName)
                os.rename(os.path.join(dir, file), newPath)
            try:
                if "  " in audio["TALB"].text[0]:
                    newName = re.sub(r" {2,}", " ", audio["TALB"].text[0])
                    audio["TALB"] = TALB(encoding=3, text=newName)
                    audio.save(v2_version=3)
            except:
                pass
    if doStatus:
        print("\ncount: " + str(count))
        print("beginning or end count: " + str(bOrE))
        if size > 0:
            print("total size: " + str(size>>30) + "gb - " + str((size>>20) - (size>>30<<10)) + "mb")
            perSize = size // count
            print("perSize: " + str(perSize>>20) + "mb - " + str((perSize>>10) - (perSize>>20<<10)) + "kb")
        if length > 0:
            print("total length: " + str(int(length//3600)) + "hr - " + str(int(length%3600//60)) + "min - " + str(int(length%60)) + " sec")
            perLength = length // count
            print("perLength: " + str(int(perLength%3600//60)) + "min - " + str(int(perLength%60)) + " sec")
        if noURL > 0:
            print("no url in metadata: " + str(noURL))
        if noCover > 0:
            print("no cover in metadata: " + str(noCover))
    if doBackup:
        backupFile.close()
    if doFound:
        foundFile.close()

if len(sys.argv) == 1:
    print("No arguments")
elif sys.argv[1] in MUSD_FOLDERS:
    download(sys.argv[1],sys.argv[2])
elif len(sys.argv) == 3:
    search(sys.argv[1],sys.argv[2])
else:
    search(sys.argv[1])






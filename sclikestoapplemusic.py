#!/usr/bin/python3.3
# -*- coding: utf-8 -*-

clientID = "<XXX your soundcloud App ID>"
client_secret = "<XXX your soundcloud App secret>"
username = "<XXX your soundcloud username>"
password = "<XXX your soundcloud password>"

import soundcloud
import json
import requests
import struct
import time
import struct
import requests
import re, string
import sys
import datetime
import locale
import os.path
import urllib
from html.parser import HTMLParser
from datetime import date, timedelta
from pathlib import Path

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

pattern = re.compile('[^\w\d\.]+',re.UNICODE)
pattern2 = re.compile('\[.*\] |^\d{1,3}|ft.*|feat.*|\(?Feat.*(?=\()|.?Out now.*|Preview|Snippet|snippet|(OUT NOW)|(Original Mix)|(Original)|\(((?!(mix|edit)\)).)*\)', re.IGNORECASE | re.UNICODE)
pattern3 = re.compile('\[.*\] |^\d{1,3}|ft.*|feat.*|\(?Feat.*(?=\()|.?Out now.*|Preview|Snippet|snippet|(OUT NOW)|(Original Mix)|(Original)|\(((?!\)).)*\)', re.IGNORECASE | re.UNICODE)

client = soundcloud.Client(client_id=clientID,
                           client_secret=client_secret,
                           username=username,
                           password=password)

def retrieve_itunes_identifier(artist, title):
    if "&" in artist:
        if len(artist.split("&")) == 2:
            artist2 = artist.split("&")[1] + " " + artist.split("&")[0]
            artist2 = pattern2.sub(' ', artist2)
            artist2 = pattern.sub(' ', artist2)
            artist2 = " ".join(artist2.split()).lower()

    title_no_mix = pattern3.sub(' ', title)
    title_mix = pattern2.sub(' ', title)
    artist = pattern2.sub(' ', artist)

    title_no_mix = pattern.sub(' ', title_no_mix)
    title_mix = pattern.sub(' ', title_mix)
    artist_temp = artist

    artist = pattern.sub(' ', artist)
    title_no_mix = " ".join(title_no_mix.split())
    title_mix = " ".join(title_mix.split())
    artist = " ".join(artist.split()).lower()

    url = "https://itunes.apple.com/search?term=" + urllib.parse.quote((artist + " " + title_mix).encode("utf-8")) + "&media=music&sort=recent&country=de&lang=de_de&explicit=yes"
    request = urllib.request.Request(url)

    try:
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode('utf-8'))
        songs = data["results"]

        # Attempt to match by title & artist
        for song in songs:

            trackname = song["trackName"].lower()
            trackname2 = song["trackCensoredName"].lower()
            artistname = song["artistName"].lower()

            trackname = pattern2.sub(' ', trackname)
            trackname2 = pattern2.sub(' ', trackname2)
            artistname = pattern2.sub(' ', artistname)

            trackname = pattern.sub(' ', trackname)
            trackname2 = pattern.sub(' ', trackname2)
            artistname = pattern.sub(' ', artistname)

            trackname = " ".join(trackname.split())
            trackname2 = " ".join(trackname2.split())
            artistname = " ".join(artistname.split())

            #print("iTunes Artist|Soundcloud Artist: " + artistname + " | " + artist)
            #print("iTunes Title|Soundcloud Title: " + trackname2 + " | " + title_mix)

            if trackname2.lower() == title_mix.lower() and (artistname.lower() in artist.lower() or artist.lower() in artistname.lower() or artistname.lower() in artist2.lower() or artist2.lower() in artistname.lower()):
                return song["trackId"]
    except:
        # We don't do any fancy error handling.. Just return None if something went wrong
        return None

def construct_request_body(timestamp, itunes_identifier):
    hex = "61 6a 43 41 00 00 00 45 6d 73 74 63 00 00 00 04 55 94 17 a3 6d 6c 69 64 00 00 00 04 00 00 00 00 6d 75 73 72 00 00 00 04 00 00 00 81 6d 69 6b 64 00 00 00 01 02 6d 69 64 61 00 00 00 10 61 65 41 69 00 00 00 08 00 00 00 00 11 8c d9 2c 00"

    body = bytearray.fromhex(hex);
    body[16:20] = struct.pack('>I', timestamp)
    body[-5:] = struct.pack('>I', itunes_identifier)
    return body


def add_song(itunes_identifier):
    data = construct_request_body(int(time.time()), itunes_identifier)

    headers = {
        "X-Apple-Store-Front" : "143443-4,32",
        "Client-iTunes-Sharing-Version" : "3.13",
        "Accept-Language" : "de-DE;q=1.0, en-DE;q=0.9",
        "Client-Cloud-DAAP-Version" : "1.3/iTunes-12.6.0.95",
        "Accept-Encoding" : "gzip",
        "X-Apple-itre" : "0",
        "Client-DAAP-Version" : "3.13",
        "User-Agent" : "iTunes/12.6 (Macintosh; OS X 10.12.3) AppleWebKit/602.4.8",
        "Connection" : "keep-alive",
        "Content-Type" : "application/x-dmap-tagged",
        # Replace the values of the next three headers with the values you intercepted
        "X-Dsid" : "<XXX your Dsid>",
        "Cookie" : "<XXX your cookie>",
        "X-Guid" : "<XXX your Guid>",
        "Content-Length" : "77"
    }

    request = urllib.request.Request("https://ld-4.itunes.apple.com/WebObjects/MZDaap.woa/daap/databases/1/cloud-add", data, headers)
    urllib.request.urlopen(request)

def get_id(url):
    try:
        parts = urllib.parse.urlsplit(url)
        if parts.hostname == 'itunes.apple.com':
            idstr = parts.path.rpartition('/')[2] # extract 'id123456'
            if idstr.startswith('id'):
                try:
                    return int(idstr[2:])
                except ValueError: pass
    except AttributeError: pass

def resolve_itunes_id(artist, title, id):
    #if "/album/" in id:

    artist2 = ''

    if "&" in artist:
        if len(artist.split("&")) == 2:
            artist2 = artist.split("&")[1] + " " + artist.split("&")[0]
            artist2 = pattern2.sub(' ', artist2)
            artist2 = pattern.sub(' ', artist2)
            artist2 = " ".join(artist2.split()).lower()

    title_no_mix = pattern3.sub(' ', title)
    title_mix = pattern2.sub(' ', title)
    artist = pattern2.sub(' ', artist)

    title_no_mix = pattern.sub(' ', title_no_mix)
    title_mix = pattern.sub(' ', title_mix)
    artist = pattern.sub(' ', artist)

    title_no_mix = " ".join(title_no_mix.split())
    title_mix = " ".join(title_mix.split())
    artist = " ".join(artist.split()).lower()

    url = "https://itunes.apple.com/lookup?id=" + str(id) + "&entity=song&media=music&sort=recent&country=de&lang=de_de&explicit=yes"
    request = urllib.request.Request(url)

    try:
        response = urllib.request.urlopen(request)

        data = json.loads(response.read().decode('utf-8'))

        songs = data["results"]

        songs = [i for i in songs if i["wrapperType"] == "track"]

        # Attempt to match by title & artist
        for song in songs:
            if song["wrapperType"] == "track":

                trackname = song["trackName"].lower()
                trackname2 = song["trackCensoredName"].lower()
                artistname = song["artistName"].lower()

                trackname = pattern2.sub(' ', trackname)
                trackname2 = pattern2.sub(' ', trackname2)
                artistname = pattern2.sub(' ', artistname)

                trackname = pattern.sub(' ', trackname)
                trackname2 = pattern.sub(' ', trackname2)
                artistname = pattern.sub(' ', artistname)

                trackname = " ".join(trackname.split())
                trackname2 = " ".join(trackname2.split())
                artistname = " ".join(artistname.split())

                #print("iTunes Artist|Soundcloud Artist: " + artistname + " | " + artist)
                #print("iTunes Title|Soundcloud Title: " + trackname2 + " | " + title_mix)

                if trackname2.lower() == title_mix.lower() and (artistname.lower() in artist.lower() or artist.lower() in artistname.lower() or artistname.lower() in artist2.lower() or artist2.lower() in artistname.lower()):
                    return song["trackId"]

        return songs[0]["trackId"]

    except Exception as e:
        print(e.message)
        return None

def import_soundcloud():
    tracks = client.get('/me/favorites')

    for track in tracks:
       if track.duration < 720000:
           if '[' in track.title and track.title.index('[') > 5:
               description = track.title.strip().split('[')[0].split('-')
           elif '|' in track.title:
                          description = track.title.strip().split('|')[0].split(' - ')
           else:
               description = track.title.strip().split(' - ')

           if len(description) >= 2:
               title, artist = description[1].lower().strip(), description[0].strip()
           else:
               title = description[0]
               artist = track.user['username']

           itunes_identifier = None
           feat_replace = re.compile(re.escape('ft.'), re.IGNORECASE)
           feat_replace.sub(title, 'feat.')
           title = title.replace("dont","don\'t")

           if not track.purchase_url is None:
               buy_id = get_id(track.purchase_url)
               if not buy_id is None:
                   itunes_identifier = resolve_itunes_id(artist, title, buy_id)

           if itunes_identifier is None:
               itunes_identifier = retrieve_itunes_identifier(artist, title)

           if not itunes_identifier is None:
               print("{} => {}".format(track.title, itunes_identifier))

               try:
                   add_song(int(itunes_identifier))
                   print("Successfuly inserted a track!")

                   try:
                       client.delete('/me/favorites/%d' % track.id)
                       print("Successfuly removed a track from soundcloud favorites!")
                   except Exception as ex:
                       print("Error removing track from soundcloud favorites: " + str(ex))
                   # Try playing with the interval here to circumvent the API rate limit
                   time.sleep(30)
               except Exception as e:
                   print("Something went wrong while inserting " + str(itunes_identifier) + " : " + str(e))
           else:
               print("{} => Not Found".format(track.title))
       else:
           print("Track is very long and probably a mix: {}".format(track.title))


print("### Importing Soundcloud favorites for user " + username + " ###")
import_soundcloud()

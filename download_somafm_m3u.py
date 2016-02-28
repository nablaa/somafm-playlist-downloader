#!/usr/bin/env python2

import os
from xml.etree import ElementTree as ET
import requests

SOMAFM_URL = "https://api.somafm.com/channels.xml"


def main():
    channels = download_somafm_channel_data()
    for channel in channels:
        title, pls = create_playlist_from_channel_data(channel)
        m3u = pls_to_m3u(pls)
        write_playlist_file(title, m3u)


def download_somafm_channel_data():
    xml = requests.get(SOMAFM_URL).content
    tree = ET.fromstring(xml)
    return tree.findall(".//channel")


def create_playlist_from_channel_data(channel):
    title = channel.find("title").text
    pls = channel.find("fastpls[@format='mp3']").text
    pls = select_best_playlist_url(pls)
    return title, pls


def select_best_playlist_url(pls):
    basename, _ = os.path.splitext(pls)
    higher_quality_pls = basename + "130.pls"
    response = requests.get(higher_quality_pls)
    if response.status_code == 200:
        return response.content
    return requests.get(pls).content


def pls_to_m3u(pls):
    streams = [line.split("=")[1]
               for line in pls.splitlines()
               if line.startswith("File") and "=" in line]

    return "\n".join(streams) + "\n"


def write_playlist_file(title, m3u):
    filename = "SomaFM_" + title.replace(" ", "-") + ".m3u"
    with open(filename, "w") as f:
        print "Writing '%s'" % filename
        f.write(m3u)


if __name__ == "__main__":
    main()

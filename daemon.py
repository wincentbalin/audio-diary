#!/usr/bin/env python
"""This is a daemon, which uses Whisper.cpp to convert speech to text and rebuilds a RSS feed afterwards"""

from __future__ import print_function, unicode_literals, with_statement
import sys
import os
import codecs
import shutil
import subprocess
import time
from datetime import datetime
from mimetypes import guess_type
from tempfile import gettempdir
from urlparse import urljoin
from xml.sax.saxutils import escape


WCPP = os.path.join(os.path.dirname(__file__), 'main')
#MODEL = os.path.join(os.path.dirname(__file__), 'ggml-base.bin')
MODEL = os.path.join(os.path.dirname(__file__), 'ggml-medium.bin')
DEVNULL = open(os.devnull, 'w')
NONMEDIA_EXTS = frozenset(['.tmp', '.txt', '.xml', '.xsl'])
RFC822_DATETIME = '%a, %d %b %Y %H:%M:%S %z'
STEM_DATETIME = '%Y-%m-%dT%H-%M-%S-%f'

FEED_INDEX = 'index.xml'  # Has the last non-media extension!
FEED_STYLESHEET = 'tohtml5.xsl'
FEED_HEAD = '''<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet type="text/xsl" href="{0}"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Audio diary</title>
<description>An audio diary</description>
<link>{1}</link>
<atom:link href="{2}" rel="self" type="application/rss+xml"/>
<lastBuildDate>{3}</lastBuildDate>'''
FEED_ITEM = '''<item>
<title>{0}</title>
<link>{1}</link>
<guid>{1}</guid>
<pubDate>{2}</pubDate>
<enclosure url="{3}" type="{4}" length="{5}"/>
</item>'''
FEED_TAIL = '''</channel>
</rss>'''


def get_build_date():
    return datetime.now().strftime(RFC822_DATETIME)


def get_pub_date(stem):
    return datetime.strptime(stem, STEM_DATETIME).strftime(RFC822_DATETIME)


def convert_media_files(files):
    for audiofile in files:
        # Convert file to a Whisper.cpp-compatible format using ffmpeg
        stem, _ = os.path.splitext(audiofile)
        basestem = os.path.basename(stem)
        wavfile = os.path.join(gettempdir(), basestem + '.wav')
        subprocess.call(['ffmpeg', '-hide_banner', '-loglevel', 'warning',
                         '-y', '-i', audiofile, '-ar', '16000', '-ac', '1',
                         '-c:a', 'pcm_s16le', wavfile])
        # Convert speech to text using Whisper.cpp
        subprocess.call([WCPP, '-l', 'auto', '-otxt', '-of', stem,
                         '-m', MODEL, '-f', wavfile], stdout=DEVNULL,
                         stderr=subprocess.STDOUT)
        # Clean up
        os.remove(wavfile)


def build_feed(feed_dir, feed_url):
    feed_path = os.path.join(feed_dir, FEED_INDEX)
    feed_index_url = urljoin(feed_url, FEED_INDEX)
    # Copy stylesheet
    stylesheet_src = os.path.join(os.path.dirname(__file__), FEED_STYLESHEET)
    stylesheet_dst = os.path.join(feed_dir, FEED_STYLESHEET)
    if not os.path.exists(stylesheet_dst):
        shutil.copyfile(stylesheet_src, stylesheet_dst)
    # Create RSS feed
    feed_stems = []
    feed_media = {}
    for fn in os.listdir(feed_dir):
        stem, ext = os.path.splitext(fn)
        if ext not in NONMEDIA_EXTS:
            feed_media[stem] = fn
            feed_stems.append(stem)
    with codecs.open(feed_path, 'w', encoding='utf-8') as feed_file:
        print(FEED_HEAD.format(FEED_STYLESHEET, feed_url, feed_index_url,
                               get_build_date()), file=feed_file)
        for stem in sorted(feed_stems, reverse=True):
            text_path = os.path.join(feed_dir, stem + '.txt')
            try:
                with codecs.open(text_path, 'r', encoding='utf-8') as text_file:
                    text = ' '.join(map(unicode.strip, text_file.readlines()))
            except IOError:
                continue
            media_path = feed_media[stem]
            content_type, _ = guess_type(media_path, strict=True)
            if content_type is None:
                content_type = 'application/octet-stream'
            media_size = os.path.getsize(os.path.join(feed_dir, media_path))
            item_params = escape(text), urljoin(feed_url, stem + '.txt'), \
                          get_pub_date(stem), urljoin(feed_url, media_path), \
                          content_type, media_size
            print(FEED_ITEM.format(*item_params), file=feed_file)
        print(FEED_TAIL, file=feed_file)


def main():
    # We run as nobody.nogroup
    if len(sys.argv) < 3:
        raise SystemExit('Usage: daemon.py feed_dir feed_url')
    feed_dir = sys.argv[1]
    feed_url = sys.argv[2]
    time.tzset()
    # Find new audio files and convert them
    while True:
        # Collect not yet converted audio files
        unconverted = set()
        for fn in os.listdir(feed_dir):
            stem, ext = os.path.splitext(os.path.join(feed_dir, fn))
            if ext in NONMEDIA_EXTS:
                continue
            if not os.path.exists(stem + '.txt'):
                unconverted.add(stem + ext)
        # Exit the loop if there is no work to do
        if not unconverted:
            break
        convert_media_files(unconverted)
        build_feed(feed_dir, feed_url)


if __name__ == '__main__':
    main()


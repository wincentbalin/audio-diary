#!/usr/bin/env python
"""Receive an e-mail from stdin and enqueue audio file(s) into a directory"""

from __future__ import print_function, unicode_literals, with_statement
import sys
import os
import email
from datetime import datetime
from string import maketrans, translate


def main():
    # We run as nobody.nogroup
    if len(sys.argv) < 2:
        raise SystemExit('Usage: enqueue.py feed_dir')
    feed_dir = sys.argv[1]
    transtable = maketrans(':.', '--')
    msg = email.message_from_file(sys.stdin)
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type[:6] != 'audio/':
            continue
        filename = part.get_filename()
        _, ext = os.path.splitext(filename)
        text = ext + '.tmp'
        basename = datetime.now().isoformat().translate(transtable)
        temp_filename = os.path.join(feed_dir, basename + text)
        with open(temp_filename, 'wb') as audiofile:
            audiofile.write(part.get_payload(decode=True))
        os.chmod(temp_filename, 0644)
        os.rename(temp_filename, os.path.join(feed_dir, basename + ext))


if __name__ == '__main__':
    main()


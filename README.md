# Audio Diary

This is a frugal audio diary, which receives e-mails with attached
voice messages, performs speech recognition, creates a RSS feed
from the results, and adds a stylesheet to create a web page
from the feed.

## Installation

1. Prepare local directory that is reachable on your web server; this will be the feed directory of the diary; it should be owned by user `nobody` and group `nogroup`; note the URL and the absolute path of the directory
2. Place files `enqueue.py`, `daemon.py`, and `tohtml5.xsl` into a separate directory; the user `nobody` should be able to execute files there; install [_whisper.cpp_](https://github.com/ggerganov/whisper.cpp) into the same directory, also download the medium model to the same location; install `ffmpeg` to convert audio files to the format preferred by _whisper.cpp_ (for example on Debian: `apt-get install ffmpeg`)
3. In file `aliases`, replace _username_ with the user part of the e-mail address you will send e-mails with audio attachments to, and the _/feed_dir_ with the absolute path of the feed directory; append the resulting file to the system-wide `aliases` file (for example on Debian: `/etc/aliases`) and update the mail aliases database by executing `newaliases`
4. In file `audiodiary.service`, replace _/feed_dir_ with the absolute path of the feed directory, and _https://feed_url_ with it's URL; copy the file to the `systemd` services directory (for example on Debian: `/etc/systemd/system`), start it using command `systemctl start audiodiary` and test the setup by sending an e-mail with audio attachment to the e-mail address of your choice
5. Persist the setup by executing command `systemctl enable audiodiary`
6. Access the URL you entered in step 4; if you see list of files and your test file, everything works as expected; access the file `index.xml` therein; you should see a web page with your test file embedded and with the recognised text beside it
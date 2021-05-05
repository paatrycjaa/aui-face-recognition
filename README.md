# aui-face-recognition

## Setup
+ install nginx according to https://obsproject.com/forum/resources/how-to-set-up-your-own-private-rtmp-server-using-nginx.50/
+ run nginx with `sudo /usr/local/nginx/sbin/nginx`
+ install `OBS Studio` and `VLC`
+ run `OBS Studio`, add a webcam (video capture device) in `sources`, start the stream (set custom server, url: `rtmp://localhost/live/test`)
+ install `ffmpeg` with `sudo apt install ffmpeg`
+ install python requirements
+ run `test_forward.py`
+ run VLC, go to `media` > `Open Network Stream` and set url to `rtmp://localhost/live/test2`

# IP Cam using Telegram as DDNS

**Based on: Raspberry Pi 2 Model B + camera module, Raspbian, Python 3.2**  
Setting: Pi → router → modem (which give the router a publicly-accessible IP address)

You will learn:
- to stream MJPEG video from Raspberry Pi
- to open a port through the router to Raspberry Pi
- to setup a Telegram bot on Raspberry Pi and use it to communicate the router's IP address to you, so you can view the video stream away from home

This system is intended for use by one person only. Its purpose is educational.

## First ...

Go to this project's [scripts](https://github.com/nickoala/ipcam/tree/master/scripts) directory, copy to your Pi these shell scripts:

- `cs`: **C**am **S**tream - start and stop the streaming server
- `pf`: **P**ort **F**orward - create and delete port-forward to Raspberry Pi
- `lspf`: List all port-forward to Raspberry Pi
- `ipaddr`: Give all relevant IP addresses

Use `chmod` to make them executable, then move them to `/usr/local/sbin`, so you can execute them like normal Linux commands.

They won't work yet, because we have not installed the necessary software.

## Install mjpg_streamer

```
sudo apt-get update
sudo apt-get upgrade
sudo rpi-update
cd ~
sudo apt-get install subversion libjpeg8-dev imagemagick libav-tools cmake
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer-experimental
make
```

Run:
```
./mjpg_streamer -i "./input_raspicam.so -fps 5" -o "./output_http.so"
```

You should be able to view the stream by pointing your browser or VLC player to:  
`http://<your Raspi's IP>:8080/?action=stream`

... mjpg_streamer options ...

To ease the process of starting and stopping the streaming server, I give you the `cs` script, which you should have already put into `/usr/local/sbin`. With `mjpg_streamer` installed, try these self-explanatory commands: `cs start`, `cs stop`, `cs status`. They respectively run, kill, and check the `mjpg_streamer` command. Edit the `cs` script to adjust streaming options to your liking.

-----
I have also considered VLC and Motion as the streaming software, but they generally stream VERY slowly (i.e. VERY long lag time) over 4G networks. They don't provide an easy way to control parameters, like frame rate and picture quality, that affect bandwidth usage.

Formats other than MJPEG may stream faster, but cannot be easily viewed on a browser and may not be viewable on all mobile devices. MJPEG may be primitive, but it is the most universal.

Above factors combined, mjpg_streamer is the best option.

## More coming ...

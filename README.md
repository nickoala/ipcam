# IP Cam using Telegram as DDNS

**Based on: Raspberry Pi 2 Model B + camera module, Raspbian, Python 3.2**  
Setting: Pi → router → modem (which give the router a publicly-accessible IP address)

You will learn:
- to stream MJPEG video from Raspberry Pi
- to open a port through the router to Raspberry Pi
- to setup a Telegram bot on Raspberry Pi and use it to communicate the router's IP address to you, so you can view the video stream away from home

This system is intended for use by one person only. Its purpose is educational.

## First ...

`sudo raspi-config` and select **Enable Camera**. Then, finish and **reboot**.

Go to the [scripts](https://github.com/nickoala/ipcam/tree/master/scripts) directory, copy to your Pi these shell scripts:

- `cs`: **C**am **S**tream - start and stop the streaming server
- `pf`: **P**ort **F**orward - create and delete port-forwards to Raspberry Pi
- `lspf`: List all port-forwards to Raspberry Pi
- `ipaddr`: Extract all relevant IP addresses

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

If you find it slow, [a lot of options](https://github.com/foosel/OctoPrint/wiki/MJPG-Streamer-configuration) [can be set from the command-line](http://skillfulness.blogspot.hk/2010/03/mjpg-streamer-documentation.html).

To ease the process of starting and stopping the streaming server, I give you the `cs` script, which you should have already put into `/usr/local/sbin`. With `mjpg_streamer` installed, try these self-explanatory commands: `cs start`, `cs stop`, `cs status`. They respectively run, kill, and check the `mjpg_streamer` command. Edit the `cs` script to adjust streaming options to your liking.

-----
I have also considered VLC and Motion as the streaming software, but they generally stream VERY slowly (i.e. VERY long lag time) over 4G networks. They don't provide an easy way to control parameters, like frame rate and picture quality, that affect bandwidth usage.

Formats other than MJPEG may stream faster, but cannot be easily viewed on a browser and may not be viewable on all mobile devices. MJPEG may be primitive, but it is the most universal.

Above factors combined, mjpg_streamer is the best option.

## Install miniupnpc

```
sudo apt-get install miniupnpc
```

After this, you should have the `upnpc` command installed. `upnpc` stands for Universal Plug-n-Play Client, able to list, create, and delete port-forwards in the router. Port-forward basically links a router's port with a Raspberry Pi's port. For example, if you forward the router's port `54321` to Pi's port `8080`, when someone visits the router on port `54321`, he will be led to Pi's port `8080`. If `mjpg_streamer` is also running, the video stream is exposed (which is what you want from an IP cam).

I would not detail the `upnpc` command here. It is part of the [MiniUPnP project](http://miniupnp.free.fr/). [Read](http://www.makelinux.com/man/1/U/upnpc) [more](http://superuser.com/questions/192132/how-to-automatically-forward-a-port-from-the-router-to-a-mac-upnp) [about it](https://forum.transmissionbt.com/viewtopic.php?t=15840) [if you want](http://po-ru.com/diary/using-upnp-igd-for-simpler-port-forwarding/).

With `upnpc` installed, try:

```
pf 54321 8080  # create port forward
lspf           # check what you have done
ipaddr         # see relevant IP addresses
```

The last command extracts three IP addresses:

1. Pi's internal IP address
2. router's external IP address
3. router's IP address as seen by the outside world

The command `pf 54321 8080` creates a linking between (1) and (2), exposing the video stream through the router. For the stream to be seen away from home, IP address (2) and (3) **must be identical**.

Now, make sure your cell phone is **not on the same LAN** as the Pi. On the cell phone, open a browser or VLC player, point it to:  
`http://<Router's Public IP>:54321/?action=stream`

If the router's IP address stays constant, we could stop right now, and the IP cam finished. As the saying goes, however, change is the only constant, especially your router's IP address. We need a way to communicate the most current IP address.

The usual way to do this is to get a domain name, and use a Dynamic Domain Name Service (DDNS) to keep the IP address up-to-date. Here, I choose another approach - **use Telegram to "simulate" a DDNS**.

Before moving on, remember to delete the port-forward to hide the video stream from the outside world:

```
pf delete 54321  # remove port forward
lspf             # check
```

## Get a Telegram Bot account

I have written a lot about [Telegram Bot API](https://core.telegram.org/bots):

- [How to setup a Telegram Bot on Raspberry Pi](http://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/)
- **[telepot](https://github.com/nickoala/telepot)**: a Python wrapper for Telegram Bot API

Please create a bot account by [chatting with BotFather](https://core.telegram.org/bots), and know two things:

- your bot's token
- your own Telegram user ID

For the latter, you really have to familiarize yourself with [telepot](https://github.com/nickoala/telepot). You will need it in the next step, too. Install it now:

```
sudo apt-get install python-pip
sudo pip install telepot
```

## Run the bot

Copy to the Pi the Python script, [ipcam.py](https://github.com/nickoala/ipcam/blob/master/ipcam.py). It is a Telegram bot that does the following:

- On startup, it starts `mjpg_streamer` by calling the `cs` script. No router port is open yet, so the video stream is not accessible from the outside.
- On receiving the `/open` command (via Bot API), it opens a port (default: 54321) through the router and text you the public URL with which you may view the video stream.
- On receiving the `/close` command, it closes the port on the router, so the video stream is no longer accessible from the outside.
- It verifies the user ID of each message received, so only the designated user may control it.

Run it by:

```
python3.2 ipcam.py <token> <user_id>
```

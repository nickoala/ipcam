import sys
import time
import subprocess
import telepot

"""
$ python ipcam.py <token>

Use Telegram as a DDNS service, making an IP cam accessible over the internet.

Accept two commands:
/open: open a port through the router to the video stream, and send the URL
/close: close the external port
"""

cs = '/usr/local/sbin/cs'
pf = '/usr/local/sbin/pf'
ipaddr = '/usr/local/sbin/ipaddr'

EXTERNAL_PORT = 54321
INTERNAL_PORT = 8080  # mjpg_streamer default

def handle(msg):
    global pf, ipaddr

    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type != 'text':
        print 'Invalid %s message from %d' % (content_type, chat_id)
        return

    if chat_id != USER_ID:
        print 'Unauthorized user: %d' % chat_id
        return

    command = msg['text'].strip().lower()

    if command == '/open':
        # port forward
        subprocess.call([pf, str(EXTERNAL_PORT), str(INTERNAL_PORT)])

        # extract IP addresses
        out = subprocess.check_output([ipaddr])

        # Output:
        # Internal=zzz.zzz.zzz.zzz
        # External=zzz.zzz.zzz.zzz
        # Public=zzz.zzz.zzz.zzz
        ip = dict([line.split('=') for line in out.decode('ascii').strip().split('\n')])

        reply = 'http://%s:%d/?action=stream' % (ip['External'], EXTERNAL_PORT)

        if ip['External'] != ip['Public']:
            reply += '\nmay not be accessible from outside'

        bot.sendMessage(chat_id, reply)

    elif command == '/close':
        # delete port forward
        subprocess.call([pf, 'delete', str(EXTERNAL_PORT)])

        bot.sendMessage(chat_id, 'Port closed')
    else:
        bot.sendMessage(chat_id, "I don't understand")


TOKEN = sys.argv[1]

# Start streaming
subprocess.call([cs, 'start'])

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print 'Listening ...'

while 1:
    time.sleep(10)

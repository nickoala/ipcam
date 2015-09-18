import sys
import time
import subprocess
import telepot

"""
$ python3.2 ipcam.py <token> <user_id>

Use Telegram as a DDNS service, making an IP cam accessible over the internet.

Accept two commands:
/open: open a port through the router to the video stream, and send the URL
/close: close the external port

Only intended to be used by one person, indicated by the <user_id> argument
on the command-line.
"""

EXTERNAL_PORT = 54321
INTERNAL_PORT = 8080  # mjpg_streamer default

def handle(msg):
    type, from_id, chat_id = telepot.glance(msg)

    if type != 'text':
        print('Invalid %s message from %d' % (type, from_id))
        return
    
    if from_id != USER_ID:
        print('Unauthorized user: %d' % from_id)
        return

    command = msg['text'].strip().lower()

    if command == '/open':
        # port forward
        subprocess.call(['pf', str(EXTERNAL_PORT), str(INTERNAL_PORT)])

        # extract IP addresses
        out = subprocess.check_output(['ipaddr'])

        # Output:
        # Internal=zzz.zzz.zzz.zzz
        # External=zzz.zzz.zzz.zzz
        # Public=zzz.zzz.zzz.zzz
        ipaddr = dict([line.split('=') for line in out.decode('ascii').strip().split('\n')])

        reply = 'http://%s:%d/?action=stream' % (ipaddr['External'], EXTERNAL_PORT)

        if ipaddr['External'] != ipaddr['Public']:
            reply += '\nmay not be accessible from outside'

        bot.sendMessage(from_id, reply)

    elif command == '/close':
        # delete port forward
        subprocess.call(['pf', 'delete', str(EXTERNAL_PORT)])

        bot.sendMessage(from_id, 'Port closed')
    else:
        bot.sendMessage(from_id, '%s??? What you talking about?' % command)


TOKEN = sys.argv[1]
USER_ID = int(sys.argv[2])  # only one user is allowed

# Start streaming
subprocess.call(['cs', 'start'])

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print('Listening ...')

while 1:
    time.sleep(10)

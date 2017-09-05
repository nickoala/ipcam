import sys
import time
import subprocess
import telepot
from telepot.loop import MessageLoop

ipaddr = '/usr/local/bin/ipaddr'

EXTERNAL_PORT = 54321

def handle(msg):
    chat_id = msg['chat']['id']

    # extract IP addresses
    out = subprocess.check_output([ipaddr])

    # Output:
    # Internal=zzz.zzz.zzz.zzz
    # External=zzz.zzz.zzz.zzz
    # Public=zzz.zzz.zzz.zzz
    #
    # Parse output into dict
    ip = dict([line.split('=') for line in out.decode('ascii').strip().split('\n')])

    reply = 'http://%s:%d/' % (ip['External'], EXTERNAL_PORT)

    if ip['External'] != ip['Public']:
        reply += '\nmay not be accessible from outside'

    bot.sendMessage(chat_id, reply)


TOKEN = sys.argv[1]

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)

import config
import telepot
import json
from time import ctime, sleep


class Bot():
    def __init__(self):
        self.bot = self.startBot()
        self.users, self.offset = self.getData()
        self.getMessages()

    def startBot(self):
        '''Avvia e restituisce il bot.'''
        print(ctime(), 'Avvio del bot in corso...')
        bot = telepot.Bot(config.token)
        print(ctime(), 'Bot avviato con successo!')
        return bot

    def getData(self):
        '''Carica gli utenti alla quale inviare i messaggi'''
        with open('data.json', encoding='utf-8') as f:
            data = json.load(f)
            users = set(data['users']) if 'users' in data else set()
            offset = data['offset'] if 'offset' in data else None
        return users, offset

    def getMessages(self):
        '''Controlla se ci sono nuovi messaggi dagli utenti'''
        messages = self.bot.getUpdates(offset=self.offset)
        offset = self.offset
        for message in messages:
            offset = message['update_id']+1
            chatId = message['message']['from']['id']
            text = message['message']['text']
            self.reply(text, chatId)
        if offset != self.offset:
            self.offset = offset
            self.updateData()

    def reply(self, text, chatId):
        '''Risponde agli utenti'''
        if text == '/start':
            self.sendMessage(chatId, 'Ti terrò aggiornato sui nuovi post!')
            self.users.add(chatId)
        elif text == '/stop':
            self.sendMessage(chatId, 'Non ti invierò più notifiche.')
            self.users.discard(chatId)
        else:
            self.sendMessage(chatId, '''Mi dispiace, non ho capito.
Usa uno dei due comandi /start o /stop.''')

    def sendMessage(self, chatId, text):
        while True:
            try:
                print(ctime(), 'Invio messaggio in corso.')
                self.bot.sendMessage(chatId, text, parse_mode='HTML',
                                     disable_web_page_preview=True)
            except Exception as e:
                print(ctime(), 'Invio fallito. Riproverò tra 5 secondi.')
                print(e)
                sleep(5)
                continue
            print(ctime(), 'Messaggio inviato con successo.')
            return

    def updateData(self):
        '''Aggiorna gli utenti nel json'''
        with open('data.json', mode='w', encoding='utf-8') as f:
            data = {}
            data['offset'] = self.offset
            data['users'] = list(self.users)
            json.dump(data, f)

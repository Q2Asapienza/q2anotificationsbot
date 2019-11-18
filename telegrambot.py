import config
import telepot
import json
import datetime

DATA_JSON = './data/telegrambot.json'


def ctime():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")


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
        try:
            with open(DATA_JSON, encoding='utf-8') as f:
                data = json.load(f)
                users = set(data['users']) if 'users' in data else set()
                offset = data['offset'] if 'offset' in data else None
        except FileNotFoundError:
            with open(DATA_JSON, mode='w', encoding='utf-8') as f:
                data = {}
                json.dump(data, f)
                users = []
                offset = None
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
        try:
            print(ctime(), 'Invio messaggio in corso.')
            self.bot.sendMessage(chatId, text, parse_mode='HTML',
                                 disable_web_page_preview=False)
        except telepot.exception.BotWasBlockedError:
            print(ctime(), "L'utente ha bloccato il bot, lo rimuovo dalla lista degli utenti. Il suo ID era:", chatId)
            self.users.discard(chatId)
            self.updateData()
            return
        except Exception as e:
            print(ctime(), 'Invio fallito. ChatID:', chatId)
            print(e.__class__.__name__)
            print(e)
            return
        print(ctime(), 'Messaggio inviato con successo.')
        return

    def updateData(self):
        '''Aggiorna gli utenti nel json'''
        with open(DATA_JSON, mode='w', encoding='utf-8') as f:
            data = {}
            data['offset'] = self.offset
            data['users'] = list(self.users)
            json.dump(data, f)

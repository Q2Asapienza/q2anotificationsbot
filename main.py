#!/usr/bin/python3
import telegrambot #TODO: telegrambot cannot be imported due to config missing
import crawler

def formatMessage(data):
    text = ''
    return text

def main():
    #initializing telegram bot
    bot = telegrambot.Bot()

    notifications = crawler.getNotifications()

    for notification in notifications:
        text = formatMessage(notification)
        for chatId in bot.users:
            bot.sendMessage(chatId, text)


if __name__ == '__main__':
    main()

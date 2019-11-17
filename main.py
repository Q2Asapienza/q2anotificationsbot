#!/usr/bin/python3
import telegrambot
import crawler
from Q2A_Pi import Keys
import time
from datetime import datetime


def formatMessage(notification):
    text = '''New Activity in {}
{} {} by {}'''
    data = notification[crawler.DATA]
    nType = data[Keys.TYPE]  # Notification Type
    # Case Question
    if nType == Keys.TYPE_QUESTIONS:
        question = data
        who = data[Keys.LAST_EDIT][Keys.WHO]
        who = f'<a href="{buildUserLink(who)}">{who}</a>'
    # Case Answer
    elif nType == Keys.TYPE_ANSWERS:
        question = data[Keys.PARENT]
        who = data[Keys.LAST_EDIT][Keys.WHO]
        who = f'<a href="{buildUserLink(who)}">{who}</a>'
    # Altrimenti è un commento
    else:
        answer = data[Keys.PARENT]
        question = answer[Keys.PARENT]
        who = data[Keys.LAST_EDIT][Keys.WHO]
        parentWho = answer[Keys.LAST_EDIT][Keys.WHO]
        if parentWho != who:
            who = f'<a href="{buildUserLink(who)}">{who}</a> on <a href="{buildUserLink(parentWho)}">{parentWho}</a>\'s answer'
        else:
            who = f'<a href="{buildUserLink(who)}">{who}</a> on its answer'
    title = question[Keys.TITLE]
    questionID = question[Keys.ID]
    title = f'<a href="{buildTitleLink(questionID)}">{title}</a>'
    otherID = data[Keys.ID]
    what = data[Keys.LAST_EDIT][Keys.WHAT]
    if what == 'edited':
        if nType == Keys.TYPE_COMMENTS:
            what = 'comment edited'
            who = data[Keys.LAST_EDIT][Keys.WHO]
            who = f'<a href="{buildUserLink(who)}">{who}</a>'
        elif nType == Keys.TYPE_ANSWERS:
            what = 'answer edited'
        else:
            what = 'question edited'
    elif what == 'selected':
        what = 'answer selected'
    what = f'<a href="{buildWhatLink(nType, questionID, otherID)}">{what}</a>'
    when = getWhen(data[Keys.LAST_EDIT][Keys.WHEN])
    text = text.format(title, what, when, who)

    return text


def buildWhatLink(nType, questionID, otherID):
    types = {Keys.TYPE_QUESTIONS: 'q',
             Keys.TYPE_ANSWERS: 'a',
             Keys.TYPE_COMMENTS: 'c'}
    link = f'https://q2a.di.uniroma1.it/{questionID}/#{types[nType]}{otherID}'
    return link


def buildTitleLink(questionID):
    return f'https://q2a.di.uniroma1.it/{questionID}/'


def buildUserLink(username):
    return f'https://q2a.di.uniroma1.it/user/{username}'


def getWhen(timestamp):
    '''Trasforma il timestamp nel when di q2a'''
    FMT = '%H:%M:%S'
    gmtime = time.strftime(FMT, time.gmtime())
    timestamp = timestamp[11:19]
    tdelta = datetime.strptime(gmtime, FMT) - datetime.strptime(timestamp, FMT)
    hh, mm, ss = map(int, str(tdelta).split(':'))
    if hh:
        s = 's' if hh > 1 else ''
        return f'{hh} hour{s} ago'
    if mm:
        s = 's' if mm > 1 else ''
        return f'{mm} minute{s} ago'
    s = 's' if ss > 1 else ''
    return f'{ss} second{s} ago'


def main():
    crawler.excluded_keys = ['recategorized', 'closed']

    # initializing telegram bot
    bot = telegrambot.Bot()

    notifications = crawler.getNotifications()

    for notification in notifications:
        text = formatMessage(notification)
        for chatId in bot.users:
            bot.sendMessage(chatId, text)


if __name__ == '__main__':
    main()

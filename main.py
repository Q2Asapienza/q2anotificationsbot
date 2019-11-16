#!/usr/bin/python3
#import telegrambot #TODO: telegrambot cannot be imported due to config missing
from crawler import *

def formatMessage(notification):
    text = ''
    data = notification[DATA]
    
    creator = data[Keys.CREATED][Keys.USER]
    editor = data[Keys.LAST_EDIT][Keys.USER]
    creator = 'its' if creator == editor else f"{creator}'s'"

    #checking data type to discover if it's a question/answer/comment
    #CASE QUESTION
    if(data[Keys.TYPE] == Keys.TYPE_QUESTIONS):
        if(notification[Keys.TYPE] == NOTIFTYPE_ADD):
            text = f'{editor} added a question: {data[Keys.TITLE]}'
        elif(notification[Keys.TYPE] == NOTIFTYPE_EDIT):
            text = f'{editor} edited {creator} question ({data[Keys.TITLE]})'

    #CASE ANSWER
    elif(data[Keys.TYPE] == Keys.TYPE_ANSWERS):
        answer = data
        question = data[Keys.PARENT]

        if(notification[Keys.TYPE] == NOTIFTYPE_ADD):
            text = f'{editor} added a answer to the question: {question[Keys.TITLE]} (from {answer[Keys.CREATED][Keys.USER]})'
        elif(notification[Keys.TYPE] == NOTIFTYPE_EDIT):
            text = f'{editor} edited {creator} answer to the question: {question[Keys.TITLE]} (from {answer[Keys.CREATED][Keys.USER]})'

    #CASE COMMENT
    elif(data[Keys.TYPE] == Keys.TYPE_COMMENTS):
        comment  = data
        answer   = comment[Keys.PARENT]
        question = answer[Keys.PARENT]
        if(notification[Keys.TYPE] == NOTIFTYPE_ADD):
            text = f'{editor} added a comment to {answer[Keys.CREATED][Keys.USER]}\'s answer to the question: {question[Keys.TITLE]}'
        elif(notification[Keys.TYPE] == NOTIFTYPE_EDIT):
            text = f'{editor} edited {creator} comment to {answer[Keys.CREATED][Keys.USER]}\'s answer to the question: {question[Keys.TITLE]}'
    
    return text

def main():
    #initializing telegram bot
    #bot = telegrambot.Bot()

    notifications = getNotifications()

    for notification in notifications:
        text = formatMessage(notification)
        print(text)
        #for chatId in bot.users:
        #    bot.sendMessage(chatId, text)


if __name__ == '__main__':
    main()

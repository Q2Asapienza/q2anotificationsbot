import telegrambot
import Q2A_Pi


def formatMessage(data):
    text = ''
    return text


def main():
    bot = telegrambot.Bot()
    q2a = Q2A_Pi.qualcosa #TODO: get questions
    newActivities = q2a.newActivities

    for activity in newActivities:
        text = formatMessage(activity)
        for chatId in bot.users:
            bot.sendMessage(chatId, text)


if __name__ == '__main__':
    # main()
    pass

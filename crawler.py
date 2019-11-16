#!/usr/bin/python3
from Q2A_Pi import Q2A, Keys, Q2ADictToSerializable # pylint: disable=unused-import

import json

CRAWLED_JSON_PATH = './crawled.json'

#types
NOTIFTYPE_ADD = 'add'
NOTIFTYPE_EDIT = 'edit'

#data
DATA = 'data'

def __getSiteAsJSON(fromActivity = True):
    #initializing Q2A crawler
    q2a = Q2A()

    #getting ALL the questions
    if(fromActivity):
        questions = q2a.getQuestionsFromActivities()
    else:
        questions = q2a.getQuestions()
    #getting answers from questions
    answers = q2a.getAnswersFromQuestions(questions)
    #getting the comments from questions
    q2a.getCommentsFromAnswers(answers)

    
    return questions

def getNotifications(fromActivity = True):
    notifications = []

    #CRAWLING THE WHOLE WEBSITE
    site = __getSiteAsJSON(fromActivity)

    #READING THE OLD WEBSITE
    #if there is an error reading the file it will just proceed to serialize the new file
    # (therefore assuming it's his first launchand there are no notifications to send)
    oldSite = None
    try:
        with open(CRAWLED_JSON_PATH,'r') as crawled_file:
            oldSite = json.load(crawled_file)
        print(f"crawler.py: {CRAWLED_JSON_PATH} read correctly")
    except Exception:
        pass

    if oldSite == None:
        print(f"crawler.py: {CRAWLED_JSON_PATH} not found, assuming it's first run")
    else:
        notifications = __diffCheck(site,oldSite)

    #dumping serializable dict to file
    json.dump(Q2ADictToSerializable(site), open(CRAWLED_JSON_PATH,'w'))
    print(f"crawler.py: {CRAWLED_JSON_PATH} wrote correctly")
    return notifications

def __diffCheck(site,oldSite):
    #CHECKING DIFFERENCES TO CREATE NOTIFICATIONS
    differences = []
    for questionID in site:
        #checking difference of question
        diff = __elementNewOrEdited(questionID,site,oldSite)

        #if the question has not just been added then it means it has been edited or there were no changes
        #so i need to check the answers or the comments to find
        if(diff[Keys.TYPE] != NOTIFTYPE_ADD):
            #region checking difference of answers
            answers = site[questionID][Keys.TYPE_ANSWERS]
            try:
                oldAnswers = oldSite[questionID][Keys.TYPE_ANSWERS]
            except Exception:
                oldAnswers = {}
            
            for answerID in answers:
                diff = __elementNewOrEdited(answerID,answers,oldAnswers)

                if(diff[Keys.TYPE] != NOTIFTYPE_ADD):
                    #region checking difference of comments
                    comments = answers[answerID][Keys.TYPE_COMMENTS]
                    try:
                        oldComments = oldAnswers[answerID][Keys.TYPE_COMMENTS]
                    except Exception:
                        oldAnswers = {}
                    for commentID in comments:
                        diff = __elementNewOrEdited(commentID,comments,oldComments)
                    #endregion
            
            #endregion
        if(diff[Keys.TYPE] != None):
            differences.append(diff)
    
    return differences

def __elementNewOrEdited(elementID,elements,oldElements):
    diff = {
            Keys.TYPE:None
    }
    #if question doesn't exists
    if(elementID not in oldElements):
        diff[Keys.TYPE] = NOTIFTYPE_ADD
        diff[DATA]      = elements[elementID]
    #if the question has been modified
    elif(elements[elementID][Keys.LAST_EDIT] != oldElements[elementID][Keys.LAST_EDIT]):
        diff[Keys.TYPE] = NOTIFTYPE_EDIT
        diff[DATA]      = elements[elementID]
    
    return diff

if __name__ == '__main__':
    print(getNotifications())
    pass

from Q2A_Pi import Q2A, Keys, Q2ADictToSerializable

import json

CRAWLED_JSON_PATH = './crawled.json'

#types
NOTIFTYPE_ADD = 'add'
NOTIFTYPE_EDIT = 'edit'
NOTIFTYPE_BEST = 'best'

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
    try:
        #READING THE OLD WEBSITE
        with open(CRAWLED_JSON_PATH,'r') as crawled_file:
            oldSite = json.load(crawled_file)
        print(f"crawler.py: {CRAWLED_JSON_PATH} read correctly")
        site = __getSiteAsJSON(fromActivity)

        #finding differences
        notifications = __diffCheck(site,oldSite)

        #updating old dict with new datas
        oldSite.update(Q2ADictToSerializable(site))
        #dumping serializable dict to file
        json.dump(oldSite, open(CRAWLED_JSON_PATH,'w'))
    except IOError:
        #OLD WEBSITE NOT FOUND, IT'S FIRST RUN, DUMPING WHOLE WEBSITE
        print(f"crawler.py: {CRAWLED_JSON_PATH} not found, assuming it's first run")

        site = __getSiteAsJSON(False)
        json.dump(Q2ADictToSerializable(site), open(CRAWLED_JSON_PATH,'w'))

    print(f"NOTIFICATIONS:\n{notifications}")

    return notifications



def __diffCheck(questions,oldQuestions):
    #CHECKING DIFFERENCES TO CREATE NOTIFICATIONS
    differences = []
    for questionID in questions:
        #checking difference of question
        diff = __elementNewOrEdited(questionID,questions,oldQuestions)

        if(diff[Keys.TYPE] != None):
            differences.append(diff)

        #TODO: CHECK BEST ANSWER

        #if this element has been just added i don't check differences for childs
        if(diff[Keys.TYPE] == NOTIFTYPE_ADD):
            continue
        
        #region checking difference of answers
        answers = questions[questionID][Keys.TYPE_ANSWERS]
        try:
            oldAnswers = oldQuestions[questionID][Keys.TYPE_ANSWERS]
        except Exception:
            oldAnswers = {}
        
        for answerID in answers:
            #checking difference of question
            ansDiff = __elementNewOrEdited(answerID,answers,oldAnswers)

            if(ansDiff[Keys.TYPE] != None):
                differences.append(ansDiff)

            #if this element has been just added i don't check differences for childs
            if(ansDiff[Keys.TYPE] == NOTIFTYPE_ADD):
                continue

            #region checking difference of comments
            comments = answers[answerID][Keys.TYPE_COMMENTS]
            try:
                oldComments = oldAnswers[answerID][Keys.TYPE_COMMENTS]
            except Exception:
                oldAnswers = {}
            for commentID in comments:
                commDiff = __elementNewOrEdited(commentID,comments,oldComments)

                if(commDiff[Keys.TYPE] != None):
                    differences.append(commDiff)
            #endregion
            
        #endregion
    
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
    #print(getNotifications())
    pass

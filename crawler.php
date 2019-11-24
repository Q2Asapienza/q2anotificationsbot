<?php
require './Q2A-php-interface/Q2A.php';

const CRAWLED_JSON_PATH = './data/crawled.json';

function ctime(){
    return date("d-m-Y H:i:s");
}

function __getSiteAsJSON($fromActivity=True){
    # initializing Q2A crawler
    $q2a = new Q2A();

    # getting ALL the questions
    $questions = null;
    if($fromActivity){
        $questions = $q2a->getQuestionsFromActivities();
    }else{
        $questions = $q2a->getQuestions();
    }
    # getting answers from questions
    $answers = $q2a->getAnswersFromQuestions($questions);
    # getting the comments from questions
    $q2a->getCommentsFromAnswers($answers);

    return $questions;
}

function getNotifications($fromActivity=True){
    $notifications = [];
    # READING THE OLD WEBSITE
    if(($oldSite = @file_get_contents(CRAWLED_JSON_PATH)) !== FALSE){
        $oldSite = json_decode($oldSite, true);
        echo ctime()." crawler.py: ".CRAWLED_JSON_PATH." read correctly";
        
        $site = __getSiteAsJSON($fromActivity);

        # finding differences
        $notifications = __diffCheck($site, $oldSite);

        # updating old dict with new datas
        $oldSite = Q2ADictToSerializable($site) + $oldSite;
        # dumping serializable dict to file
        file_put_contents(CRAWLED_JSON_PATH, json_encode($oldSite));
    }else{
        # OLD WEBSITE NOT FOUND, IT'S FIRST RUN, DUMPING WHOLE WEBSITE
        echo ctime()." crawler.py: ".CRAWLED_JSON_PATH." not found, assuming it's first run";

        $site = __getSiteAsJSON(False);
        $site = Q2ADictToSerializable($site);
        $site = json_encode($site);
        file_put_contents(CRAWLED_JSON_PATH, $site);
    }

    echo "NOTIFICATIONS:\n".count($notifications);
    return $notifications;
}

function __diffCheck($questions, $oldQuestions){
    # CHECKING DIFFERENCES TO CREATE NOTIFICATIONS
    $differences = [];
    foreach ($questions as $questionID => $question){
        # checking difference of question
        $diff = __elementNewOrEdited($questionID, $questions, $oldQuestions);

        if($diff != null){
            $differences[] = $diff;
        }
        
        # region checking difference of answers
        $answers = $questions[$questionID]->{Keys::TYPE_ANSWERS};
        $oldAnswers = [];
        if(isset($oldQuestions[$questionID][Keys::TYPE_ANSWERS])){
            $oldAnswers = $oldQuestions[$questionID][Keys::TYPE_ANSWERS];
        }
        
        foreach ($answers as $answerID => $answer){
            # checking difference of question
            $ansDiff = __elementNewOrEdited($answerID, $answers, $oldAnswers);

            if($ansDiff != null){
                $differences[] = $ansDiff;
            }

            # region checking difference of comments
            $comments = $answers[$answerID]->{Keys::TYPE_COMMENTS};
            $oldComments = [];
            if(isset($oldAnswers[$answerID][Keys::TYPE_COMMENTS])){
                $oldComments = $oldAnswers[$answerID][Keys::TYPE_COMMENTS];
            }
            foreach ($comments as $commentID => $comment){
                $commDiff = __elementNewOrEdited($commentID, $comments, $oldComments);

                if($commDiff[Keys::TYPE] != null){
                    $differences[] = $commDiff;
                }
            }
            # endregion
        }
        # endregion
    }
    return $differences;
}

function __elementNewOrEdited($elementID, $elements, $oldElements){
    global $excluded_keys;
    $diff = null;
    # if question doesn't exists
    if(!array_key_exists($elementID, $oldElements)){
        $diff = $elements[$elementID];
    # if the question has been modified
    }else if($elements[$elementID]->{Keys::LAST_EDIT} != $oldElements[$elementID][Keys::LAST_EDIT] && !array_key_exists($elements[$elementID]->{Keys::LAST_EDIT}[Keys::WHAT], $excluded_keys)){
        $diff = $elements[$elementID];
    }
    return $diff;
}

$excluded_keys = [];
if (basename(__FILE__) == basename($_SERVER["SCRIPT_FILENAME"])) {
    if(!isset($excluded_keys) && $argc == 2){
        $excluded_keys = json_decode($argv[1], true);
    }
    $notifications = getNotifications();
    var_dump($notifications);
}
?>
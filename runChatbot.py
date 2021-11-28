#from chatbot import app
from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import trainingData
import random
from spellchecker import SpellChecker

app = Flask(__name__)

hal = ChatBot("HAL")

#trains the AI chatbot in english using the corpus_trainer
corpus_trainer = ChatterBotCorpusTrainer(hal);
corpus_trainer.train("chatterbot.corpus.english.ai")
corpus_trainer.train("chatterbot.corpus.english.conversations")
corpus_trainer.train("chatterbot.corpus.english.computers")
corpus_trainer.train("chatterbot.corpus.english.emotion")
corpus_trainer.train("chatterbot.corpus.english.greetings")
corpus_trainer.train("chatterbot.corpus.english.movies")

#trains HAL using the training data defined in trainingData.py
conversationTrainer = ListTrainer(hal)
conversationTrainer.train(trainingData.casualConversation)
conversationTrainer.train(trainingData.basicAdvice)
conversationTrainer.train(trainingData.advisor)
conversationTrainer.train(trainingData.gpaToTransfer)

correctTypos = SpellChecker()

tag_list = ['cs 149', 'ise 164', 'cs 146', 'cmpe 131', 'cmpe 120', 'cmpe 102', 'cmpe 133', 'cmpe 148', 'cmpe 165', 'cmpe 172', 'cmpe 187', 'cmpe 195a', 'cmpe 195b', 'engr 195a', 'engr 195b', 'engr 195', 'cmpe 195', 'cmpe195', 'engr195', 'cs 151', 'cs 157a', 'cs 166', 'cs149', 'ise164', 'cs146', 'cmpe131', 'cmpe120', 'cmpe102', 'cmpe133', 'cmpe148', 'cmpe165', 'cmpe172', 'cmpe187', 'cmpe195a', 'cmpe195b', 'engr195a', 'engr195b', 'engr195', 'cmpe195', 'cs151', 'cs157a', 'cs166', 'how many units should i take', 'cmpe 137', 'cmpe137', 'cmpe 139', 'cmpe139', 'cmpe 152', 'cmpe152', 'cmpe 185', 'cmpe185', 'cmpe 181', 'cmpe181', 'cmpe 182', 'cmpe182', 'cmpe 183', 'cmpe183', 'cmpe 185', 'cmpe185', 'cmpe 188', 'cmpe188', 'cmpe 189', 'cmpe189', 'cs 116a', 'cs116a', 'cs 134', 'cs134', 'cs 152', 'cs152']
prereq = ['prerequisite', 'prereq', 'prerequisites', 'prereqs', 'take before', 'what class do i need to']

@app.route('/')
def index():
    return render_template('base.html')

@app.route("/get")
def getResponse():
    userMessage = request.args.get('msg')
    userMessage = userMessage.lower()
    userMessage = correctTypos.correction(userMessage)
    tag = [s for s in tag_list if(s in userMessage)]
    hasPrereq = [s for s in prereq if(s in userMessage)]
    if(bool(tag) and bool(hasPrereq)):
        selected_intent = next((i for i in trainingData.overallPrereq if i['tag'] == tag[0]), None)
        possibleResponses = selected_intent['responses']
        response = possibleResponses[0]
        return str(response)
    elif(bool(hasPrereq) and not(bool(tag))):
        return "sorry i don't know the prerequiste for that. you can check using the course catalog here: https://catalog.sjsu.edu/content.php?catoid=12&navoid=4145"
    elif(not(bool(hasPrereq)) and bool(tag)):
        selected_intent = next((i for i in trainingData.overallPrereq if i['tag'] == tag[0]), None)
        possibleResponses = selected_intent['responses']
        response = possibleResponses[1]
        return str(response)
    else:
        return str(hal.get_response(userMessage)) + " If you don't like my answer, you can reword the question and ask it again or as me who your advisor is to get more indepth answers. I'm ready for more advising related questions."

if __name__ == '__main__':
    app.run(debug=True)

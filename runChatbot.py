#from chatbot import app
from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import trainingData
import random

app = Flask(__name__)

hal = ChatBot("HAL")

#trains the AI chatbot in english using the corpus_trainer
corpus_trainer = ChatterBotCorpusTrainer(hal);
corpus_trainer.train("chatterbot.corpus.english")

#trains HAL using the training data defined in trainingData.py
conversationTrainer = ListTrainer(hal)
conversationTrainer.train(trainingData.casualConversation)
conversationTrainer.train(trainingData.basicAdvice)
conversationTrainer.train(trainingData.advisor)
conversationTrainer.train(trainingData.gpaToTransfer)

tag_list = ['cs 149', 'cs 146', 'cmpe 131', 'cmpe 120', 'cmpe 102', 'cmpe 133', 'cmpe 148', 'cmpe 165', 'cmpe 172', 'cmpe 187', 'cmpe 195a', 'cmpe 195b', 'engr 195a', 'engr 195b', 'engr 195', 'cmpe 195', 'cs 151', 'cs 157a', 'cs 166']

@app.route('/')
def index():
    return render_template('base.html')

@app.route("/get")
def getResponse():
    userMessage = request.args.get('msg')
    tag = [s for s in tag_list if(s in userMessage)]
    if(bool(tag)):
        selected_intent = next((i for i in trainingData.overallPrereq if i['tag'] == tag[0]), None)
        possibleResponses = selected_intent['responses']
        response = possibleResponses[random.randint(0, len(possibleResponses)-1)]
        return str(response)
    else:
        return str(hal.get_response(userMessage))

if __name__ == '__main__':
    app.run(debug=True)

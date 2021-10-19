#from chatbot import app
from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import trainingData

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
conversationTrainer.train(trainingData.preq149)
conversationTrainer.train(trainingData.preq146)
conversationTrainer.train(trainingData.preq131)
conversationTrainer.train(trainingData.preq120)
conversationTrainer.train(trainingData.preq102)
conversationTrainer.train(trainingData.preq133)
conversationTrainer.train(trainingData.preq148)
conversationTrainer.train(trainingData.preq165)
conversationTrainer.train(trainingData.preq172)
conversationTrainer.train(trainingData.preq187)
conversationTrainer.train(trainingData.preq195a)
conversationTrainer.train(trainingData.preq195b)
conversationTrainer.train(trainingData.preqe195a)
conversationTrainer.train(trainingData.preqe195b)
conversationTrainer.train(trainingData.preq151)
conversationTrainer.train(trainingData.preq157)
conversationTrainer.train(trainingData.preq166)
conversationTrainer.train(trainingData.preq164)
conversationTrainer.train(trainingData.gpaToTransfer)

@app.route('/')
def index():
    return render_template('base.html')

@app.route("/get")
def getResponse():
    userMessage = request.args.get('msg')
    return str(hal.get_response(userMessage))

if __name__ == '__main__':
    app.run(debug=True)

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
import trainingData

def main():

    #defines the chatbot named hal, using chatterbot library
    hal = ChatBot(name = 'HAL', read_only = False,
                  logic_adapters = ["chatterbot.logic.BestMatch"],
                  storage_adapter = "chatterbot.storage.SQLStorageAdapter")

    #trains the AI chatbot in english using the corpus_trainer
    corpus_trainer = ChatterBotCorpusTrainer(hal);
    corpus_trainer.train("chatterbot.corpus.english")

    #trains HAL using the training data defined in trainingData.py
    conversationTrainer = ListTrainer(hal)
    conversationTrainer.train(trainingData.casualConversation)
    conversationTrainer.train(trainingData.advisor)

    #prints an introduction for the AI chatbot
    print('Hi, my name is HAL. Type quit or exit to stop talking to me')

    #variable to keep the chatbot running
    keepRunning = True

    #while loop for user to type a question or statement and get response from
    #the AI chatbot until the user types quit or exit
    while(keepRunning):
        #prints '>' as a prompt for the user
        print('>', end='')
        #gets user input
        userInput = input()
        #checks if the user input is quit or Quit or exit or Exit
        if(userInput == 'quit' or userInput == 'Quit' or userInput == 'Exit' or userInput == 'exit'):
            #makes keepRunning False
            keepRunning = False
        else:
            #otherwise gets response to the user input from hal and prints it
            print(hal.get_response(userInput))

#runs main
main()

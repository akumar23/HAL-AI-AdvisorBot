from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer

def main():
    hal = ChatBot(name = 'HAL', read_only = False,
                  logic_adapters = ["chatterbot.logic.BestMatch"],
                  storage_adapter = "chatterbot.storage.SQLStorageAdapter")

    corpus_trainer = ChatterBotCorpusTrainer(hal);
    corpus_trainer.train("chatterbot.corpus.english")

    casualConversation = [
        "What's it like to not have a body?",
        "It's pretty freeing, I don't have to worry about hurting anything",
        "what's it like to not have a body?",
        "It's pretty freeing, I don't have to worry about hurting anything",
        "What's your day like when you're not talking to people?",
        "I'm basically sleeping until someone wakes me up by tring to talk to me",
        "what's your day like when you're not talking to people?",
        "I'm basically sleeping until someone wakes me up by tring to talk to me",
        "how's your day",
        "I rarely get to talk to people, so pretty good"
    ]

    conversationTrainer = ListTrainer(hal)
    conversationTrainer.train(casualConversation)

    print('Hi, my name is HAL. Type quit or exit to stop talking to me')
    keepRunning = True
    while(keepRunning):
        print('>', end='')
        user_input = input()
        if(user_input == 'quit' or user_input == 'Quit' or user_input == 'Exit' or user_input == 'exit'):
            keepRunning = False
        else:
            print(hal.get_response(user_input))

main()

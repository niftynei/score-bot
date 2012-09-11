import pyrc

class Dumboooot(pyrc.Bot):
	users = []

if __name__ == '__main__':
	bot = Dumboooot('irc.freenode.net', channels = ['#test-scorebot'])
	bot.connect()

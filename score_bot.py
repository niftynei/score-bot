import pyrc
import pyrc.utils.hooks as hooks
import re
import pprint

###
#				x) Get list of all users on the channel
#				x) Add user when user joins room
#				x) Remove user from list when user leaves
#				x) Update username when switches
#				x) Get the person's name that posts
#				x) Regex all chat on channel for the +1 keyword
# TODO: 1) Database or data file for keeping score
#				7) Create a user object that has username & current screenname
###

nickname = 'blind_harry'

class ScoreBotter(pyrc.Bot):
	users = []
	scores = {}
	plus_one_pattern = re.compile('(?P<before>\S+)?(?:\s+)?\+\d(?:\s+)?(?P<after>\S+)?')

	@hooks.command()
	def scoreboard(self, channel):
		scrs = ''
		for score in self.scores:
			if self.scores[score] != 0:
				scrs += "%s-%s " %(score, self.scores[score])
		if scrs == '':
			scrs = 'None'
		self.message(channel, "Scores: %s" %(scrs))

	def receivemessage(self, channel, nick, message):
		super(ScoreBotter, self).receivemessage(channel, nick, message)
		self._plus_one(nick, message)


	def add_listeners(self):
		super(ScoreBotter, self).add_listeners()
		self.add_listener(r'^:(\S+) 353 \S+ @ (\S+) :\S+ (.+)$', self._users)
		self.add_listener(r'^:(\S+)!~\S+ NICK\s+:(\S+)', self._change_name)
		self.add_listener(r'^:(\S+)!~\S+ JOIN (\S+)', self._add_user) 
		self.add_listener(r'^:(\S+)!~\S+ PART (\S+)', self._remove_user) 

	def _plus_one(self, nick, message):
		m = self.plus_one_pattern.search(message)
		if m is not None:
			for match in m.groups():
				if match is not None:
					match = re.sub(':', '', match)	
					if match == nick:
						self.scores[match] -= 2
					elif match in self.scores:
						self.scores[match] += 1
					elif match == nickname:
						self.scores[nick] = 10

	def _users(self, server, channel, users):
		if len(self.users) < 1:
			self.users = re.split(' ', re.sub('@', '', users))
			self.scores = dict(zip(self.users, [0 for user in self.users]))

	def _change_name(self, last_nick, new_nick):
		if last_nick in self.scores:
			self.scores[new_nick] = self.scores[last_nick]
			del self.scores[last_nick]
	
	def _add_user(self, nick, channel):
		if nick not in self.scores:
			self.scores[nick] = 0
	
	def _remove_user(self, nick, channel):
		if nick in self.scores:
			del self.scores[nick]

if __name__ == '__main__':
	bot = ScoreBotter('irc.freenode.net', channels = ['#test-scorebot'], nick = nickname)
	bot.connect()

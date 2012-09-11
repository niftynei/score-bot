import pyrc
import pyrc.utils.hooks as hooks
import re

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
class ScoreBotter(pyrc.Bot):
	users = []
	scores = {}
	plus_one_pattern = re.compile('(?P<before>\S+)? ?\+1 ?(?P<after>\S+)?')

	@hooks.command()
	def scoreboard(self, channel):
		self.message(channel, "Scores: %s" %(str(self.scores)))

	def receivemessage(self, channel, nick, message):
		super(ScoreBotter, self).receivemessage(channel, nick, message)

		m = self.plus_one_pattern.search(message)
		if m is not None:
			for match in m.groups():
				if match is not None:
					match = re.sub(':', '', match)	
					if match in self.scores:
						self.scores[match] += 1
					#	self.scores[nick] += 1

	def add_listeners(self):
		super(ScoreBotter, self).add_listeners()
		self.add_listener(r'^:(\S+) 353 \S+ @ (\S+) :\S+ (.+)$', self._users)
		self.add_listener(r'^:(\S+)!~\S+ NICK :(\S+)$', self._change_name)
		self.add_listener(r'^:(\S+)!~\S+ JOIN (\S+)', self._add_user) 
		self.add_listener(r'^:(\S+)!~\S+ PART (\S+)', self._remove_user) 

	def _users(self, server, channel, users):
		self.users = re.split(' ', re.sub('@', '', users))
		self.scores = dict(zip(self.users, [0 for user in self.users]))

	def _change_name(self, last_nick, new_nick):
		if self.scores[last_nick]:
			self.scores[new_nick] = self.scores[last_nick]
			del self.scores[last_nick]
	
	def _add_user(self, nick, channel):
		if nick not in self.scores:
			self.scores[nick] = 0
	
	def _remove_user(self, nick, channel):
		if nick in self.scores:
			del self.scores[nick]

if __name__ == '__main__':
	bot = ScoreBotter('irc.freenode.net', channels = ['#test-scorebot'])
	bot.connect()

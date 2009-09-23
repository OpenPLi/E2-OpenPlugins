from urlparse import urlparse

def descramble(text):
	mask = [ 89, 52, 178, 9, 56, 86, 114, 5, 29, 98, 156, 209, 243, 73, 198, 101 ]
	masknr = 0
	descrambled = ''
	if text[0] == '*':
		for i in range(len(text) / 2):
			i = i * 2 + 1
			char = (ord(text[i]) - 65) * 16 + ord(text[i + 1]) - 65
			char = char ^ mask[masknr]
			masknr = masknr + 1
			masknr = masknr & 15
			char = 128 * (char&64)/64 + 64 * (char&2)/2 + 32 * (char&1) + 16 * (char&4)/4 + 8 * (char&32)/32 + 4 * (char&128)/128 + 2 * (char&8)/8 + (char&16)/16
			descrambled += chr(char)
	else:
		descrambled = text
	return descrambled

def geturl(url):
	return urlparse(descramble(url))
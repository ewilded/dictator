# Password wordlist generator by ewilded
# Version 2020
# The goal is to make this:
# - smart -> effective
# - easy to use
# - flexible

# TODO
# - Introduce even distribution of the words when merging multiple input wordlists, the idea is that we assume wordlists
# are ordered based on the keyword's popularity, meaning the most popular passwords go first. Thus, when we have, let's say, two 100-word lists, the we don't want the first word from the second list to become the 101-st word in the merged list, but
# rather the first/second one - and so on. Also, while doing this, we could also get rid of any potential duplicates.
# - dedup words from multiple wordlists (https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists#7961390)
# - generate separate outputs for each username (so far usernames are included into the words automatically and one output file is created, so manager1234 would be attempted against alice, as well as alice1234 against manager, which might not be a huge problem, but is not exactly what we want)

import datetime
from time import gmtime, strftime
import sys
import os

default_wordlist = os.path.dirname(os.path.realpath(__file__))+'/wordlists/w3af_pass.txt'
months_seasons_wordlist = os.path.dirname(os.path.realpath(__file__))+'/wordlists/en/months_seasons.txt'
usernames=[]

# FUNCTION DEFINITIONS
def get_arg(name):
	for argindex in range(0,len(sys.argv)):
		if(sys.argv[argindex]=="-"+name):
			try:
				return sys.argv[argindex+1]
			except NameError:
				return ''
	return ''
	
def if_arg(name):
	for argindex in range(0,len(sys.argv)):
		if(sys.argv[argindex]=="-"+name):
			return True
	return False
	
def usage():
	print("Usage:\n")
	print(sys.argv[0]+" parameters\n")
	print("Whereas parameters can be as follows:\n")
	print("-depth 1-5\t\t\t\t\t\t\tdetermines the depth of the output wordlists (default = 1)")
	print("-usernames alice,bob\t\t\t\t\t\tcomma-separated list of usernames (default = '', not recommended)")
	print("-custom customwordlist.txt,customwordlist2.txt\t\t\tcomma-separated list of input files with custom wordlists to use (by default only built-in wordlist will be used (it is recommended to provide custom wordlists).")
	print("-only-custom\t\t\t\t\t\t\twhether not to include the default built-in wordlists ("+default_wordlist+" + "+months_seasons_wordlist+") if -custom wordlists are specified (by default both custom and built in will be used, use this parameter to override this behaviour).")
	print("-stdout\t\t\t\t\t\t\tprint passwords to stdout instead of a file.")
	print("-h/-usage\t\t\t\t\t\t\tprints this message.")
	# TBD: for future versions - language.
	# Other arguments are currently not parsed, but automatically derived from the value of the depth argument.
	return
	
def load_wordlist(wpath,wlist):
	# merge the wlist with the words from the file pointed with wpath, evenly distributing the words and skipping duplicates
	new_output_list = []
	with open(wpath,'r') as f:
		buff=list(f)
		wlist_count = len(wlist)
		buff_count = len(buff)
		max_count = wlist_count
		if buff_count > max_count:
			max_count=buff_count
		for i in range(0,max_count):
			if i < wlist_count and i < buff_count:
				wlist_item=wlist[i].rstrip().lower()
				element_already_present=False	# since for some mysterious reason fucking "not in list:" 
				for new_item in new_output_list: # did not want to work, I replaced all its instances with this monstrosity
					if new_item==wlist_item:
						element_already_present=True
						break
				if element_already_present==False:
					new_output_list.append(wlist_item)

				buff_item=buff[i].rstrip().lower()
				element_already_present=False
				for new_item in new_output_list:
					if new_item==buff_item:
						element_already_present=True
						break
				if element_already_present==False:
					new_output_list.append(buff_item)
			else:
			# at this point i is either bigger than buff_count or wlist_count
				if i < wlist_count:
					# buff_count is reached here, no more processing of buff
					wlist_item=wlist[i].rstrip().lower()
					element_already_present=False
					for new_item in new_output_list:
						if new_item==wlist_item:
							element_already_present=True
							break
					if element_already_present==False:
						new_output_list.append(wlist_item)
				else:
					# wlist_count is reached here, no more processinf of wlist
					buff_item=buff[i].rstrip().lower()
					element_already_present=False
					for new_item in new_output_list:
						if new_item==buff_item:
							element_already_present=True
							break
					if element_already_present==False:
						new_output_list.append(buff_item)
	# OK, we are done merging, now save the new list back into wlist by overwriting it
	return new_output_list

def leet_indexes(word):
	replaceable = ['a','b','c','e','g','i','l','o','s','t','z']
	ret_indexes = []
	for i in range(0,len(word)-1):
		for r in replaceable:
			if r==word[i]:
				ret_indexes.append(i)
	return ret_indexes
	
def leet(word_string):
	word = list(word_string)
	word_alternative = word.copy()
	return_values = []
	indexes = leet_indexes(word)
	indexes_alternative = indexes.copy() # the alternative version, if needed
	if(len(indexes)==0):
		return [word_string]
	for i in range(0,len(indexes)): # iterate over replaceable characters
	# This is where we decide whether we replace the character or not.
	# The default is yes, however we might skip the replacement
	# if we find that the neighboring character is also replaceable
	# the goal is not to replace both neighboring characters, but instead
	# create two instances of the string, one where one of the chars is replaced
	# another one when the other one is replaced
	# So we are about to replace words[indexes[i]] now, unless...
		replace=True
		replace_next=False
		# we do not really need to iterate over all other characters
		# just check the neighbor to the right
		if i+1<len(indexes):
			if indexes[i+1]-indexes[i]==1: # check if the difference is one
			# so we are dealing with neighbors
				if word_string[indexes[i]]!=word_string[indexes[i+1]]: # check if the character is NOT the same
					# this condition was redundant here
					#if (word_string[indexes[i]]=='i' and word_string[indexes[i+1]]=='l') or (word_string[indexes[i]]=='l' and word_string[indexes[i+1]]=='i'):
					replace=False
					# this is where we can create alternative replacement
					# so if we averted replacing Steven -> s73v3n, but did st3v3n instead
					# now we also want to create s7even
					# so we set replace_next_new = true
					# which will force the creation of another copy and have its character replaced instead
					# create an instance with the one particular character (skipped in normal order) replaced
					## i, i+1 should be added to a list of alternative replacements
					# so, at this point we should remove "i" from the indexes_alternative list
					indexes_alternative.remove(indexes[i+1])
				else:
					replace_next=True # the next char is the same, replace it
		
		if replace==True:
			index_range = [i]
			if replace_next:
				index_range.append(i+1)
	
			# create instances with single characters replaced
			for j in index_range:
				if word_string[indexes[j]]=='a': # this should have a second-instance version
					word[indexes[j]]='@'
				if word_string[indexes[j]]=='b':
					word[indexes[j]]='8'
				if word_string[indexes[j]]=='c': # this should have a second-instance version
					word[indexes[j]]='('
				if word_string[indexes[j]]=='e':
					word[indexes[j]]='3'
				if word_string[indexes[j]]=='g':
					word[indexes[j]]='9'
				if word_string[indexes[j]]=='i': 
					word[indexes[j]]='1'
				if word_string[indexes[j]]=='l':
					word[indexes[j]]='1'
				if word_string[indexes[j]]=='o':
					word[indexes[j]]='0'
				if word_string[indexes[j]]=='s':
					word[indexes[j]]='5'
				if word_string[indexes[j]]=='t':
					word[indexes[j]]='7'
				if word_string[indexes[j]]=='z':
					word[indexes[j]]='2'
	
	return_values.append("".join(word))
	if(len(indexes)!=len(indexes_alternative)): # there is an alternative version of the word
		for j in indexes_alternative:
				if word_string[j]=='a': # this should have a second-instance version
					word_alternative[j]='@'
				if word_string[j]=='b':
					word_alternative[j]='8'
				if word_string[j]=='c': # this should have a second-instance version
					word_alternative[j]='('
				if word_string[j]=='e':
					word_alternative[j]='3'
				if word_string[j]=='g':
					word_alternative[j]='9'
				if word_string[j]=='i': 
					word_alternative[j]='1'
				if word_string[j]=='l':
					word_alternative[j]='1'
				if word_string[j]=='o':
					word_alternative[j]='0'
				if word_string[j]=='s':
					word_alternative[j]='5'
				if word_string[j]=='t':
					word_alternative[j]='7'
				if word_string[j]=='z':
					word_alternative[j]='2'
		return_values.append("".join(word_alternative))
	# ok, now create alternatives here
	## Algorithm:
	## 1. Identify replaceable characters along with indexes, e.g. o=>0,4; i=>2.
	## 2. Iterate over them.
	## 3. Inside that iteration, iterate again.
	## 4. Inside each iteration, make two copies of the string; one with and one without the replacement.
	## 5. Skip replacement when indexes are adjacent (e.g. 1 and 2, 4 and 5), unless the characters behind them are equal.
	return return_values

# END OF FUNCTION DEFINITIONS

if if_arg('usage') or if_arg('h'):
	usage()
	exit()
	
# ARGUMENT PARSING
# depth
try:
	depth=int(get_arg('depth'))
except ValueError:
	depth=0

if(depth>5 or depth<1):
	depth=1 # depth was not specified or out of range (1-5), falling back to default
	
# output directory
output_directory=get_arg('o')
if(output_directory==""):
	output_directory=os.getcwd()
if(not os.path.isdir(output_directory)):
	print("ERROR: Invalid output directory specified ("+output_directory+"), falling back on cwd: "+os.getcwd())
	output_directory=os.getcwd()

# usernames
usernames_list=get_arg('usernames')
if(usernames_list!=""):
	usernames=usernames_list.split(",")

# Variation settings, currently fixed/derived from the depth
# Default values
case_sens=True
first_cap=True # applies only if case_sens=1
append_numbers=True
append_years=True
append_popular_suffixes=True
leet_rules=False

# depth=1 (default)
numbers_to_append=2
years_to_append=2
popular_suffixes_to_append=2

if(depth>1):
	leet_rules=True
	
if(depth==2):
	numbers_to_append=4
	years_to_append=4
	popular_suffixes_to_append=4
if(depth==3):
	numbers_to_append=6
	years_to_append=6
	popular_suffixes_to_append=6
if(depth==4):
	numbers_to_append=8
	years_to_append=8
	popular_suffixes_to_append=8
if(depth==5):
	numbers_to_append=10
	years_to_append=10
	popular_suffixes_to_append=-1 # -1 means all, the list will be loaded from a file and will grow gradually

## OK, time to generate

wordlist_files=[default_wordlist, months_seasons_wordlist]
wordlists=get_arg('custom')
if(wordlists==""):
	# wordlists were not specified, use the default set (we need to work on this default set as well)
	# as it makes no sense to come up with a completely new list every time
	# so this provided by default "built-in" set should be good, while its length should depend on the depth parameter (which means there should be five versions of it, whereas only the fifth one is the full one)
	if if_arg('only-custom'):
		print("ERROR: no wordlists were specified while -only-custom argument was used. No words to use for list generation, qutting.")
		usage()
		exit()
else:
	if if_arg('only-custom'):
		wordlist_files=wordlists.split(',')
	else:
		wordlist_files=wordlist_files+wordlists.split(',')

## Basically we want our basic universal wordlist + any custom words (preferred over the basic one). Also, would be nice to deduplicate these result (without changing the order if items) right away at this point.

## Load the wordlists
custom_words_content=[]
custom_words_content = usernames + custom_words_content  # start with the usernames, obviously

for wordlist_file in wordlist_files:
	custom_words_content=load_wordlist(wordlist_file,custom_words_content)

## Now, the entire following part should be split between the input usernames, to make the output results fine-tuned.
## Each username will be simply prepended to the wordlist, it will also result in a separate output file.

## Declare output word lists
output = []
words = custom_words_content
Words = []
words_leet = []
Words_leet = []
words_suffix = []
Words_suffix = []
words_leet_suffix = []
Words_leet_suffix = []

## Start generating
## First uppercase
if case_sens==True:
	if first_cap==True:
		for word in words:
			Words.append(word.title())
## OK, so far we have words + Words propagated
			
## Now, leet rules
if(leet_rules==True):
	# words
	for word in words:
		ret_words_leet=leet(word)
		for word_leet in ret_words_leet:
			if(word_leet!=word):	# avoid creation of duplicates by applying these rules on passwords like 12345
				words_leet.append(word_leet)

	# Words
	if(case_sens==True and first_cap==True):
		for Word in Words:
			ret_Words_leet=leet(Word)
			for Word_leet in ret_Words_leet:
				if(Word_leet!=Word): 
					Words_leet.append(Word_leet)
					
# OK, so far so good.
output = words + Words + words_leet + Words_leet  ## this is part of the final result already

output_copy = output.copy() # working copy to iterate for further mutations

# Declare years, numbers and other popular suffixes
numbers = [1,2,3,4,5,6,7,8,9,0]
current_year=datetime.date.today().year
years=[current_year]
for i in range(1,10): # generate a list of the last 10 years
	years.append(current_year-i)
popular_suffixes = ["!","12","!@","123","!@#$","1234","!@#$%","12345","21","@!","321","#@!","111","222","333","999"]

if popular_suffixes_to_append==-1:
	popular_suffixes_to_append=len(popular_suffixes)
	
# Now, append suffixes in an optimum way (the most probable first)
for word in output_copy:
	i=0
	while True:
		move_on=False
		# 1. numbers
		if append_numbers==True:
			if(i<numbers_to_append): # must be smaller, e.g. 2<3, with 2 being the third (max) index
				output.append(word+str(numbers[i]))
				move_on=True

		# 2. years
		if append_years==True:
			if(i<years_to_append):
				output.append(word+str(years[i]))
				move_on=True

		# 3. popular predefined suffixes
		if(i<popular_suffixes_to_append):
				output.append(word+popular_suffixes[i])
				move_on=True
		i=i+1
		if move_on==False: # none of the iterations added anything, which means i exceeded the highest maximum
			break

# OK, now generate the output filename based on current timestamp and number of words inside.
if if_arg("stdout"):
	for password in output:
		print(password)
else:
	output_filename=strftime("%Y-%m-%d_%H%M%S", gmtime())+"_"+str(len(output))+".txt"
	fo=open(output_directory+"/"+output_filename,'w')	
	for item in output:
		fo.write("%s\n" % item)
	print("Done. Generated "+str(len(output))+" passwords (based on "+str(len(words))+" basic words from the wordlists) saved in "+output_directory+"/"+output_filename)

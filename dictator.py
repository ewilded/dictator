#!/usr/bin/python
import datetime

# Variation settings
case_sens='y'
first_cap='y'
phrase_base_first_cap='y'
append_numbers='y'
append_years='y'
use_dates='y'
append_years_per_phrase=6 	#change to 1, 2, 3 etc. to use only first 1,2,3 lines from the years file in word+number patterns, set to 'all' otherwise
append_numbers_per_phrase=4 #change to 1, 2, 3 etc. to use only first 1,2,3 lines from the numbers file in word+number patterns, set to 'all' otherwise
use_names='y'
#phrase_separators=['']
phrase_separators=['','_','-']

languages=['en']

## Build dictionary locations
output='result.txt'
custom_words='wordlists/custom.txt'
universal_words='wordlists/universal.txt'
letters='wordlists/letters1.txt' #letters list (2 and 3 contain 2-3 long variations)
years='wordlists/years.txt'
numbers='wordlists/numbers.txt'
phrase_prefixes='wordlists/phrase_prefixes.txt'
#phrase_base='wordlists/phrase_base.txt'
## Languages to use; supported values: en (dictionaries for other languages need to be developed/translated)

buff=[]
custom_words_content=[]
base_words_content=[]
months_content=[]
months_short_content=[]
names_content=[]
letters_content=[]
numbers_content=[]
universal_words_content=[]
phrase_prefixes_content=[]
years_content=[]
dates_content=[]

# A date from month ago seems to be most probable hit (it might be good to also make sure we do not point to a weekend)
if use_dates=='y':
	now = datetime.datetime.now()
	monthago=now+datetime.timedelta(days=-30)
	dates_content.append(monthago.strftime("%Y-%m-%d"))
	dates_content.append(monthago.strftime("%Y\%m\%d"))
	dates_content.append(monthago.strftime("%Y-%m"))
	dates_content.append(monthago.strftime("%Y\%m"))
# function/method for wordlist loading

def load_wordlist(wpath,wlist):
	with open(wpath,'r') as f:
		buff=list(f)
		for item in buff:	
			wlist.append(item.rstrip().lower())
	
load_wordlist(custom_words,custom_words_content)
load_wordlist(universal_words,universal_words_content)
load_wordlist(letters,letters_content)
load_wordlist(numbers,numbers_content)
load_wordlist(years,years_content)
load_wordlist(phrase_prefixes,phrase_prefixes_content)


universal_words_content+=phrase_prefixes_content

for ln in languages:	
	with open('wordlists/'+ln+'/base.txt','r') as f:
		buff=list(f)
		for item in buff:	
			base_words_content.append(item.rstrip().lower())
	with open('wordlists/'+ln+'/months.txt','r') as f:
		buff=list(f)
		for item in buff:	
			months_content.append(item.rstrip().lower())
	if use_names=='y':
		with open('wordlists/'+ln+'/names.txt','r') as f:
			buff=list(f)
			for item in buff:	
				names_content.append(item.rstrip().lower())

# let's make the short months now
months_unique=set(months_content)
months_content=list(months_unique)
# Get short representation of the months
for m in months_content:
	months_short_content.append(m[:3])
# Ok, basic contents already read, now its time to create the actual list of payloads
# First, simple concatenation
# content=base_words_content+months_content+names_conent
output_content_unique=set(base_words_content+months_content+months_short_content+names_content+letters_content+years_content+phrase_prefixes_content+universal_words_content+dates_content)
output_content=list(output_content_unique)

if case_sens=='y':
	if first_cap=='y':
		for l in base_words_content:
			output_content.append(l.title())
		for l in months_content:
			output_content.append(l.title())
		for l in months_short_content:
			output_content.append(l.title())
		for l in names_content:
			output_content.append(l.title())
		for l in letters_content:
			output_content.append(l.title())

# Numbers append
if append_numbers=='y':
		up_to_num=append_numbers_per_phrase
		if append_numbers_per_phrase=='all':
			up_to_num=len(numbers_content)
		for i in range(0,up_to_num):
			num=numbers_content[i]
			for l in base_words_content:
				output_content.append(l+num)
			for l in months_content:
				output_content.append(l+num)
			for l in months_short_content:
				output_content.append(l+num)	
			for l in names_content:
				output_content.append(l+num)
			for l in letters_content:
				output_content.append(l+num)
			for l in universal_words_content:
				output_content.append(l+num)

# Years append
if append_years=='y':
		up_to_year=append_years_per_phrase
		if append_years_per_phrase=='all':
			up_to_year=len(years_content)
		for i in range(0,up_to_year):
			year=years_content[i]
			for l in base_words_content:
				output_content.append(l+year)
			for l in months_content:
				output_content.append(l+year)
			for l in months_short_content:
				output_content.append(l+year)
			for l in names_content:
				output_content.append(l+year)
			for l in letters_content:
				output_content.append(l+year)
			for l in universal_words_content:
				output_content.append(l+year)
				
# Ok, now is the time for the phrase builder
for pref in phrase_prefixes_content:
	for word in base_words_content+universal_words_content:
		for separator in phrase_separators:
			if pref!=word:
				output_content.append(pref+separator+word)
				if case_sens=='y':
					if first_cap=='y':
						if separator=='':
							output_content.append(pref+separator+word.title())
							if phrase_base_first_cap=='y': 
								output_content.append(pref.title()+word.title())
						
fo=open(output,'w')
for item in output_content:
  fo.write("%s\n" % item)

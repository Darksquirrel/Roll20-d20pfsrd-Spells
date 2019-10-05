import bs4 as bs
import requests
from glob import glob

# pyinstaller -F "Spell Macro Generator.py"

def gensoup(url):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36', 'Accept-Encoding': 'identity'}
	r = requests.get(url, headers=headers)
	return bs.BeautifulSoup(r.content, 'lxml')
		
def GenReplaceDict(url,SpellLevel,CastingStat):
	try:
		School=None
		ActionType=None
		Components=None
		Range=None
		Area=None
		EffectType=None
		Duration=None
		Save=''
		DC=None
		soup = gensoup(url)
		i = soup.find('div', attrs={'class':"article-content"})
		School,_,_ = i.find_next('p').text.partition(';')
		Name = i.find_previous('h1').text
		Resist,Effect='',''
		for t in soup.find_all('p', attrs={"class":"divider"}):
			if t.text == 'CASTING':
				ActionType = t.find_next('p').text.replace('Casting Time ','')
				if 'Components ' in ActionType:
					ActionType,_,Components = ActionType.partition('Components ')
				elif 'Component' in ActionType:
					ActionType,_,Components = ActionType.partition('Component')
			elif t.text == 'EFFECT':
				mystr = t.find_next('p').text.replace('Range ','')
				if 'Area' in mystr:
					EffectType = 'Area'
					Range,sep,tail = mystr.partition('Area')
					Range = Range.replace('.','')
				elif 'Target' in mystr:
					EffectType = 'Target'
					Range,sep,tail = mystr.partition('Target')
					Range = Range.replace('.','')
				elif 'Effect' in mystr:
					EffectType = 'Effect'
					Range,sep,tail = mystr.partition('Effect')
					Range = Range.replace('.','')
				if 'Area' in mystr or 'Target' in mystr or 'Effect' in mystr:
					Area,sep,tail = tail.partition('Duration ')
					Duration,sep,tail = tail.partition('Saving Throw ')
					Save,sep,Resist = tail.partition('Spell Resistance ')
				else:
					Area, Duration = ' ', ' '
					Save,sep,Resist = mystr.partition('Spell Resistance ')
					Save = Save.replace('Saving Throw ','')
			elif t.text == 'DESCRIPTION':
				head,sep,tail = str(t.find_parent('div').text).partition('DESCRIPTION')
				Effect,sep,tail = tail.partition('\n\n')
				Effect=Effect.replace('\n',' ')
				Effect,_,_ = Effect.partition('.')
			if Effect!='':
				break
				
				
		if 'Fort' in Save or 'Ref' in Save or 'Will' in Save:
			DC='[[10+%s+@{%s-mod}]]'%(SpellLevel,CastingStat)
		else:
			DC='See Text'
		Save = 'N/A' if Save == '' else Save
		School=' ' if School == None else School
		ActionType=' ' if ActionType == None else ActionType
		Components=' ' if Components == None else Components
		Range=' ' if Range == None else Range
		Area=' ' if Area == None else Area
		EffectType=' ' if EffectType == None else EffectType
		Duration=' ' if Duration == None else Duration
		Effect=' ' if Effect == None else Effect
		ReplaceDict = {
			'URLREPLACE':url,
			'ZZZZ':SpellLevel+' - '+Name,
			'zzzz':Name,
			'AAAA':School,
			'BBBB':ActionType,
			'CCCC':Components,
			'YYYY':Range,
			'XXXX':Area,
			'DDDD':EffectType,
			'WWWW':Duration,
			'VVVV':Save,
			'UUUU':DC,
			'TTTT':Resist,
			'SSSS':Effect
			}
		return ReplaceDict
	except KeyboardInterrupt as e:
		pass
	#except Exception as e:
		#print(Name, url, e)
	
def GenMacroStr():	# MacroStr=GenMacroStr()
	MacroStr='| ZZZZ, &amp;{template:pf_attack} '
	MacroStr+='{{name=[zzzz](URLREPLACE) AAAA}}'
	MacroStr+='{{Cast Time= BBBB}} '
	MacroStr+='{{Components= CCCC}} '
	MacroStr+='{{Range= YYYY}} '
	MacroStr+='{{DDDD= XXXX}} '
	MacroStr+='{{Duration= WWWW}} '
	MacroStr+='{{Save= VVVV UUUU}} '
	MacroStr+='{{Spell Resist= TTTT}} '
	MacroStr+='{{Effects= SSSS}}'
	return MacroStr

def GenLists(Folder):	# ListofLists = GenLists()
	ListofLists = []
	globlist = glob('Spell Lists/%s/*.txt'%(Folder))
	for file in globlist:
		with open(file, 'r') as f:
			ListofLists.append(f.readlines())
	return ListofLists

def Main(CastingStat,Folder):
	MacroStr=GenMacroStr()
	TotalStr = '/w gm ?{Select a Spell to Cast '
	for Urls in GenLists(Folder):
		for i in range(len(Urls)):
			print(Urls[i])
			if i==0:
				SpellLevel = Urls[i]
				output = ''
			else:
				output = MacroStr
				url = Urls[i].replace('\n','')
				for key, value in GenReplaceDict(url,SpellLevel,CastingStat).items():
					output = output.replace(key,value.replace(',','').replace('\n','').replace('\t',''))
				TotalStr+=output
	print((TotalStr.replace('}','&#125;').replace('mod&#125;','mod}'))+'}')
	
	# https://www.d20pfsrd.com/magic/all-spells/m/make-whole
	#$ addd try except build this | Make Whole, &amp;{template:pf_attack&#125; {{name=[Make Whole](https://www.d20pfsrd.com/magic/all-spells/m/make-whole)&#125;&#125;{{Cast Time= See Link &#125;&#125;}

if __name__ == '__main__':
	CastingStat = input('Enter Casting Stat (INT/WIS/WIS)')
	Folder = input('Enter Name of Folder to read (Shep Divine for \'Spell Lists\\Shep Divine\\\')')
	#Folder = 'Nara Arcane'
	#CastingStat = 'CHA'
	Main(CastingStat,Folder)
	input('\nPress enter to close')
	
	
	
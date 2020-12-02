import requests, json, datetime, os
from pathlib import Path
from sys import argv

configs = json.load(open('./configs.json'))
dataDirectory = os.getcwd() + '/data/'

def getData(url):
	headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}

	return requests.get(url.strip(), headers=headers).json()

def extract():
	sections = configs['sections'].replace(' ', '').split(',')
	sort = configs['sort'] # options: new, top, controversial
	sortdur = configs['sortdur'] # options: ?t = today,week, month,year,all
	limit = configs['limit']
	tries = int(configs['tries'])

	base = 'https://www.reddit.com/r/'
	filename = str(datetime.date.today())
	output = {}

	extractables = ['title', 'author_fullname', 'ups', 'thumbnail', 'permalink']
	for subreddit in sections:
		print(f'Processing {subreddit}...')

		output[subreddit] = []
		currentTry = 1
		url = f'{base}{subreddit}/{sort}.json?t={sortdur}&limit={limit}'
		while currentTry < tries:
			readable = getData(url)
			if 'data' not in readable:
				currentTry += 1
				print(f'Retrying {subreddit} [Try: {currentTry} / {tries}')
				continue

			break

		if 'data' not in readable:
			print(f'Error processing {subreddit}, max tries ({tries}) reached')
			print(readable)
			continue

		posts = readable['data']['children']
		for single in posts:
			current = {}
			post = single['data']

			for item in extractables:
				if item in post:
					current[item] = post[item]

			output[subreddit].append(current)

	filename = dataDirectory + filename + '.json'
	output = json.dumps(output, indent=4)

	file = open(filename, 'w')
	file.write(output)
	file.close()

	print(f'Output: {filename}')

def read():
	paths = sorted(Path(dataDirectory).iterdir(), key=os.path.getmtime)
	paths.reverse() # latest first
	separator = '=' * 40

	for file in paths:
		size = os.path.getsize(file)
		if size > 100:
			readable = json.load(open(file))
			for subreddit, posts in readable.items():
				print(separator)
				print(f'/r/{subreddit} ({configs["sort"]} {configs["limit"]} of {configs["sortdur"]})')
				print(separator)

				for post in posts:
					print(f"{post['title']} ({post['ups']})")
					print(f"https://reddit.com{post['permalink']}\n")
			break

if len(argv) < 2:
	print(__file__ + str(' [read || extract || extract_read]'))
else:
	mode = argv[1]
	if 'extract' in mode:
		extract()

	if 'read' in mode:
		read()
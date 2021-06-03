#!/usr/bin/env python3

import requests
from lxml import html
import sys
import glob
import os
import json
import time
import datetime


def main(in_fn, out_fn, hero, mult):
	file_input = read_file(in_fn)
	output = pn2ps(file_input, hero, mult)
	game_info(output)
	save_output(out_fn, output)


def read_file(in_fn): 
	with open(in_fn, 'r') as f:
		data = f.read()

	data = data.replace('Flop', 'flop')
	data = data.replace('Turn', 'turn')
	data = data.replace('River', 'river')
	
	return data


# Converts log to Poker Stars format using web request
def pn2ps(raw, hero, mult):
	url = 'https://pokernowconvert.herokuapp.com/logs'
	data = {'heroname' : hero,
			'multiplier' : mult,
			'raw' : raw}

	r = requests.post(url, data = data)
	tree = html.fromstring(r.content)
	output = tree.xpath('//*[@id="convertedTextarea"]')[0]

	return output.text


def game_info(output):
	hands = output.split('\n\n')
	first_hand = hands[0]
	lines = first_hand.split('\n')
	print(lines[0].split(': ')[1][:-12], '\n')

	start, end = None, None
	for i, hand in enumerate(hands):
		if '#' not in hand:
			continue

		lines = hand.split('\n')
		time_struct  = time.strptime(lines[0].split('- ')[1][:-3], "%Y/%m/%d %H:%M:%S")
		
		if 'Dealt to' in hand and start == None:
			start = time_struct
		
		if i != 0 and 'Dealt to' in hands[i - 1]:
			end = time_struct

	t1, t2 = time.mktime(start), time.mktime(end)
	print(f"Played from {time.strftime('%H:%M', start)} to {time.strftime('%H:%M', end)} ({datetime.timedelta(seconds=t2-t1)})")

	print(f'Hands played: {count_hands(hands)}')


def count_hands(hands):
	return len([hand for hand in hands if 'Dealt to' in hand])


def save_output(out_fn, output):
	with open(out_fn, "w") as f:
		f.write(output)


if __name__ == "__main__":
	# Loads config file
	with open('config.json', 'r') as f:
		info = json.load(f)

	hero, mult = info['hero'], 1

	# Custom multiplier
	if len(sys.argv) == 2:
		mult = sys.argv[1]

	# Runs on all logs that don't have 
	list_of_files = glob.glob(info['csv_dir'])

	for file in list_of_files:
		# Saves file as same name but with .txt
		in_fn = file
		paths = in_fn.split('/')
		out_fn = info['txt_dir'] + paths[-1][:-3] + 'txt'

		if not os.path.exists(out_fn):
			print('-'*80)
			print(in_fn)
			main(in_fn, out_fn, hero, mult)
			print()

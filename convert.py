#!/usr/bin/env python3

import requests
from lxml import html
import sys
import re
import glob
import os
import json
from tqdm import trange

def main(in_fn, out_fn, hero, mult):
	file_input = read_file(in_fn)
	output = pn2ps(file_input, hero, mult)
	save_output(out_fn, output)
	print(f'Hands played: {count_hands(output)}')


def read_file(in_fn): 
	with open(in_fn, 'r') as f:
		data = f.read()

	data = data.replace('Flop', 'flop')
	data = data.replace('Turn', 'turn')
	data = data.replace('River', 'river')
	
	return data


def pn2ps(raw, hero, mult):
	url = 'https://pokernowconvert.herokuapp.com/logs'
	data = {'heroname' : hero,
			'multiplier' : mult,
			'raw' : raw}

	r = requests.post(url, data = data)
	tree = html.fromstring(r.content)
	output = tree.xpath('//*[@id="convertedTextarea"]')[0]

	return output.text


def count_hands(text):
	hands = text.split('\n\n')

	hands_played = len([hand for hand in hands if 'Dealt to' in hand])

	return hands_played


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
			print(out_fn)

		# main(in_fn, out_fn, hero, mult)

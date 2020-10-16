import argparse
import requests
import json
import csv

IDURL ="https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&field=place_id&location={},{}&radius={}&keyword={}"
NIDURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&field=place_id&location={},{}&radius={}&keyword={}&pagetoken={}"
BURL = "https://maps.googleapis.com/maps/api/place/details/json?placeid={}&fields=name,formatted_address,formatted_phone_number,website,rating&key={}"
GURL = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}"

api_key = ""

parser = argparse.ArgumentParser(description='headless google maps api')
parser.add_argument('-f', '--filename', type=str, help='filename to output too')
parser.add_argument('-i', '--input', type=str, help='input file with desired types')
parser.add_argument('-t', '--type', type=str, help='type for solo scans')
parser.add_argument('-a', '--address', type=str, help='address')
parser.add_argument('-r', '--radius', type=int, help='search radius', default=30)
parser.add_argument('-k', '--key', type=str, help='google maps api key')


def get_gcode(addr):
	res = requests.get(GURL.format(addr, api_key))
	try:
		jdata = json.loads(res.text)
		lat = jdata.get('results')[0].get('geometry').get('location').get('lat')
		lon = jdata.get('results')[0].get('geometry').get('location').get('lng')
	except:
		print('gcode issue, check address')
		exit()
	return lat, lon

def get_ids(btype, x, y, rad, token=None):
	ids = []
	if token:
		res = requests.get(NIDURL.format(api_key,x,y,rad,btype,token))
	else:
		res = requests.get(IDURL.format(api_key,x,y,rad,btype))
	jdata = json.loads(res.text)
	for i in jdata.get("results"):
		ids.append(i["place_id"])
	if jdata.get("next_page_token"):
		ids += get_ids(btype,x,y,rad,jdata.get("next_page_token"))
	ids = list(set(ids))
	return ids


def get_b(b_id):
	res = requests.get(BURL.format(b_id, api_key))
	jdata = json.loads(res.text)
	print(jdata)
	jdata = jdata.get('result')
	name = jdata.get('name')
	address = jdata.get('formatted_address')
	phone = jdata.get('formatted_phone_number')
	rating = jdata.get('rating')
	website = jdata.get('website')

	return {
		'id' : b_id,
		'name' : name,
		'address' : address,
		'phone' : phone,
		'rating': rating,
		'website' : website
	}


def strip_file(file_n):
	with open(file_n, 'r') as a:
		data = a.readlines()
	return data

def to_json(data, filename):
	jdict = {}
	for i in data:
		jdict[i.get('id')] = i
	with open(filename, 'w+') as a:
		json.dump(jdict, a)

def to_csv(data, filename):
	try:
		keys = data[0].keys()
		with open(filename, 'w+') as a:
			writer = csv.DictWriter(a, keys)
			writer.writeheader()
			for d in data:
				writer.writerow(d)
	except:
		with open(filename, 'w+') as a:
			a.write('types\n')
			a.write('no buisnesses found of this type')

if __name__ == "__main__":
	args = parser.parse_args()
	b_data = []

	if not args.key:
		print('no api key supplied')
		exit()
	else:
		api_key = args.key

	if not args.filename:
		print('no output file supplied')
		exit()

	if args.address:
		lat, lon = get_gcode(args.address)
	else:
		print("no address supplied")
		exit()

	if args.input and args.type:
		print('Pick either input file or type')
		exit()
	elif args.type:
		btype = args.type
		ids = get_ids(btype, lat, lon, args.radius)
		for i in ids:
			print('getting buisness {}'.format(i))
			b_data.append(get_b(i))
		to_csv(b_data, str(args.filename)+"_"+btype+".csv")

	elif args.input:
		btypes = strip_file(args.input)
		for i in btypes:
			b_data = []
			ids = get_ids(i, lat, lon, args.radius)
			for a in ids:
				b_data.append(get_b(a))
			fname = str(args.filename) +"_"+ i +".csv"
			to_csv(b_data, fname)

	else:
		print('no types recieved')
		exit()






#!/usr/bin/python3
import urllib.request
import requests
import os
import re
import getopt
import sys
from shutil import copy, rmtree
from checksumdir import dirhash

def parse_args():
  argv = sys.argv[1:]
  opts, args = getopt.getopt(argv, 'x:y:')
  return args

def get_elem_safe(arr, ind):
  try:
    return arr[ind]
  except:
    return None

keybase_name = get_elem_safe(parse_args(), 0) or 'regul'
mods_url = f'https://keybase.pub/{keybase_name}/docs/mods/'

def parse_html():
  global mods_url
  html = urllib.request.urlopen(mods_url).read().decode("utf-8")
  rg = re.compile('"https.*jar\"')

  res = [''.join(s.split('"')) for s in rg.findall(html)]
  return res

#                 urls string[]
def download_mods(urls, local_path, target_path):
  global keybase_name
  rg0 = re.compile(f'{keybase_name}\/')
  rg1 = re.compile("\:\/\/")
  rg2 = re.compile("mods\/.*\?")

  for url in urls:
    name = ''.join(rg0.findall(url))
    url = url.replace(name, '')
    download_name = name.replace('/', '.')
    download_url = url.replace(''.join(rg1.findall(url)),'://' + download_name) + '?dl=1'
    filename = url[30:]
    print(f'Downloading {filename}')
    urllib.request.urlretrieve(download_url, f'./{local_path}/{filename}')

  print('Files downloaded')
  synchronize(local_path, target_path)

def get_diff(path0, path1):
  h0 = dirhash(path0)
  h1 = dirhash(path1)
  return h0 != h1

def clear(path):
  print(f'Clearing directory {path}')
  for f in os.listdir(path):
    try:
      os.remove(path + '/' + f)
    except:
      rmtree(path + '/' + f)

def synchronize(path0, path1):
  print('Starting sync')

  if (get_diff(path0, path1)):
    clear(path1)
    [ copy(path0 + '/' + f, path1 + '/' + f) for f in os.listdir(path0) ]
    print('Synchronized successfully')
  else: print('Up to date - exit')

def main():
  local_path = f'{get_elem_safe(parse_args(), 1) or "./data"}'
  target_path = f'{get_elem_safe(parse_args(), 2) or os.path.expanduser("~") + "/.minecraft/mods"}'
  if not os.path.exists(local_path):
    print('Creating data directory')
    os.mkdir(local_path)

  clear(local_path)
  download_mods(parse_html(), local_path,  target_path)

if __name__ == '__main__':
  main()


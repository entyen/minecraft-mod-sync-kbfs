#!/usr/bin/python3
import urllib.request
import contextlib
import os
import re
import getopt
import sys
import time
import threading
import requests
import ctypes
from shutil import copy, rmtree
from checksumdir import dirhash

def parse_args():
  argv = sys.argv[1:]
  try:
    opts, args = getopt.getopt(argv, 'x:y:')
    return args
  except:
    return []

def get_elem_safe(arr, ind):
  try:
    return arr[ind]
  except:
    return None

keybase_name = get_elem_safe(parse_args(), 0) or 'regul'
mods_url = f'https://keybase.pub/{keybase_name}/docs/mods/'
servers_url = f'https://keybase.pub/{keybase_name}/docs/servers.dat' # TODO

if os.name == 'nt':
  slash = '\\'
  mc_path = os.path.expandvars("%appdata%")
else: 
  slash = '/'
  mc_path = os.path.expanduser("~")

def parse_html():
  global mods_url
  html = urllib.request.urlopen(mods_url).read().decode("utf-8")
  rg = re.compile('"https.*jar\"')

  res = [''.join(s.split('"')) for s in rg.findall(html)]
  return res

#                 urls string[]
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def dowlnoad_urlm(url, filename):
  with open(filename, 'wb') as out_file:
    with contextlib.closing(urllib.request.urlopen(url)) as fp:
        block_size = 1024 * 8
        while True:
            block = fp.read(block_size)
            if not block:
                break
            out_file.write(block)

def download_mods(urls, local_path, target_path):
  global keybase_name
  rg0 = re.compile(f'{keybase_name}\/')
  rg1 = re.compile("\:\/\/")
  rg2 = re.compile("mods\/.*\?")
  procs = []

  for url in urls:
    name = ''.join(rg0.findall(url))
    url = url.replace(name, '')
    download_name = name.replace('/', '.')
    download_url = url.replace(''.join(rg1.findall(url)),'://' + download_name) + '?dl=1'
    filename = url[30:]
    print(f'Downloading {filename}')
    p = threading.Thread(target=dowlnoad_urlm, args=(download_url, f'./{local_path}/{filename}'))
    p.start()
    procs.append(p)

  while True in [p.is_alive() for p in procs]:
    nconv = int(p.name.split('-')[1].split(' ')[0])
    sum = len(threading.enumerate()) - (nconv - len(procs))
    progress(len(procs) - sum, len(procs))
    time.sleep(0.25)
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
      os.remove(path + slash + f)
    except:
      rmtree(path + slash + f)

def synchronize(path0, path1):
  print('Starting sync')

  if (get_diff(path0, path1)):
    clear(path1)
    [ copy(path0 + slash + f, path1 + slash + f) for f in os.listdir(path0) ]
    print('Synchronized successfully')
    clear(path0)
    os.rmdir(path0)
  else:
    print('Up to date - exit')
    clear(path0)
    os.rmdir(path0)

def main():
  local_path = f'.{slash}.data'
  target_path = f'{mc_path}{slash}.minecraft{slash}mods'
  if not os.path.exists(local_path):
    print('Creating data directory')
    os.mkdir(local_path)
    if os.name == 'nt':
      FILE_ATTRIBUTE_HIDDEN = 0x02
      ret = ctypes.windll.kernel32.SetFileAttributesW(local_path, FILE_ATTRIBUTE_HIDDEN)

  clear(local_path)
  download_mods(parse_html(), local_path,  target_path)

if __name__ == '__main__':
  main()

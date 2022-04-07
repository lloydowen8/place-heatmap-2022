# Robin Gisler
# https://github.com/gislerro/rplace-cropped-timelapse-creator/blob/main/scraper.py

import os
import io
import sys
import requests
import queue
import time

from PIL import Image
from bs4 import BeautifulSoup
from threading import Thread
from tqdm import tqdm

url = 'https://rplace.space/combined/'
img_url = lambda id: f'{url}/{id}.png'

cache = 'image_cache'
img_cache = lambda id: f'{cache}/{id}.png'

def get_image_ids(start_id, end_id, granularity):
   res = requests.get(url)
   
   ids = []
   if res.status_code == 200:
      soup = BeautifulSoup(res.text, 'html.parser')
      for a in soup.find_all('a'):
         id = os.path.splitext(a.get('href'))[0]
         try:
            id = int(id)
            if id > end_id:
               break
            if id >= start_id:
               ids.append(id)
         except ValueError: # skip <a> tags that aren't image links
            continue
   else: 
      print(f'Could not get image ids from {url}')
      sys.exit()
      
   return ids[::granularity]

def init_fetch_images(ids, t):
   os.makedirs(cache, exist_ok=True)
   q = queue.Queue()
   for id in ids:
      q.put(id)
      
   for i in range(t):
      w = Worker(q, i)
      w.setDaemon(True)
      w.start()

class Worker(Thread):
   def __init__(self, request_queue, wid):
      Thread.__init__(self)
      self.queue = request_queue
      self.wid = wid

   def run(self):
      n = self.queue.qsize()
      pbar = tqdm(desc='Image download',
                  ascii=True,
                  total=n,
                  disable= self.wid != 0,
                  leave=False)
      while True:
         if self.queue.empty():
            break
         id = self.queue.get()
         try:
            img = Image.open(img_cache(id))
            img.load()
         except:
            res = requests.get(img_url(id), stream=True)
            if res.status_code == 200:
               img = Image.open(io.BytesIO(res.content))
               img.save(img_cache(id), 'PNG')
            else:
               print(f'Could not download image {id}')
               sys.exit()
         if self.wid == 0:
            pbar.n = n - self.queue.qsize()
            pbar.refresh()
      self.queue.task_done()
            

def get_image(id):
   while True:
      try:
         img = Image.open(img_cache(id))
         img.load()
         break
      except:
         time.sleep(1)
   return img
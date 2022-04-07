import yaml
import cv2
import numpy as np

from PIL import Image
from tqdm import tqdm

import scraper
from img_processing import HeatmapGenerator

def get_img_pair(img_ids, idx):
    return scraper.get_image(img_ids[idx-1]), scraper.get_image(img_ids[idx])

with open('config.yaml', 'r') as f:
   config = yaml.load(f, Loader=yaml.FullLoader)
   
s = config['timelapse']['image-range']['start']
e = config['timelapse']['image-range']['end']
g = config['timelapse']['frame-granularity']
t = config['timelapse']['download-threads']

x = config['place-canvas']['top-left-coordinates']['x']
y = config['place-canvas']['top-left-coordinates']['y']
dx = config['place-canvas']['dimensions']['width']
dy = config['place-canvas']['dimensions']['height']

intensity = config['heatmap']['intensity']
decay = config['heatmap']['decay']

n = config['output']['name']
w = config['output']['dimensions']['width']
h = config['output']['dimensions']['height']

ids = scraper.get_image_ids(s, e, g)
scraper.init_fetch_images(ids, t)

heat_gen = HeatmapGenerator(intensity, decay, [[x, y], [x+dx, y+dy]])

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
vid = cv2.VideoWriter(f'{n}.mp4', fourcc, 30.0, (w, h))

for idx in tqdm(range(1, len(ids)), desc='Timelapse creation', ascii=True, leave=False):
    img1, img2 =  get_img_pair(ids, idx)
    img1 = img1.crop((x, y, x + dx, y + dy))
    img2 = img2.crop((x, y, x + dx, y + dy))

    heatmap = heat_gen.generate_heat_map(cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR), cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR))
    cv2.imshow("image", heatmap)
    cv2.waitKey(1)
    heatmap = Image.fromarray(heatmap).resize((w, h), Image.Resampling.NEAREST)
    vid.write(np.array(heatmap))
   
vid.release()
print(f'\nDone, check {n}.mp4')
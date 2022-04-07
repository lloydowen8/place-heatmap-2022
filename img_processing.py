from typing_extensions import Self
import numpy as np
import os
import cv2

class HeatmapGenerator(): 
    def __init__(self, intensity, decay, area): 
        self.intensity = intensity
        self.decay = decay
        self.heatmap = np.zeros((area[1][1]-area[0][1], area[1][0]-area[0][0], 3))

    def generate_heat_map(self, img, img2):

        b, g, r = self.heatmap[..., 0], self.heatmap[..., 1], self.heatmap[..., 2]
        r_mask = (r > 0) & (g == 0.0) & (b == 0.0)
        g_mask =  (g > 0.0) & (b == 0.0)
        b_mask = (b > 0.0)

        # Decay hotspots quicker  
        temp_image = self.heatmap[b_mask]
        temp_image[:, 0] -= self.decay / 255
        self.heatmap[b_mask] = temp_image
        temp_image = self.heatmap[g_mask]
        temp_image[:, 1] -= self.decay / 255
        self.heatmap[g_mask] = temp_image
        temp_image = self.heatmap[r_mask]
        temp_image[:, 2] -= self.decay / 255
        self.heatmap[r_mask] = temp_image

        # Sequential frame colour masks
        # (Detects changes for each pixel between sequential images)
        b_1, g_1, r_1 = img[..., 0], img[..., 1], img[..., 2]
        b_2, g_2, r_2 = img2[..., 0], img2[..., 1], img2[..., 2]
        mask = (b_1 == b_2) & (g_1 == g_2) & (r_1 == r_2)
        mask = ~mask

        b, g, r = self.heatmap[..., 0], self.heatmap[..., 1], self.heatmap[..., 2]
        r_mask = (r < 1.0)
        g_mask = (~r_mask) & (g < 1.0)
        b_mask = (~r_mask) & (~g_mask) & (b < 1.0)

        # If changes detected increase the brightness 
        # (Using "Hot" colour map)
        # Work around for numpy masking issues (probably a faster way of doing this)
        temp_image = self.heatmap[mask & r_mask]
        temp_image[:, 2] += self.intensity / 255
        temp_image[:, 1] += (temp_image[:, 2] - 1).clip(0, 1)
        self.heatmap[mask & r_mask] = temp_image


        temp_image = self.heatmap[mask & g_mask]
        temp_image[:, 1] += self.intensity / 255
        temp_image[:, 0] += (temp_image[:, 1] - 1).clip(0, 1)
        self.heatmap[mask & g_mask] = temp_image


        temp_image = self.heatmap[mask & b_mask]
        temp_image[:, 0] += self.intensity / 255
        self.heatmap[mask & b_mask] = temp_image

        self.heatmap = self.heatmap.clip(0.0, 1.0)

        return (self.heatmap * 255).astype("uint8")
import os
import numpy as np
import torch.nn as nn
import torch
from tqdm import tqdm

class RED_CNN(nn.Module):
    def __init__(self, out_ch=96, norm_range_min=-1024, norm_range_max=3072):
        super(RED_CNN, self).__init__()
        self.norm_range_min = norm_range_min
        self.norm_range_max = norm_range_max
        self.conv1 = nn.Conv2d(1, out_ch, kernel_size=5, stride=1, padding=0)
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=5, stride=1, padding=0)
        self.conv3 = nn.Conv2d(out_ch, out_ch, kernel_size=5, stride=1, padding=0)
        self.conv4 = nn.Conv2d(out_ch, out_ch, kernel_size=5, stride=1, padding=0)
        self.conv5 = nn.Conv2d(out_ch, out_ch, kernel_size=5, stride=1, padding=0)

        self.tconv1 = nn.ConvTranspose2d(out_ch, out_ch, kernel_size=5, stride=1, padding=0)
        self.tconv2 = nn.ConvTranspose2d(out_ch, out_ch, kernel_size=5, stride=1, padding=0)
        self.tconv3 = nn.ConvTranspose2d(out_ch, out_ch, kernel_size=5, stride=1, padding=0)
        self.tconv4 = nn.ConvTranspose2d(out_ch, out_ch, kernel_size=5, stride=1, padding=0)
        self.tconv5 = nn.ConvTranspose2d(out_ch, 1, kernel_size=5, stride=1, padding=0)

        self.relu = nn.ReLU()

    def forward(self, x):
        # encoder
        x = self.normalize(x)
        residual_1 = x
        out = self.relu(self.conv1(x))
        out = self.relu(self.conv2(out))
        residual_2 = out
        out = self.relu(self.conv3(out))
        out = self.relu(self.conv4(out))
        residual_3 = out
        out = self.relu(self.conv5(out))
        # decoder
        out = self.tconv1(out)
        out += residual_3
        out = self.tconv2(self.relu(out))
        out = self.tconv3(self.relu(out))
        out += residual_2
        out = self.tconv4(self.relu(out))
        out = self.tconv5(self.relu(out))
        out += residual_1
        out = self.relu(out)
        out = self.denormalize(out)
        return out

    def normalize(self, image):
        image = (image - self.norm_range_min) / (self.norm_range_max - self.norm_range_min)
        return image

    def denormalize(self, image):
        image = image * (self.norm_range_max - self.norm_range_min) + self.norm_range_min
        return image

    def predict(self, image, batch_size=1, device='cpu'):
        if image.ndim == 2: image = image[None, None, :, :]
        if image.dtype != 'float32': image = image.astype('float32')
        with torch.no_grad():
            n_images = image.shape[0]
            if batch_size > n_images:
                batch_size = n_images
            batch_indices = np.arange(n_images)
            if n_images % batch_size == 0:
                batch_indices = np.split(batch_indices, n_images//batch_size)
                if batch_size == 1: batch_indices = np.array(batch_indices).reshape(-1, 1)
            else:
                modulo=n_images % batch_size
                batch_indices = np.split(batch_indices[:n_images-modulo], n_images//batch_size)
                batch_indices.append(list(range(n_images-modulo, n_images)))
            pred = np.zeros_like(image)
            image = torch.tensor(image, device=device)
            for batch in tqdm(batch_indices):
                pred[batch] = self.forward(image[batch]).to('cpu').numpy()
            return pred

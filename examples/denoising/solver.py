import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import OrderedDict
from skimage.exposure import match_histograms

import torch
import torch.nn as nn
import torch.optim as optim

from prep import printProgressBar
from networks import RED_CNN
from measure import compute_measure

from pathlib import Path

class Solver(object):
    def __init__(self, args, data_loader):
        self.mode = args.mode
        self.load_mode = args.load_mode
        self.data_loader = data_loader

        if args.device:
            self.device = torch.device(args.device)
        else:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.norm_range_min = args.norm_range_min
        self.norm_range_max = args.norm_range_max
        self.trunc_min = args.trunc_min
        self.trunc_max = args.trunc_max

        self.save_path = args.save_path
        self.multi_gpu = args.multi_gpu

        self.num_epochs = args.num_epochs
        self.print_iters = args.print_iters
        self.decay_iters = args.decay_iters
        self.save_iters = args.save_iters
        self.test_iters = args.test_iters
        self.result_fig = args.result_fig

        self.patch_size = args.patch_size

        self.REDCNN = RED_CNN()
        if (self.multi_gpu) and (torch.cuda.device_count() > 1):
            print('Use {} GPUs'.format(torch.cuda.device_count()))
            self.REDCNN = nn.DataParallel(self.REDCNN)
        self.REDCNN.to(self.device)
        print(self.device)

        self.lr = args.lr
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.REDCNN.parameters(), self.lr)

        if args.augment:
            print('Loading noise patches for augmentation...')
            # prep for augmentation
            noise_patch_dir = Path('/home/brandon.nelson/Dev/PediatricCTSizeAugmentation/noise_patches/patch_size_64x64')
            diameters = [112, 131, 151, 185, 216, 292]

            noise_files = [noise_patch_dir / f'diameter{d}mm.npy' for d in diameters]
            noise_patches = 500 # <-- experiment with how many to include (too many to load all 30,000/diameter)
            noise_patch_dict = {f.stem: np.load(f)[:noise_patches].astype('int16') for f in noise_files}
            input_shape = noise_patch_dict['diameter292mm'].shape

            i = 0
            for x, y in self.data_loader:
                i += 1
                if i > 0:
                    break
            train_noise = x - y
            ref_images = train_noise.reshape(-1, 1).numpy()
            equal_hist_patches = {diam: match_histograms(input_images.reshape(-1, 1), reference=ref_images).reshape(input_shape) for diam, input_images in noise_patch_dict.items()}
            equal_hist_patches = {diam: p - p.mean() for diam, p in equal_hist_patches.items()} # remove the DC bias introduced by the histogram matching
            self.noise_patches = torch.tensor(np.concatenate(list(equal_hist_patches.values())).astype('int16'), device=self.device)
            print('noise patch loading complete.')

    def augment(self, image_label, aug_thresh=0.35):
        image, label = image_label
        noise_patch = self.noise_patches[torch.randperm(len(image))].reshape_as(image)
        noise_lambda = 1 # torch.rand([1])[0].item() # adds a random amount of noise, consider ablating to see affect with and without this (seems similar to the noise level augmentation which was generally beneficial whereas having it off would be just augmenting with a single noise level (equal to quarter dose but with different texture))
        add_noise = torch.rand([1])[0].item() < aug_thresh #from 0.5

        if add_noise:
            image = label + noise_lambda*noise_patch
        return image, label

    def save_model(self, iter_):
        f = os.path.join(self.save_path, 'REDCNN_{}iter.ckpt'.format(iter_))
        torch.save(self.REDCNN.state_dict(), f)


    def load_model(self, iter_):
        f = os.path.join(self.save_path, 'REDCNN_{}iter.ckpt'.format(iter_))
        if self.multi_gpu:
            state_d = OrderedDict()
            for k, v in torch.load(f):
                n = k[7:]
                state_d[n] = v
            self.REDCNN.load_state_dict(state_d)
        else:
            self.REDCNN.load_state_dict(torch.load(f))


    def lr_decay(self):
        lr = self.lr * 0.5
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr


    def denormalize_(self, image):
        image = image * (self.norm_range_max - self.norm_range_min) + self.norm_range_min
        return image


    def trunc(self, mat):
        mat[mat <= self.trunc_min] = self.trunc_min
        mat[mat >= self.trunc_max] = self.trunc_max
        return mat


    def save_fig(self, x, y, pred, fig_name, original_result, pred_result):
        x, y, pred = x.numpy(), y.numpy(), pred.numpy()
        f, ax = plt.subplots(1, 3, figsize=(30, 10))
        ax[0].imshow(x, cmap=plt.cm.gray, vmin=self.trunc_min, vmax=self.trunc_max)
        ax[0].set_title('Quarter-dose', fontsize=30)
        ax[0].set_xlabel("PSNR: {:.4f}\nSSIM: {:.4f}\nRMSE: {:.4f}".format(original_result[0],
                                                                           original_result[1],
                                                                           original_result[2]), fontsize=20)
        ax[1].imshow(pred, cmap=plt.cm.gray, vmin=self.trunc_min, vmax=self.trunc_max)
        ax[1].set_title('Result', fontsize=30)
        ax[1].set_xlabel("PSNR: {:.4f}\nSSIM: {:.4f}\nRMSE: {:.4f}".format(pred_result[0],
                                                                           pred_result[1],
                                                                           pred_result[2]), fontsize=20)
        ax[2].imshow(y, cmap=plt.cm.gray, vmin=self.trunc_min, vmax=self.trunc_max)
        ax[2].set_title('Full-dose', fontsize=30)

        f.savefig(os.path.join(self.save_path, 'fig', 'result_{}.png'.format(fig_name)))
        plt.close()


    def train(self, augment=0):
        train_losses = []
        total_iters = 0
        start_time = time.time()
        for epoch in range(1, self.num_epochs):
            self.REDCNN.train(True)

            for iter_, (x, y) in enumerate(self.data_loader):
                total_iters += 1

                # add 1 channel
                x = x.unsqueeze(0).float().to(self.device)
                y = y.unsqueeze(0).float().to(self.device)

                if self.patch_size: # patch training
                    x = x.view(-1, 1, self.patch_size, self.patch_size)
                    y = y.view(-1, 1, self.patch_size, self.patch_size)

                if augment: #conditional likely uneeded if lambda = 0, same effect
                    x, y = self.augment((x, y), augment)

                pred = self.REDCNN(x)
                loss = self.criterion(pred, y)
                self.REDCNN.zero_grad()
                self.optimizer.zero_grad()

                loss.backward()
                self.optimizer.step()
                train_losses.append(loss.item())

                # print
                if total_iters % self.print_iters == 0:
                    print("STEP [{}], EPOCH [{}/{}], ITER [{}/{}] \nLOSS: {:.8f}, TIME: {:.1f}s".format(total_iters, epoch, 
                                                                                                        self.num_epochs, iter_+1, 
                                                                                                        len(self.data_loader), loss.item(), 
                                                                                                        time.time() - start_time))
                # learning rate decay
                if total_iters % self.decay_iters == 0:
                    self.lr_decay()
                # save model
                if total_iters % self.save_iters == 0:
                    self.save_model(total_iters)
                    np.save(os.path.join(self.save_path, 'loss_{}_iter.npy'.format(total_iters)), np.array(train_losses))


    def test(self):
        del self.REDCNN
        # load
        self.REDCNN = RED_CNN().to(self.device)
        self.load_model(self.test_iters)

        # compute PSNR, SSIM, RMSE
        ori_psnr_avg, ori_ssim_avg, ori_rmse_avg = 0, 0, 0
        pred_psnr_avg, pred_ssim_avg, pred_rmse_avg = 0, 0, 0

        with torch.no_grad():
            for i, (x, y) in enumerate(self.data_loader):
                shape_ = x.shape[-1]
                x = x.unsqueeze(0).float().to(self.device)
                y = y.unsqueeze(0).float().to(self.device)

                pred = self.REDCNN(x)

                # denormalize, truncate
                # x = self.trunc(self.denormalize_(x.view(shape_, shape_).cpu().detach()))
                # y = self.trunc(self.denormalize_(y.view(shape_, shape_).cpu().detach()))
                # pred = self.trunc(self.denormalize_(pred.view(shape_, shape_).cpu().detach()))
                x = x.view(shape_, shape_).cpu().detach()
                y = y.view(shape_, shape_).cpu().detach()
                pred = pred.view(shape_, shape_).cpu().detach()

                data_range = self.norm_range_max - self.norm_range_min

                original_result, pred_result = compute_measure(x, y, pred, data_range)
                ori_psnr_avg += original_result[0]
                ori_ssim_avg += original_result[1]
                ori_rmse_avg += original_result[2]
                pred_psnr_avg += pred_result[0]
                pred_ssim_avg += pred_result[1]
                pred_rmse_avg += pred_result[2]

                # save result figure
                if self.result_fig:
                    self.save_fig(x, y, pred, i, original_result, pred_result)

                printProgressBar(i, len(self.data_loader),
                                 prefix="Compute measurements ..",
                                 suffix='Complete', length=25)
            print('\n')
            print('Original === \nPSNR avg: {:.4f} \nSSIM avg: {:.4f} \nRMSE avg: {:.4f}'.format(ori_psnr_avg/len(self.data_loader), 
                                                                                            ori_ssim_avg/len(self.data_loader), 
                                                                                            ori_rmse_avg/len(self.data_loader)))
            print('\n')
            print('Predictions === \nPSNR avg: {:.4f} \nSSIM avg: {:.4f} \nRMSE avg: {:.4f}'.format(pred_psnr_avg/len(self.data_loader), 
                                                                                                  pred_ssim_avg/len(self.data_loader), 
                                                                                                  pred_rmse_avg/len(self.data_loader)))

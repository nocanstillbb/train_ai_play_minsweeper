import cv2
import json
import math
import numpy as np
import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.utils.data import DataLoader, TensorDataset

class GridCNN(nn.Module):
    def __init__(self):
        super(GridCNN, self).__init__()

        # 共享的特征提取网络
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)

        # 提取16×30的局部特征
        self.pool = nn.AdaptiveAvgPool2d((16, 30))  # (N, 64, 16, 30)


        # 分类层
        self.fc1 = nn.Linear(64, 32)
        self.fc2 = nn.Linear(32, 14)

    def forward(self, x):
        # 共享特征提取
        x = F.relu(self.conv1(x))  # (N, 32, 256, 480)
        x = F.relu(self.conv2(x))  # (N, 64, 256, 480)

        # 全局池化缩小至16x30网格大小
        x = self.pool(x)  # (N, 64, 16, 30)


        # 变换维度，准备全连接层
        x = x.permute(0, 2, 3, 1)  # (N, 16, 30, 64)

        # 全连接层
        x = F.relu(self.fc1(x))  # (N, 16, 30, 32)
        x = self.fc2(x)  # (N, 16, 30, 14)

        return x



#class MinesweeperSubAreaNet(nn.Module):
#    def __init__(self):
#        super(MinesweeperSubAreaNet, self).__init__()
#        
#        # 局部卷积层
#        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)   # (batch, 32, 256, 480)
#        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)  # (batch, 64, 256, 480)
#        # 残缺网络
#        self.res_conv_x_1 = nn.Conv2d(3, 32, kernel_size=1, stride=1) 
#        self.res_conv_x_2 = nn.Conv2d(3, 64, kernel_size=1, stride=1) 
#        
#        # 全局池化（可以换成其他方式）
#        self.avgPool = nn.AdaptiveAvgPool2d((16, 30))  # (batch, 64, 16, 30)
#        #self.maxPool = nn.AdaptiveMaxPool2d((16, 30))  # (batch, 64, 16, 30)
#
#        # 全连接层
#        self.fc1 = nn.Linear(64, 128)  # (batch, 16, 30, 128)
#        self.fc2 = nn.Linear(128, 14)  # (batch, 16, 30, 14)
#
#
#    def forward(self, x):
#        # 输入: x -> (batch, 3, 256, 480)
#        x_1_res = self.res_conv_x_1(x)
#        x_2_res = self.res_conv_x_2(x)
#
#        x = F.relu(self.conv1(x)) + x_1_res # (batch, 32, 256, 480)
#        x = F.relu(self.conv2(x)) + x_2_res  # (batch, 64, 256, 480)
#
#        # 进行区域池化，把图像缩小到 (16, 30)
#        x = self.avgPool(x) 
#
#        # 维度变换 (batch, 16, 30, 64)
#        x = x.permute(0, 2, 3, 1)  # 交换维度 (batch, 16, 30, 64)
#
#        # 全连接层
#        x = F.relu(self.fc1(x))  # (batch, 16, 30, 128)
#        x = self.fc2(x)          # (batch, 16, 30, 14)
#
#        return x

#class MinesweeperSubAreaNet(nn.Module):
#    def __init__(self):
#        super(MinesweeperSubAreaNet, self).__init__()
#        
#        # 局部卷积层
#        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)   # (batch, 32, 256, 480)
#        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)  # (batch, 64, 256, 480)
#        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)  # (batch, 128, 256, 480)
#        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)  # (batch, 128, 256, 480)
#        self.conv5 = nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1)  # (batch, 128, 256, 480)
#        
#        self.pool = nn.AdaptiveMaxPool2d((16, 30))  # (batch, 512, 16, 30)
#        #self.pool = nn.AdaptiveAvgPool2d((16, 30))  # (batch, 512, 16, 30)
#
#        # 全连接层
#        self.fc1 = nn.Linear(512, 256)  # (batch, 16, 30, 256)
#        self.fc2 = nn.Linear(256, 128)  # (batch, 16, 30, 128)
#        self.fc3 = nn.Linear(128, 64)  # (batch, 16, 30, 64)
#        self.fc4 = nn.Linear(64, 32)  # (batch, 16, 30, 14)
#        self.fc5 = nn.Linear(32, 14)  # (batch, 16, 30, 14)
#
#    def forward(self, x):
#        # 输入: x -> (batch, 3, 256, 480)
#        x = F.relu(self.conv1(x))  # (batch, 32, 256, 480)
#        x = F.relu(self.conv2(x))  # (batch, 64, 256, 480)
#        x = F.relu(self.conv3(x))  # (batch, 128, 256, 480)
#        x = F.relu(self.conv4(x))  # (batch, 256, 256, 480)
#        x = F.relu(self.conv5(x))  # (batch, 512, 256, 480)
#
#        # 进行区域池化，把图像缩小到 (16, 30)
#        x = self.pool(x)  # (batch, 512, 16, 30)
#
#        # 维度变换 (batch, 16, 30, 64)
#        x = x.permute(0, 2, 3, 1)  # 交换维度 (batch, 16, 30, 512)
#
#        # 全连接层
#        x = F.relu(self.fc1(x))  # (batch, 16, 30, 256)
#        x = F.relu(self.fc2(x))  # (batch, 16, 30, 128)
#        x = F.relu(self.fc3(x))  # (batch, 16, 30, 64)
#        x = F.relu(self.fc4(x))  # (batch, 16, 30, 32)
#        x = self.fc5(x)          # (batch, 16, 30, 14)
#
#        return x

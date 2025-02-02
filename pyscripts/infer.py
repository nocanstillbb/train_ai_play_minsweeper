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
import mines_model as MM

from torch.utils.data import DataLoader, TensorDataset

# 定义超参数
batch_size = 1
num_epochs = 1
learning_rate = 0.001
data_dir = "/Users/hbb/source/repos/train_ai_play_minsweeper/build/data_collector/data_val"
#data_dir = "/Users/hbb/source/repos/train_ai_play_minsweeper/build/data_collector/data"



def letterbox_image(image, target_size=(256, 480)):
    ##打印调试
    #np.set_printoptions(threshold=sys.maxsize)
    """Resize and pad image to target size while maintaining aspect ratio."""
    height, width = image.shape[:2]
    scale = min(target_size[1] / width, target_size[0] / height)
    new_width, new_height = int(width * scale), int(height * scale)
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    # Create a padded image
    pad_width = target_size[1] - new_width
    pad_height = target_size[0] - new_height
    padded_image = cv2.copyMakeBorder(
        resized_image, 
        0, pad_height, 
        0, pad_width, 
        borderType=cv2.BORDER_CONSTANT, 
        value=(0, 0, 0)
    )
    return padded_image

def json_to_tensor(json_path):

    #打印调试
    #np.set_printoptions(threshold=sys.maxsize)

    """Convert JSON label to a (16, 30, 10) tensor."""
    #print("Loading JSON data...")
    with open(json_path, 'r') as f:
        label_data = json.load(f)

    # Convert the "minsRows" data to a numpy array
    mins_rows = np.array(label_data["minsRows"], dtype=np.int8)

    #打印调试
    #print("Input mins layout:")
    #print(mins_rows)

    # Ensure mins_rows is a 2D array
    if mins_rows.ndim != 2:
        raise ValueError("Expected a 2D array for 'minsRows', got shape: {}".format(mins_rows.shape))

    # Convert to one-hot encoding (-1 maps to index 0, 0 maps to index 1, ..., 9 maps to index 10)
    mins_rows += 1
    one_hot_labels = np.eye(14, dtype=np.int8)[mins_rows]

    # Print shape for verification
    #print("Generated tensor shape:", one_hot_labels.shape)

    #打印调试
    #print(one_hot_labels)

    #return one_hot_labels
    return mins_rows



files = []

def load_data(data_dir):
    """Load images and labels, convert to PyTorch tensors."""
    image_tensors = []
    label_tensors = []
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".jpg"):
            files.append(filename)
            # Load and preprocess the image
            image_path = os.path.join(data_dir, filename)
            image = cv2.imread(image_path)
            if image is None:
                continue  # Skip if image could not be loaded
            image = letterbox_image(image)
            letterbox_path = image_path.replace(".jpg", "_letterbox_.jpg")
            ##打印调试
            #cv2.imwrite(letterbox_path,image)

            image = np.transpose(image, (2, 0, 1))  # Convert to CHW format
            image_tensors.append(torch.tensor(image, dtype=torch.float32) / 255.0)  # Normalize to [0, 1]
            
            # Load and preprocess the label
            #print("image path : {}".format(image_path))
            label_path = image_path.replace(".jpg", ".label_status")
            #print("label path : {}".format(label_path))
            if not os.path.exists(label_path):
                continue
            label_tensor = json_to_tensor(label_path)
            label_tensors.append(torch.tensor(label_tensor, dtype=torch.float32))

    
    return torch.stack(image_tensors), torch.stack(label_tensors)

# Example usage
image_tensors, label_tensors = load_data(data_dir)

device = torch.device("mps")
image_tensors = image_tensors.to(device)
label_tensors = label_tensors.to(device)

print(f"Image tensors shape: {image_tensors.shape}")  # Should be (N, 3, 256, 480)
print(f"Label tensors shape: {label_tensors.shape}")  # Should be (N, 16, 30, 10)
print(f"Image tensor type: {image_tensors.dtype}, device: {image_tensors.device}")
print(f"Label tensor type: {label_tensors.dtype}, device: {label_tensors.device}")


# 初始化模型
model = MM.GridCNN()

if len(sys.argv) > 1:  # 判断是否有传入参数
    path = sys.argv[1]  # 获取第一个参数
    abs_path = os.path.abspath(path)  # 转换为绝对路径
    print(f"输入参数路径: {abs_path}")
    model.load_state_dict(torch.load(abs_path))
    #model.load_state_dict(torch.load(PATH,map_location=device)) #如果保存时的device和想要加载到的device不同,则需要指定map_localtion
    #model.to(device=device)

model.to(device)
model.eval()#切换到推理模式

torch.set_printoptions(linewidth=2000)

with torch.no_grad():
    for i in range(len(image_tensors)):
        print("==============================================================")
        val_outputs = model(image_tensors[i].unsqueeze(0)) #升维

        #print("output:{}".format(val_outputs.shape))
        val_outputs = val_outputs.argmax(dim=-1)  #从独热编码转换为枚举值二维矩阵
        #print("output:{}".format(val_outputs.shape))

        #print("output:{}".format(val_outputs -1))
        #print("lable :{}".format((label_tensors[i] -1).long()))
        result = torch.all(val_outputs == label_tensors[i])
        print("{} result:{}".format(files[i],result))
        
        if  result == False :
            sys.exit(-1)






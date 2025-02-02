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
batch_size = 32 
num_epochs = 1000
learning_rate_0 = 0.0001
learning_rate_1 = 0.0001
data_dir = "/Users/hbb/source/repos/train_ai_play_minsweeper/build/data_collector/data_train"





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

def load_data(data_dir):
    """Load images and labels, convert to PyTorch tensors."""
    image_tensors = []
    label_tensors = []
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".jpg"):
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




# 创建数据集和数据加载器
dataset = TensorDataset(image_tensors, label_tensors)
train_size = int(0.8 * len(dataset))  # 80% 训练集
val_size = len(dataset) - train_size  # 20% 验证集
train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)




# 初始化模型
model = MM.GridCNN()

if len(sys.argv) > 1:  # 判断是否有传入参数
    path = sys.argv[1]  # 获取第一个参数
    abs_path = os.path.abspath(path)  # 转换为绝对路径
    print(f"输入参数路径: {abs_path}")
    model.load_state_dict(torch.load(abs_path))
    #model.load_state_dict(torch.load(PATH,map_location=device)) #如果保存时的device和想要加载到的device不同,则需要指定map_localtion
    #model.to(device=device)
    #model.eval()#切换到推理模式

model.to(device)

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()  # 交叉熵损失
#optimizer = optim.SGD(model.parameters(), lr=learning_rate_0)
optimizer = optim.Adam(model.parameters(), lr=learning_rate_0)

lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer,T_max=num_epochs,eta_min=learning_rate_1) 

# 打印模型架构
print(model)
for name, param in model.named_parameters():
    print(f"Parameter {name} is on device: {param.device}")

# 训练和验证循环
for epoch in range(num_epochs):
    # 训练模式
    model.train()
    total_loss = 0
    batch_count = 0

    for batch_images, batch_labels in train_loader:
        batch_count +=1
        #print(f"batch start ==============================================================")
        #print("batch_images shape {}".format(batch_images.shape))
        #print("batch_labels shape {}".format(batch_labels.shape))
        #print(f"batch_images device: {batch_images.device}")
        #print(f"batch_labels device: {batch_labels.device}")
        batch_labels = batch_labels.long()
        #print(f"batch_labels tensors shape: {batch_labels.shape}")  # Should be (N, 3, 256, 480)
        #print(f"batch_labels tensor type: {batch_labels.dtype}, device: {batch_labels.device}")

        outputs = model(batch_images)
        #print(f"outputs tensors shape: {outputs.shape}")  # Should be (N, 3, 256, 480)
        #print(f"outputs tensor type: {outputs.dtype}, device: {outputs.device}")

        #print(f"after reshape==============================================================")

        batch_labels = batch_labels.view(-1)  # (batch_size * 16 * 30)
        #print(f"batch_labels tensors shape: {batch_labels.shape}")  # Should be (N, 3, 256, 480)
        #print(f"batch_labels tensor type: {batch_labels.dtype}, device: {batch_labels.device}")

        outputs = outputs.view(-1, 14)  # (batch_size * 16 * 30, 14)
        #print(f"outputs tensors shape: {outputs.shape}")  # Should be (N, 3, 256, 480)
        #print(f"outputs tensor type: {outputs.dtype}, device: {outputs.device}")

        loss = criterion(outputs, batch_labels)

        # 反向传播和优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
    print(f"Epoch [{epoch+1}/{num_epochs}],  Training Loss: {total_loss / len(train_loader):.10f}")
    lr_scheduler.step()


    # 验证模式
    model.eval()
    val_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for val_images, val_labels in val_loader:
            val_labels = val_labels.long()

            # 前向传播
            val_outputs = model(val_images)
            val_outputs = val_outputs.view(-1, 14)
            val_labels = val_labels.view(-1)

            loss = criterion(val_outputs, val_labels)
            val_loss += loss.item()

            # 计算准确率
            _, predicted = torch.max(val_outputs, 1)  # 获取预测类别
            correct += (predicted == val_labels).sum().item()
            total += val_labels.size(0)

    print(f"Validation Loss: {val_loss / len(val_loader):.4f}, Accuracy: {100 * correct / total:.6f}%")

    torch.save(model.state_dict(),f"epo{epoch}_acc{correct / total:.4f}model.pt")



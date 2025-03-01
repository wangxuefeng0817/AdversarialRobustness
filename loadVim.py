import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from PIL import Image
import requests
from matplotlib import pyplot as plt
from torchvision import datasets
from transformers import ViTImageProcessor, ViTForImageClassification
import sys

from timm.data.constants import IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD

import models_mamba as vm


# Create wrapper object of model so inference output stored in logits attribute
class SimpleNamespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
class VimWrapper(nn.Module):
    def __init__(self, vim_model, config):
        super(VimWrapper, self).__init__()
        self.vim_model = vim_model
        self.config = SimpleNamespace(id2label=config.id2label, label2id=config.label2id)
    
    def forward(self, x):
        # Use the original model to compute the output
        output = self.vim_model(x)
        # Return output in a form that includes a `.logits` attribute
        return SimpleNamespace(logits=output)

def loadVim():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    sys.path.insert(0, '/home/jupyter/AdversarialRobustness')
    sys.path.insert(0, '/home/jupyter/AdversarialRobustness/vim')
    
    # Does the same preprocessing
    processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")

    # Use ViT for config, as Vim doesn't contain metadata
    confproxymod = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")
    
    # Load Model and prepare processor (taken from ViT)
    checkpoint = torch.load("/home/jupyter/AdversarialRobustness/vim_s_midclstok_ft_81p6acc.pth")
    model = vm.vim_small_patch16_stride8_224_bimambav2_final_pool_mean_abs_pos_embed_with_midclstok_div2()
    model.load_state_dict(checkpoint["model"])
    model.to(device)
    model.eval()
    torch.no_grad()
    
    # Wrap model
    model = VimWrapper(model, confproxymod.config)
    
    return model, processor
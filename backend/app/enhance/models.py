import os
from pathlib import Path
from typing import Any, Optional
import numpy as np

# Safe optional torch loader
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
    _BaseModule: Any = nn.Module
except ImportError:
    TORCH_AVAILABLE = False
    torch: Any = None
    nn: Any = None
    _BaseModule: Any = object


class SimpleGate(_BaseModule):
    def forward(self, x: Any) -> Any:
        x1, x2 = x.chunk(2, dim=1)
        return x1 * x2


class NAFBlock(_BaseModule):
    def __init__(self, c: int, DW_Expand: int = 2, FFN_Expand: int = 2, drop_out_rate: float = 0.0):
        super().__init__()
        dw_channel = c * DW_Expand
        self.conv1 = nn.Conv2d(c, dw_channel, 1, padding=0, stride=1, groups=1, bias=True)
        self.conv2 = nn.Conv2d(dw_channel, dw_channel, 3, padding=1, stride=1, groups=dw_channel, bias=True)
        self.conv3 = nn.Conv2d(dw_channel // 2, c, 1, padding=0, stride=1, groups=1, bias=True)
        self.sg = SimpleGate()

        # Simplified Channel Attention
        self.sca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(dw_channel // 2, dw_channel // 2, 1, padding=0, stride=1, groups=1, bias=True),
        )

        ffn_channel = FFN_Expand * c
        self.conv4 = nn.Conv2d(c, ffn_channel, 1, padding=0, stride=1, groups=1, bias=True)
        self.conv5 = nn.Conv2d(ffn_channel // 2, c, 1, padding=0, stride=1, groups=1, bias=True)

        self.norm1 = nn.GroupNorm(1, c)
        self.norm2 = nn.GroupNorm(1, c)
        self.beta = nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)
        self.gamma = nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)

    def forward(self, inp):
        x = inp
        x = self.norm1(x)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.sg(x)
        x = x * self.sca(x)
        x = self.conv3(x)
        y = inp + x * self.beta

        x = self.norm2(y)
        x = self.conv4(x)
        x = self.sg(x)
        x = self.conv5(x)
        return y + x * self.gamma


class NAFNet(_BaseModule):
    """
    Nonlinear Activation Free Network (NAFNet) architecture.
    State-of-the-art computational efficiency for image deblurring and denoising.
    """

    def __init__(self, img_channel: int = 3, width: int = 32, middle_blk_num: int = 4, enc_blk_nums=[2, 2, 4], dec_blk_nums=[2, 2, 2]):
        super().__init__()
        self.intro = nn.Conv2d(img_channel, width, 3, padding=1, stride=1, groups=1, bias=True)
        self.ending = nn.Conv2d(width, img_channel, 3, padding=1, stride=1, groups=1, bias=True)

        self.encoders = nn.ModuleList()
        self.downs = nn.ModuleList()
        chan = width
        for num in enc_blk_nums:
            self.encoders.append(nn.Sequential(*[NAFBlock(chan) for _ in range(num)]))
            self.downs.append(nn.Conv2d(chan, 2 * chan, 2, 2))
            chan = chan * 2

        self.middle_blks = nn.Sequential(*[NAFBlock(chan) for _ in range(middle_blk_num)])

        self.decoders = nn.ModuleList()
        self.ups = nn.ModuleList()
        for num in dec_blk_nums:
            self.ups.append(nn.Sequential(nn.Conv2d(chan, chan * 2, 1, bias=False), nn.PixelShuffle(2)))
            chan = chan // 2
            self.decoders.append(nn.Sequential(*[NAFBlock(chan) for _ in range(num)]))

        self.padder_size = 2 ** len(enc_blk_nums)

    def forward(self, inp):
        B, C, H, W = inp.shape
        x = self.intro(inp)
        encs = []
        for encoder, down in zip(self.encoders, self.downs):
            x = encoder(x)
            encs.append(x)
            x = down(x)

        x = self.middle_blks(x)

        for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x)
            x = x + enc_skip
            x = decoder(x)

        x = self.ending(x)
        return x + inp


class SRVGGNetCompact(_BaseModule):
    """
    Compact VGG-style deep neural network for Real-ESRGAN super-resolution and blind deblurring.
    Uses 32 intermediate convolutional layers with PReLU activations and PixelShuffle upsampling.
    """

    def __init__(self, num_in_ch: int = 3, num_out_ch: int = 3, num_feat: int = 64, num_conv: int = 32, upscale: int = 4):
        super().__init__()
        self.upscale = upscale
        self.body = nn.ModuleList()
        self.body.append(nn.Conv2d(num_in_ch, num_feat, 3, 1, 1))
        self.body.append(nn.PReLU(num_parameters=num_feat))
        for _ in range(num_conv):
            self.body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1))
            self.body.append(nn.PReLU(num_parameters=num_feat))
        self.body.append(nn.Conv2d(num_feat, num_out_ch * upscale * upscale, 3, 1, 1))
        self.upsampler = nn.PixelShuffle(upscale)

    def forward(self, x: Any) -> Any:
        import torch.nn.functional as F
        out = x
        for i in range(len(self.body)):
            out = self.body[i](out)
        out = self.upsampler(out)
        base = F.interpolate(x, scale_factor=self.upscale, mode='nearest')
        return out + base


def load_deep_model(weights_path: Path, model_type: str, device: str = "cpu"):
    """
    Safely loads PyTorch deep model weights if PyTorch is installed and file exists.
    Supports Real-ESRGAN neural super-resolution and NAFNet restoration.
    Returns None on failure to trigger seamless classical fallback.
    """
    if not TORCH_AVAILABLE or not weights_path.is_file():
        return None

    try:
        dev = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
        if model_type in ("nafnet_denoise", "nafnet_deblur"):
            model = NAFNet(img_channel=3, width=32, middle_blk_num=4)
            ckpt = torch.load(weights_path, map_location=dev, weights_only=True)
            state_dict = ckpt.get("params", ckpt)
            model.load_state_dict(state_dict, strict=False)
            model.to(dev)
            model.eval()
            return model
        elif model_type in ("realesrgan", "realesrgan_x4", "realesr_compact"):
            model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4)
            ckpt = torch.load(weights_path, map_location=dev, weights_only=True)
            state_dict = ckpt.get("params", ckpt)
            model.load_state_dict(state_dict, strict=True)
            model.to(dev)
            model.eval()
            return model
    except Exception as e:
        return None
    return None

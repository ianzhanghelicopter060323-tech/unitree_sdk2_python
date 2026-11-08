from pathlib import Path

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient


# 网关指定
ChannelFactoryInitialize(0, "eth0")
camera = VideoClient()
camera.SetTimeout(3.0) # 等待3s没有就是timeout
camera.Init()


# 请求1帧图像
code, data = camera.GetImageSample()
if code == 0 and data :
    path = Path("/home/ianzhang/unitree_sdk2_python/ian_test/output/GO2_photo_origin.jpg")
    path.write_bytes(bytes(data))
    print(f"图像采集成功，保存在{path}, 返回码{code}")
else :
    print(f"未收到图像，SDK 返回码为 {code}")
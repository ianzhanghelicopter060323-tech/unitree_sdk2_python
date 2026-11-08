import argparse
from datetime import datetime
from pathlib import Path

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient


def main():
    parser = argparse.ArgumentParser(description="从 Go2 前置摄像头拍一张照片")
    parser.add_argument("interface", nargs="?", default="eth0", help="连接 Go2 的网卡")
    args = parser.parse_args()

    ChannelFactoryInitialize(0, args.interface)
    camera = VideoClient()
    camera.SetTimeout(3.0)
    camera.Init()

    code, data = camera.GetImageSample()
    if code != 0 or not data:
        print(f"未收到图像，SDK 返回码为 {code}")
        return 1

    path = Path(datetime.now().strftime("go2_%Y%m%d_%H%M%S_%f.jpg"))
    path.write_bytes(bytes(data))
    print(f"照片已保存到 {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

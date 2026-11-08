from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
import unitree_sdk2py.go2.sport.sport_api
from unitree_sdk2py.go2.sport.sport_client import SportClient

import argparse


def main() -> int :
    parser = argparse.ArgumentParser(description="发送GO2站立指令")
    parser.add_argument("interface", nargs="?", default="eth0", help="连接 Go2 的网卡")
    args = parser.parse_args()

    ChannelFactoryInitialize(0, args.interface)
    sports = SportClient()
    sports.SetTimeout(3.0)
    sports.Init()

    code = sports.StandUp()
    if code == 0 :
        print(f"站立成功，返回码{code}")
        return 0
    else :
        print(f"站立失败，返回码{code}")
        return 1

if __name__ == "__main__" :
    raise SystemExit(main())
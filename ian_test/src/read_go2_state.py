"""通过有线网卡读取 Go2 的五帧状态。"""
import argparse
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_


def main():
    # 创建一个解析器，读取后面输入的参数
    # description=__doc__ 把文件开头的三引号内的注释作为帮助信息
    # 意思就是运行python3 脚本.py --help后会打印在终端中的信息
    # 但不调用parser，--help不会有任何用
    parser = argparse.ArgumentParser(description=__doc__)
    
    # 选取网卡，定义网卡参数
    # "interface" 意思是可以在脚本运行时直接写eth0，指定网卡名
    # default：默认是eth0网卡
    # help：在运行 --help时出现提示
    parser.add_argument("interface", nargs="?", default="eth0", help="连接 Go2 的网卡，默认 eth0")
    args = parser.parse_args() # 读取命令行，解析后把结果保存在args

    # 初始化DDS通信
    # 这里的 args.interface 的意思是取出在command line里指定的网卡名
    ChannelFactoryInitialize(0, args.interface)


    # 订阅哪个话题： rt/lowstate是话题名， LowState_是消息类型
    sub = ChannelSubscriber("rt/lowstate", LowState_)
    sub.Init()
    print(f"正在通过 {args.interface} 等待 Go2 状态……", flush=True)
    ticks = []
    try:
        for index in range(50): # 采样5次
            state = sub.Read(5) # 最多等待5s,有消息就返回，不需要一定5s

            # 输出看state类型
            print(f"state type={type(state)}")
            # print(f"state={state}")

            if state is None:
                print("等待 5 秒未收到状态帧，请检查网卡和 DDS 连接。")
                return 1
            ticks.append(state.tick)
            roll, pitch, yaw = state.imu_state.rpy 
            print(f"样本 {index + 1}  tick={state.tick}  "
                  f"横滚={roll:.3f}  俯仰={pitch:.3f}  偏航={yaw:.3f} rad", flush=True)
            if index < 4:
                time.sleep(0.5)
    finally:
        sub.Close() # 关闭订阅

    # 只要有一对出现“后一个小于或等于前一个”，程序就提示你检查。
    # 五次都递增，说明这次短实验里读到了持续更新的状态。
    # any()函数逐项检查 b <= a 是否为为True
    if any(b <= a for a, b in zip(ticks, ticks[1:])):
        print("已收到五帧，但 tick 未持续递增。")
        return 1
    print("通过：收到五帧，tick 持续递增。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main()) # SystemExit会依据main返回的退出码执行(1 正常运行， 0 报错了)

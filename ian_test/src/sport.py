import argparse
import math
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_


def looks_like_standing(state):
    # 平地实验用的经验阈值；四个 calf 电机依次对应右前、左前、右后、左后。
    roll, pitch, _ = state.imu_state.rpy
    return (
        abs(roll) <= math.radians(12)
        and abs(pitch) <= math.radians(12)
        and math.hypot(*state.imu_state.gyroscope) <= 0.25
        and all(
            -1.95 <= state.motor_state[i].q <= -0.65
            and abs(state.motor_state[i].dq) <= 0.3
            for i in (2, 5, 8, 11)
        )
    )


def observe_stance(sub):
    deadline = time.monotonic() + 10
    stable_since = None
    previous_tick = None
    last_seen = 0.0
    while time.monotonic() < deadline:
        state = sub.Read(0.25)
        now = time.monotonic()
        if state is None:
            stable_since = None
            continue
        if now - last_seen > 0.25 or (previous_tick is not None and state.tick <= previous_tick):
            stable_since = None
        last_seen, previous_tick = now, state.tick
        if not looks_like_standing(state):
            stable_since = None
            continue
        if stable_since is None:
            stable_since = now
        elif now - stable_since >= 1.0:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="发送一次 Go2 起立指令并观察姿态")
    parser.add_argument("interface", nargs="?", default="eth0", help="连接 Go2 的网卡")
    args = parser.parse_args()

    ChannelFactoryInitialize(0, args.interface)
    sports = SportClient()
    sports.SetTimeout(3.0)
    sports.Init()
    code = sports.StandUp()
    if code != 0:
        print(f"起立请求未获成功确认，返回码 {code}。请观察机器人状态。")
        return 1

    print("起立请求返回成功，正在读取 rt/lowstate……", flush=True)
    sub = ChannelSubscriber("rt/lowstate", LowState_)
    sub.Init()
    try:
        if observe_stance(sub):
            print("连续 1 秒符合平地静止站姿特征。请目视确认四足支撑。")
            return 0
        print("10 秒内未确认静止站姿。请检查实际姿态、反馈数据和阈值。")
        return 2
    finally:
        sub.Close()


if __name__ == "__main__":
    raise SystemExit(main())

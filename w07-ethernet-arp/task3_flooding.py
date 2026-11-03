#!/usr/bin/env python3
"""Week 7 · Task 3 — A switch that runs out of room.

Textbook §6.4.3.

A switch does not have room for every station on the network. Its forwarding
table sits in a fixed amount of fast memory, and when that fills, something has
to go. Whatever goes gets **flooded** the next time anyone sends to it - out of
every port, to every station that did not ask for it.

`NaiveSwitch` handles a full table the simplest way: throw out whichever entry
has been there longest. That is a perfectly reasonable first idea and it is
close to the worst thing you can do with this traffic.

    python3 bench.py
    python3 bench.py --yours

Correctness first: every frame whose destination is reachable must still reach
it. A switch that floods less because it delivers less is not a switch.
"""
from collections import OrderedDict


class NaiveSwitch:
    """Correct. Evicts the oldest entry, which is not the least useful one."""

    BROADCAST = "ff:ff:ff:ff:ff:ff"

    def __init__(self, ports, capacity):
        self.ports = ports
        self.capacity = capacity
        self.table = OrderedDict()                 # mac -> port, insertion order

    def handle(self, frame, in_port):
        src, dst, now = frame
        if src not in self.table and len(self.table) >= self.capacity:
            self.table.popitem(last=False)         # throw out the oldest arrival
        self.table[src] = in_port

        if dst == self.BROADCAST or dst not in self.table:
            return [p for p in range(self.ports) if p != in_port]
        out = self.table[dst]
        return [] if out == in_port else [out]


class YourSwitch:
    """LFU 기반의 학습 스위치 (Admission Control 적용)"""
    BROADCAST = "ff:ff:ff:ff:ff:ff"

    def __init__(self, ports, capacity):
        self.ports = ports
        self.capacity = capacity
        self.table = {}  # mac -> port (포워딩 테이블)
        self.freq = {}   # mac -> 통신 횟수 (Eviction 정책을 위한 Evidence)

    def handle(self, frame, in_port):
        src, dst, _ = frame

        # 1. 출발지 MAC 학습 및 갱신
        if src in self.table:
            self.table[src] = in_port
            self.freq[src] += 1
        else:
            if len(self.table) < self.capacity:
                self.table[src] = in_port
                self.freq[src] = 1
            else:
                # 테이블이 꽉 찼을 때 LFU(가장 적게 통신한 항목) 탐색
                lfu_mac = min(self.freq, key=self.freq.get)

                # [핵심] 테이블의 최소 통신 횟수가 1인 경우에만 쫓아냄
                if self.freq[lfu_mac] == 1:
                    del self.table[lfu_mac]
                    del self.freq[lfu_mac]
                    self.table[src] = in_port
                    self.freq[src] = 1

        # 2. 목적지가 브로드캐스트거나 모르는 곳이면 플러딩
        if dst == self.BROADCAST or dst not in self.table:
            return [p for p in range(self.ports) if p != in_port]

        # 3. 목적지를 아는 경우 횟수 증가 후 해당 포트로만 전송
        self.freq[dst] += 1
        out = self.table[dst]
        return [] if out == in_port else [out]

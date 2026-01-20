import argparse
import asyncio
import time
from asyncua import Client

DEFAULT_ENDPOINT = "opc.tcp://keun90:48010"

DEFAULT_NODES = {
    "status": "ns=7;s=Factory.LINE1.EQP1.Status",
    "temp": "ns=7;s=Factory.LINE1.EQP1.Temperature",
    "seq": "ns=7;s=Factory.LINE1.EQP1.Seq",
    "raw": "ns=7;s=Factory.LINE1.EQP1.RawMessage",
    # DateTime은 서버 구현/클라이언트 변환 차이로 테스트가 꼬일 수 있어 옵션으로 둠
    # "last": "ns=7;s=Factory.LINE1.EQP1.LastUpdate",
}

class SubHandler:
    def __init__(self, report_sec: int, check_seq: bool):
        self.report_sec = report_sec
        self.check_seq = check_seq
        self.count = 0
        self.err_seq = 0
        self.last_seq = None
        self.t0 = time.time()
        self.last_report = self.t0

    def datachange_notification(self, node, val, data):
        # data: DataValue (server timestamp 등 포함)
        self.count += 1

        # Seq 품질 체크(선택): 역전/중복 정도만 잡음 (과도한 검증 금지)
        if self.check_seq and self.last_seq is not None:
            try:
                # Seq 노드일 때만 검사하고 싶으면 NodeId로 필터링 가능하지만,
                # 오버엔지니어링 방지 위해 "val이 int면 검사"로 단순화
                if isinstance(val, int) and val < self.last_seq:
                    self.err_seq += 1
                if isinstance(val, int):
                    self.last_seq = val
            except Exception:
                pass
        elif self.check_seq and isinstance(val, int) and self.last_seq is None:
            self.last_seq = val

        now = time.time()
        if now - self.last_report >= self.report_sec:
            elapsed = now - self.last_report
            rate = self.count / elapsed
            total_elapsed = int(now - self.t0)
            print(f"[{total_elapsed}s] notif_rate={rate:.1f}/s, count={self.count}, seq_err={self.err_seq}")
            self.count = 0
            self.err_seq = 0
            self.last_report = now

async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    p.add_argument("--pub_ms", type=int, default=250, help="publishing interval ms")
    p.add_argument("--report_sec", type=int, default=10)
    p.add_argument("--check_seq", action="store_true")
    args = p.parse_args()

    async with Client(args.endpoint) as client:
        # subscribe 생성
        handler = SubHandler(report_sec=args.report_sec, check_seq=args.check_seq)
        sub = await client.create_subscription(args.pub_ms, handler)

        # 모니터링할 노드들 추가
        nodes = [client.get_node(nid) for nid in DEFAULT_NODES.values()]
        handles = await sub.subscribe_data_change(nodes)

        print("SUBSCRIBED:", len(handles), "nodes / pub_ms =", args.pub_ms)
        print("Press Ctrl+C to stop")

        # 계속 대기
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())

# Task 1
- Why must a frame never go back out of the port it came in on? Give the concrete thing that breaks if it does
  프레임이 들어온 포트로 다시 나가게 되면 네트워크에 브로드캐스트 스톰(Broadcast Storm)과 무한 루프가 발생하여 대역폭이 완전히 마비됩니다.
- A switch floods when it does not know. A router drops. Why the difference?
  2계층 장비인 스위치는 로컬 네트워크 내부에서 목적지를 직접 찾아야 하므로(Self-learning) 플러딩이 필수적입니다. 반면 3계층 장비인 라우터가 모르는 패킷을 플러딩하면 전 세계 인터넷망에 불필요한 트래픽 폭주를 일으키기 때문에 드롭(Drop)시킵니다.
- Your aging is a timeout. What does the switch lose by using time rather than something more direct, and what would "more direct" even be?
  타임아웃 방식은 기기의 오프라인 상태를 즉각 반영하지 못해 메모리를 낭비하며, 빠른 이동 시 포워딩 오류를 유발합니다. 더 직접적인(more direct) 방식은 하드웨어 단의 물리적 연결 해제(Link-down) 신호를 감지하여 즉시 테이블에서 해당 엔트리를 지우는 것입니다.

# Task 2
- The first entry to come back, and why it had to be that one
  가장 먼저 복구되는 엔트리는 로컬 라우터(기본 게이트웨이)의 MAC 주소입니다. 백그라운드 프로세스들이 외부 인터넷과 통신하기 위해서는 반드시 라우터를 거쳐야 하므로 라우터의 주소를 가장 먼저 찾게 됩니다.
- Why a server on the other side of the world is not in your ARP table
  ARP는 로컬 네트워크(동일 서브넷) 내에서만 동작하는 2계층 프로토콜입니다. 외부 서버로 향하는 패킷은 2계층에서 로컬 라우터의 MAC 주소로 전송되므로, 외부 서버의 실제 MAC 주소는 내 ARP 테이블에 기록될 필요도 없고 기록되지도 않습니다.
- The two destination addresses from B2, and what each one means
  첫 번째는 브로드캐스트 주소(ff:ff:ff:ff:ff:ff)로 특정 IP를 가진 기기를 찾기 위해(ARP Request) 네트워크 전체에 던지는 질문입니다. 두 번째는 특정 기기의 유니캐스트 MAC 주소로, 질문을 받은 당사자가 요청자에게 1:1로 자신의 MAC 주소를 알려주기(ARP Reply) 위해 사용합니다. (참고: 관리자 권한이 없어 캐시를 비우지 못해 기존에 채워진 테이블과 캡처본을 분석했습니다.)

# Task 3
- Your eviction rule, and the evidence you keep to run it
  가장 통신 빈도가 적은 항목을 제거하는 LFU(Least Frequently Used) 정책을 사용했습니다. 이를 위한 증거로 `self.freq` 딕셔너리를 두어 각 기기의 패킷 송수신 횟수를 기록했습니다.
- Whether you decline admissions, and what happened to the numbers when you tried
  새로운 기기의 수용을 거부(Decline)하는 로직을 적용했습니다. 쫓겨날 대상의 통신 횟수가 2회 이상이라면, 새로 들어오려는 기기(잠재적 1회성 통신)를 테이블에 아예 기록하지 않았습니다. 그 결과 Wasted deliveries(플러딩) 수치가 대폭 삭감되었습니다.
- R6: the attack, in your own words, and one thing a switch could do about it
  공격 방법 (MAC Flooding Attack): 공격자가 무작위로 생성한 가짜 MAC 주소를 대량으로 스위치에 보내 한정된 테이블 용량을 고의로 가득 채우는 공격입니다. 스위치가 모든 패킷을 더미 허브처럼 전 포트로 플러딩하게 만들어 타인의 통신을 도청합니다.
  방어책: 포트 보안(Port Security) 기능을 활성화하여 물리적 포트당 학습할 수 있는 MAC 주소의 최대 개수를 제한하거나 인가된 기기만 통신하도록 설정합니다.



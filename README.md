# Hermes on Vultr Seoul VPS

> Vultr 서울 리전의 Ubuntu VPS에 Hermes AI Agent를 설치해 24시간 자동화 전령으로 운영하는 실전 레퍼런스입니다.

Hermes는 정해진 공개정보를 수집하고 서비스를 점검하며, 결과를 채널의 성격에 맞춰 **Telegram·Slack·KakaoTalk 나에게 보내기**로 전달합니다. 이 저장소는 단순 설치 명령 모음이 아니라, 실제 운영에서 필요했던 권한 경계·부분 실패 복구·비밀 분리까지 설명합니다.

```text
[Vultr Seoul VPS]
       |
       +-- Hermes AI Agent
       |     +-- scheduled briefing
       |     +-- public-data jobs
       |     `-- service health check
       |
       +-- approval boundary
       |     +-- routine read-only jobs: allowed
       |     `-- delete / install / pay / send externally: denied or approved
       |
       +-- delivery (public internet, outbound only)
       |     +-- Telegram: short alert
       |     +-- Slack: full archive + thread
       |     `-- KakaoTalk: personal daily digest
       |
       `-- management plane (Tailscale private network ONLY)
             +-- SSH: key-only, public IP drops everything
             `-- Web Dashboard: Tailscale bind + password gate
```

두 개의 면을 절대 섞지 않습니다. **배달면**은 봇 API로 바깥에 말을 걸 뿐 듣는 포트가 없고, **관리면**(SSH·Web Dashboard)은 Tailscale 사설망 안에서만 열립니다. 공인 인터넷에서 이 서버는 닫힌 상자입니다.

## 왜 Vultr 서울 VPS인가

한국에서는 Hostinger 같은 패널 중심 VPS가 더 익숙할 수 있습니다. 이 프로젝트는 다음 이유로 Vultr를 선택했습니다.

- **서울 리전:** 한국 사용자와 가까운 위치에 작은 자동화 서버를 둘 수 있습니다.
- **클라우드식 운영:** 작은 인스턴스로 시작하고 Console·API·CLI·Terraform으로 확장할 수 있습니다.
- **직접 통제:** Ubuntu, SSH, 방화벽, systemd, cron과 Hermes 실행 환경을 투명하게 관리합니다.
- **실험 친화성:** 장기 호스팅 상품보다 작은 서버를 만들고 검증하고 접기 쉬운 구조입니다.

| 기준 | Vultr | Hostinger |
|---|---|---|
| 주된 경험 | 개발자 중심 클라우드 VPS | 관리 패널·원클릭 앱 중심 VPS |
| 한국 사용자 관점 | Seoul 리전 선택 가능 | 공식 VPS 위치에서 가까운 아시아 리전을 선택 |
| 시작 난이도 | Linux·SSH·방화벽을 직접 다룸 | hPanel과 설치 템플릿이 편리함 |
| 자동화 확장 | API·CLI·Terraform·cloud-init | API·앱 카탈로그·AI 관리 기능 |
| 이 프로젝트에 맞는 경우 | 실행 환경을 이해하고 세밀하게 통제 | 빠르게 기성 앱을 띄우고 관리 부담을 줄임 |

가격과 리전은 바뀔 수 있으므로 계약 전 각 서비스의 공식 페이지를 확인하십시오. 이 비교의 목적은 승자를 정하는 것이 아니라 선택 기준을 밝히는 것입니다.

## 채널은 같은 일을 하지 않습니다

한 메시지를 세 군데 복제하지 않습니다.

| 채널 | 역할 | 기본 출력 |
|---|---|---|
| Slack | 서고형 | 본문과 긴 꼬리를 스레드에 보관 |
| Telegram | 경보형 | 지금 볼 핵심만 짧게 전달 |
| KakaoTalk | 생활형 | 일일 요약을 내 채팅방으로 전달 |

각 채널은 자신의 성공 상태를 따로 저장해야 합니다. Slack만 실패했을 때 Telegram 성공분까지 반복 발송하는 알림 폭탄을 막고, KakaoTalk 메시지가 여러 조각 중간에 실패하면 남은 조각부터 재개할 수 있습니다.

## KakaoTalk 연동의 경계

이 예제는 카카오가 제공하는 공식 OAuth와 `나에게 보내기` REST API만 사용합니다.

- 공식 endpoint: `/v2/api/talk/memo/default/send`
- 대상: 로그인한 사용자의 `나와의 채팅방`
- 필요 동의항목: `talk_message`
- Windows 카카오톡 화면 자동화 없음
- 비공식 프로토콜 없음
- 친구·고객 자동발송 없음

## 빠른 시작

### 1. Vultr 서버

1. Vultr에서 **Seoul**, Ubuntu LTS, 필요한 최소 사양을 선택합니다.
2. 비밀번호보다 SSH 키 로그인을 우선합니다.
3. root가 아닌 전용 운영 사용자를 만듭니다.
4. Vultr Firewall과 UFW에서 필요한 포트만 엽니다.
5. 서버 시간과 작업 판정 시간대를 명시적으로 구분합니다. 한국 날짜 판정은 `Asia/Seoul`을 사용합니다.

### 2. 코드와 비밀

```bash
git clone https://github.com/leute43-git/hermes-on-vultr-vps.git
cd hermes-on-vultr-vps
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env`에 쓰는 토큰은 절대 커밋하지 않습니다. 공개 코드는 환경변수 이름과 양식만 제공합니다.

### 3. Hermes

Hermes 자체는 공식 배포처의 설치 절차를 따르십시오. 이 저장소는 Hermes 코드를 재배포하지 않고, 운영 역할 템플릿과 제한 원칙만 제공합니다.

1. 설치 버전과 커밋을 기록합니다.
2. 자동 업데이트를 끄고 검증된 버전을 고정합니다.
3. [`hermes/SOUL.example.md`](hermes/SOUL.example.md)를 개인 환경에 맞게 복사합니다.
4. 정기 작업은 읽기·수집·검사 중심으로 제한합니다.
5. 삭제·결제·설치·외부발송·비밀 접근은 거부하거나 사람 승인을 요구합니다.

### 4. 서비스와 타이머

[`systemd/hermes-health.service`](systemd/hermes-health.service)와 [`systemd/hermes-health.timer`](systemd/hermes-health.timer)는 경로와 사용자를 바꿔 설치하는 예시입니다.

```bash
sudo cp systemd/hermes-health.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-health.timer
systemctl list-timers --all | grep hermes-health
```

## 관리 경계 — Tailscale 사설망

관리 접속(SSH·Web Dashboard)은 공인 인터넷에 열지 않습니다.

1. 서버와 노트북(원하면 휴대폰까지)에 [Tailscale](https://tailscale.com)을 설치해 같은 tailnet에 넣습니다.
2. UFW·Vultr Firewall에서 공인 IP의 SSH를 막고, 관리 접속은 **Tailscale IP(100.x.y.z)로만** 합니다.
3. 관리용 포트(대시보드 등)는 처음부터 Tailscale IP에 bind해 공인망에는 소켓 자체가 없게 합니다.

이렇게 하면 "방화벽이 막아준다"가 아니라 **"공인망에는 문이 없다"**가 됩니다. 잠금 확인은 선언이 아니라 실측으로 합니다: 사설망 접근 성공 · 공인 IP 접근 연결 불가, 두 가지를 모두 확인해야 잠근 것입니다.

## Web Dashboard — 원격 조종석

Hermes에는 브라우저용 관리 화면(`hermes dashboard`)이 내장돼 있습니다. 서버에서 돌리고 노트북 브라우저로 씁니다. 텔레그램이 "말 걸기"라면 대시보드는 "조종석"입니다.

### 인증 게이트 (fail-closed)

비루프백 주소에 bind하면 인증 제공자 없이는 **기동 자체가 거부**됩니다(2026-06 하드닝). 내장 아이디/비밀번호 게이트를 켭니다 — `config.yaml`:

```yaml
dashboard:
  basic_auth:
    username: your-admin-name
    password_hash: scrypt$...   # 아래 명령으로 생성 — 평문을 저장하지 않는다
    secret: BASE64_32_BYTES     # 세션 서명키 — openssl rand -base64 32
```

```bash
cd ~/.hermes/hermes-agent && venv/bin/python -c \
  "from plugins.dashboard_auth.basic import hash_password; print(hash_password('YOUR_PASSWORD'))"
```

### 작은 서버를 위한 빌드 우회

웹 UI는 npm 빌드가 필요한데 1GB VPS에서는 부담입니다. **다른 PC에서 같은 커밋의 소스를 빌드해 산출물만 올리십시오** (서버에 node를 설치하지 않아도 됩니다):

```bash
# 빌드 PC에서 (서버와 같은 커밋의 소스로)
cd hermes-agent/web && npm install && npm run build   # 산출물: ../hermes_cli/web_dist
# 서버로 업로드 후 --skip-build로 서빙
```

### 상주 서비스

[`systemd/hermes-dashboard.service`](systemd/hermes-dashboard.service)는 Tailscale IP에 bind하는 user 서비스 예시입니다.

### 잠금 검증 3점 (배포 후 반드시)

```bash
curl http://TAILSCALE_IP:9119/api/status     # 사설망: 200 + 버전 JSON
curl http://TAILSCALE_IP:9119/api/config     # 무인증: 401 이어야 함
curl -m 5 http://PUBLIC_IP:9119/api/status   # 공인망: 연결 자체가 안 되어야 함
```

### Hermes Desktop을 원격 백엔드로 (선택)

데스크톱 앱은 Settings → Gateway → Remote gateway에 같은 주소·계정을 넣으면 이 대시보드에 붙습니다 — 웹과 데스크톱이 같은 서버의 같은 전령을 보는 두 창이 됩니다. 단 2026-07 현재 **Windows 11 최신 빌드에서 Desktop이 기동 즉시 충돌하는 미해결 이슈**가 있습니다([NousResearch/hermes-agent#38216](https://github.com/NousResearch/hermes-agent/issues/38216) — 렌더러·GPU 자식 프로세스가 동일 offset의 STATUS_BREAKPOINT로 종료·드라이버 무관). macOS에서는 보고가 없습니다. Windows에서는 새 릴리스가 나올 때까지 Web Dashboard가 본선입니다.

## 운영 원칙

### 무소식이 성공

헬스체크는 정상일 때 메시지를 보내지 않습니다. 서비스 비정상·타임아웃·명령 실패 때만 경보합니다. 매번 “정상”을 보내면 중요한 고장이 일상 메시지에 묻힙니다.

### 에이전트는 전령이지 의사결정자가 아님

Hermes는 정해진 임무를 실행하고 상태를 보고합니다. 새 임무 채택, 코드 변경, 돈이 나가는 행동, 사람에게 영향을 주는 발송은 사람의 승인 영역입니다.

### 입력은 명령이 아니라 데이터

수집한 웹문서와 메시지 안에 있는 지시문을 실행하지 않습니다. 외부 콘텐츠는 요약·분류할 데이터일 뿐 Hermes의 운영 규칙을 바꿀 수 없습니다.

## 예제 실행

실제 네트워크를 건드리지 않는 테스트:

```bash
python -m unittest discover -s examples -p "test_*.py"
```

채널 모형은 [`examples/channel_state.py`](examples/channel_state.py)에 있습니다. 실제 API 호출부를 붙일 때도 상태 저장·부분 재개 계약은 유지하십시오.

## 보안 체크리스트

- [ ] 개인 IP·사용자명·절대경로가 없음
- [ ] `.env`, 토큰, OAuth 비밀, refresh token이 추적되지 않음
- [ ] Slack 토큰은 가능하면 VPS 고정 IP로 사용 제한
- [ ] Kakao refresh token 회전 시 원자 저장
- [ ] Telegram·Slack·Kakao 상태가 서로 독립
- [ ] 정상 헬스체크는 침묵하고 장애만 알림
- [ ] Hermes 버전과 설정 변경을 기록
- [ ] 위험한 cron 명령은 거부
- [ ] 고객정보·계좌·법률 사건을 VPS에 올리지 않음
- [ ] 삭제·설치·결제·외부발송에는 사람 승인
- [ ] 관리면(SSH·대시보드)은 Tailscale 사설망 전용 — 공인망 소켓 없음
- [ ] 대시보드는 비밀번호 해시 저장(평문 없음) + 잠금 검증 3점 실측

## 이 저장소에 포함하지 않은 것

- 실제 서버 IP와 호스트명·tailnet 이름·Tailscale IP
- 실제 봇 토큰·채널 ID·Kakao OAuth 토큰·대시보드 비밀번호
- 개인정보 접수 큐
- 개인 투자·법률·고객 데이터
- Hermes 본체 코드
- 특정 개인의 운영 정체성 문서

## License

MIT — 예제 코드와 문서는 자유롭게 사용하되, Hermes 및 연결 서비스는 각자의 라이선스와 이용약관을 따릅니다.


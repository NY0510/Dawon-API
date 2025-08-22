# 다원 파워매니저 AI 스마트플러그 비공식 API

펌웨어 버전 **1.01.36**에서 **B540-W** 모델로 테스트 되었습니다.

이 코드를 사용하여 발생한 문제에 대해서는 책임지지 않습니다. 사용은 본인의 책임 하에 진행해주세요.

## 구현된 기능

- 기기 목록 조회
- 기기 상태 조회
- 현재 온도 조회
- 현재 사용 전력 조회
- 오늘까지의 이번달 누적 사용 전력 조회
- 차트 데이터 조회 (시간, 일, 월별 전력 사용량 및 요금)
- _기기 전원 제어 [구현 예정]_

## 사전 준비

AIPM 앱의 패킷을 캡쳐하여 로그인에 필요한 값을 추출해야 합니다. 패킷 캡쳐에는 [mitmproxy](https://www.mitmproxy.org/) 사용을 권장합니다.

여기서는 자세한 설명은 생략하고, 필요한 값을 추출하는 방법을 설명합니다. mitmproxy의 사용 방법은 [공식 문서](https://docs.mitmproxy.org/stable/) 및 블로그 등을 참고하세요.

캡쳐한 패킷 중 `POST https://dwapi.dawonai.com:18443/iot2/member/loginAction.opi` 요청의 Body에서 다음 값을 추출합니다: `user_id`, `sso_token`, `terminal_id`, `terminal_name`

`.env.example` 파일을 참고하여 `.env` 파일을 생성하고, 추출한 값을 입력합니다.

```ini
USER_ID=""
SSO_TOKEN=""
TERMINAL_ID=""
TERMINAL_NAME=""
```

## 실행

```bash
uv sync
uv run fastapi run src/main.py
```

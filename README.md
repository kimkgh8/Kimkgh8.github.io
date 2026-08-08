# ROOT KIM Apps

Google Play에 공개한 Android 앱의 안내, 개인정보처리방침과 고객 지원을 제공하는 정적 사이트입니다.

## 공개 경로

- `/`: 앱 개발자 홈
- `/apps/babyspace/`: 베이비스페이스 안내
- `/apps/credit-card-tracker/`: 실적메이트 안내
- `/privacy/`: 앱별 개인정보처리방침
- `/support/`: 고객 지원
- `/app-ads.txt`: AdMob 판매자 인증

## 로컬 확인

```powershell
python -m unittest discover -s tests -v
python -m http.server 4000
```
브라우저에서 `http://localhost:4000`을 엽니다.

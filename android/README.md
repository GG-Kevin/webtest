# RemoteAssist (family remote-support app, v1 scaffold)

부모-자녀 두 대의 Android 기기 사이에서, **서로 동의한 상태로 요청 → 승인 후에만** 화면을 보고
원격으로 조작(탭/스와이프/텍스트 입력)할 수 있는 개인용 앱입니다. Play 스토어에는 올리지 않고
APK를 직접 설치(사이드로드)해서 씁니다.

## 아키텍처 요약

- **백엔드는 Firestore 하나만 사용합니다.** 커스텀 서버, Cloud Functions, FCM 푸시가 없습니다.
- 앱은 두 기기 모두에서 **상시 포그라운드 서비스(`WatchService`)**를 실행해, Firestore
  실시간 리스너로 요청/응답을 직접 감지합니다 (푸시 서버가 필요 없는 이유).
- 화면 공유 + 원격 입력은 **WebRTC**로 처리합니다: 화면은 비디오 트랙, 입력 명령은 데이터채널.
  SDP/ICE 교환(시그널링)은 Firestore 문서를 통해 이루어집니다.
- 자녀 기기에서 실제 입력을 수행하는 건 Android **AccessibilityService**입니다
  (탭/스와이프는 `dispatchGesture`, 텍스트 입력은 포커스된 필드에 `ACTION_SET_TEXT`).
- 화면 캡처는 **MediaProjection**(Android 표준 화면녹화 API)을 사용하며, 세션마다 자녀 기기에서
  OS 자체의 "화면 캡처를 허용하시겠습니까?" 팝업이 한 번 더 뜹니다 (이중 확인 장치).

```
sessions/{sessionId}          요청 상태(requested/accepted/declined/ended)
sessions/{id}/signaling/offer  {sdp}
sessions/{id}/signaling/answer {sdp}
sessions/{id}/candidates_caller/*   부모(요청자) ICE candidate
sessions/{id}/candidates_callee/*   자녀(대상) ICE candidate
pairings/{code}               6자리 페어링 코드 (10분 유효)
devices/{deviceId}            역할 + 상대 기기 id
```

## 시작하기 전에

1. **Firebase 프로젝트 생성**: https://console.firebase.google.com 에서 새 프로젝트 생성
2. Android 앱 추가, 패키지명: `com.kevinfamily.remoteassist`
   (부모/자녀 두 폰이 **같은 APK**를 쓰므로 앱 등록은 한 번만 하면 됩니다)
3. `google-services.json` 다운로드 → `android/app/google-services.json` 위치에 저장
   (이 저장소에는 포함되어 있지 않습니다 — 직접 받아서 넣어야 빌드됩니다)
4. Firestore Database 생성 (Native mode), 아무 리전이나 선택
5. Firestore 규칙(Rules)에 아래 내용 적용:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /pairings/{code} {
      allow read, write: if true;
    }
    match /devices/{deviceId} {
      allow read, write: if true;
    }
    match /sessions/{sessionId} {
      allow read, write: if true;
      match /{subcollection}/{docId} {
        allow read, write: if true;
      }
    }
  }
}
```

> ⚠️ **보안 참고**: 이 v1은 Firebase Auth를 붙이지 않아서 위 규칙이 완전히 열려 있습니다 —
> 프로젝트 설정값(config)을 아는 사람은 누구나 이론적으로 읽고 쓸 수 있습니다. 개인적으로
> 빠르게 써보는 용도로는 괜찮지만(세션 id·페어링 코드가 추측 불가능한 값이라 실질적 위험은
> 낮음), 더 안전하게 하려면 Firebase Anonymous Auth를 추가하고 규칙을 `request.auth.uid`
> 기준으로 좁히는 걸 다음 단계로 추천합니다.

## 빌드 & 설치

1. Android Studio(최신 버전, JDK 17)로 `android/` 폴더 열기
2. Gradle sync (WebRTC·Firebase 의존성 자동 다운로드)
3. `google-services.json` 배치 확인 (위 단계)
4. `./gradlew assembleDebug` 또는 Android Studio에서 Run
   → APK 위치: `android/app/build/outputs/apk/debug/app-debug.apk`
5. 이 APK를 두 폰(부모/자녀) 모두에 설치
   - 사이드로드이므로 "출처를 알 수 없는 앱 설치 허용"이 필요합니다
6. 첫 실행:
   - 부모 폰: "부모입니다" 선택 → 화면에 뜨는 6자리 코드를 자녀에게 전달
   - 자녀 폰: "자녀입니다" 선택 → 코드 입력 → 페어링 완료
   - 자녀 폰: 안내에 따라 **접근성 서비스** 켜기 (설정 > 접근성 > RemoteAssist)
7. 테스트: 부모 폰에서 "원격 지원 요청" → 자녀 폰에 알림 → 승인 →
   OS 화면 캡처 허용 팝업 승인 → 부모 화면에 자녀 화면이 뜨고 조작 가능

## 알아둘 점 / 남은 작업

- **TURN 서버 없음**: 기본은 공개 STUN만 사용합니다. 같은 Wi-Fi거나 대부분의 이동통신망
  조합에서는 되지만, 특정 NAT/CGNAT 환경에서는 연결이 안 될 수 있습니다. 안 되면
  `WebRtcClient.defaultIceServers()`에 TURN 서버(예: metered.ca 무료 플랜, 또는 자체
  coturn)를 추가하세요.
- **배터리 최적화**: 두 폰 모두 이 앱을 배터리 최적화 예외로 설정해야 `WatchService`가
  백그라운드에서 계속 실행되어 요청을 놓치지 않습니다 (제조사별 절전 정책이 강할수록
  중요, 특히 자녀 폰).
- **실기기 테스트 필요**: 이 프로젝트는 코드 스캐폴딩 단계이며, Android SDK/에뮬레이터가
  없는 환경에서 작성되어 실제 컴파일·기기 테스트를 거치지 않았습니다. Android Studio에서
  열어 Gradle sync 및 실기기 빌드 시 의존성 버전 등 사소한 조정이 필요할 수 있습니다.
- **화면 해상도**: 터치 좌표는 0~1 정규화 값으로 전송되므로 두 폰의 해상도가 달라도
  동작합니다.

## 사용 시 유의사항

이 앱은 **자녀도 설치 사실과 부모의 원격 지원 가능성을 인지하고 동의한 상태**에서 쓰는 걸
전제로 설계되었습니다 (세션마다 자녀 기기의 명시적 승인 필요). 본인 소유가 아닌 기기나
동의 없는 대상에게 사용하는 것은 국가별 통신비밀보호법·개인정보보호법 위반이 될 수
있습니다.

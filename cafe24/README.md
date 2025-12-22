# 카페24 디자인보관함 업로드용 파일

이 폴더의 파일들을 카페24 디자인보관함에 업로드하여 사용할 수 있습니다.

## 📦 파일 목록

1. **tf.min.js** (약 1.4MB)
   - TensorFlow.js Core 라이브러리
   - 필수 파일

2. **body-pix.min.js** (약 200KB)
   - BodyPix 모델 (사람 전용 배경제거)
   - 선택사항

3. **deeplab.min.js** (약 500KB)
   - DeepLab 모델 (일반 객체 세그멘테이션)
   - 추천 (상품 사진에 적합)

## 📤 카페24 업로드 방법

1. 카페24 관리자 페이지 접속
2. 디자인 > 디자인보관함
3. `tfjs` 또는 `ai-libs` 폴더 생성
4. 이 폴더의 모든 `.js` 파일 업로드

## 🔗 HTML에서 사용

```html
<!-- 카페24 디자인보관함 경로로 변경 -->
<script src="https://your-domain.cafe24.com/design/tfjs/tf.min.js"></script>
<script src="https://your-domain.cafe24.com/design/tfjs/body-pix.min.js"></script>
<script src="https://your-domain.cafe24.com/design/tfjs/deeplab.min.js"></script>
```

## ⚠️ 주의사항

- 파일 크기가 크므로 카페24 디자인보관함 용량 제한 확인 필요
- CORS 설정이 필요할 수 있음
- 모델 파일은 별도로 다운로드 필요 (DeepLab의 경우)

## 📚 참고

- TensorFlow.js: https://www.tensorflow.org/js
- BodyPix: https://github.com/tensorflow/tfjs-models/tree/master/body-pix
- DeepLab: https://github.com/tensorflow/tfjs-models/tree/master/deeplab


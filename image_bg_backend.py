from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image
from io import BytesIO
from rembg import remove, new_session
import threading

app = Flask(__name__)
CORS(app)  # CORS 허용

# 모델 세션을 lazy load로 변경 (메모리 절약 및 시작 시간 단축)
u2net_session = None
session_lock = threading.Lock()

def get_session():
    """모델 세션을 lazy load로 가져오기"""
    global u2net_session
    if u2net_session is None:
        with session_lock:
            if u2net_session is None:
                u2net_session = new_session('u2net')
    return u2net_session

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return {'status': 'ok'}, 200

@app.route('/api/remove_bg', methods=['POST'])
def remove_bg():
    """배경 제거 API"""
    try:
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
        
        # width, height 파라미터 가져오기
        width = int(request.form.get('width', 600))
        height = int(request.form.get('height', 600))
        
        # 이미지 로드
        image = Image.open(file.stream)
        
        # 배경 제거 (투명 배경 PNG 반환)
        # 이미지를 바이트로 변환
        img_bytes = BytesIO()
        image.convert("RGB").save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        # rembg로 배경 제거 (투명 배경) - lazy load 세션 사용
        session = get_session()
        result_bytes = remove(
            img_bytes.getvalue(),
            session=session,
            alpha_matting=False
        )
        
        # 결과 이미지 로드
        result_image = Image.open(BytesIO(result_bytes)).convert("RGBA")
        
        # 리사이징 및 중앙 정렬
        result_image.thumbnail((width, height), Image.Resampling.LANCZOS)
        new_img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        paste_x = (width - result_image.width) // 2
        paste_y = (height - result_image.height) // 2
        new_img.paste(result_image, (paste_x, paste_y), result_image)
        
        # PNG로 변환 (투명도 포함)
        output = BytesIO()
        new_img.save(output, format='PNG')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/png',
            as_attachment=False
        )
        
    except Exception as e:
        import traceback
        error_msg = f"배경 제거 실패: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {'error': error_msg}, 500

if __name__ == '__main__':
    print("=" * 50)
    print("배경 제거 백엔드 서버 시작")
    print("=" * 50)
    print("서버 주소: http://localhost:5001")
    print("API 엔드포인트: /api/remove_bg")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)


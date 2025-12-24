from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image
from io import BytesIO
from rembg import remove, new_session
import threading
import numpy as np
import cv2
from skimage.morphology import dilation, disk, closing, opening
from skimage.measure import label, regionprops
from pymatting import estimate_alpha_cf

app = Flask(__name__)
# CORS 명시적 설정 (GitHub Pages 포함)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://jecng.github.io", "http://localhost:*", "https://*.github.io"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

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

def refine_alpha_mask(alpha):
    """알파 마스크 정제: morphology, connected components, 텍스트 제거"""
    # 1. Morphology operations으로 노이즈 제거
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    alpha_uint8 = (alpha * 255).astype(np.uint8)
    
    # Opening: 작은 노이즈 제거
    alpha_cleaned = cv2.morphologyEx(alpha_uint8, cv2.MORPH_OPEN, kernel, iterations=2)
    # Closing: 작은 구멍 채우기
    alpha_cleaned = cv2.morphologyEx(alpha_cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # 2. Gaussian blur로 엣지 부드럽게
    alpha_cleaned = cv2.GaussianBlur(alpha_cleaned, (5, 5), 1.0)
    
    # 3. Connected components로 가장 큰 객체만 유지
    _, labels = cv2.connectedComponents(alpha_cleaned > 128)
    if labels.max() > 0:
        # 각 컴포넌트의 크기 계산
        unique, counts = np.unique(labels[labels > 0], return_counts=True)
        if len(unique) > 0:
            largest_component = unique[np.argmax(counts)]
            alpha_cleaned = (labels == largest_component).astype(np.uint8) * 255
    
    # 4. 상단 22% 영역의 작은 컴포넌트 제거 (텍스트 제거)
    h, w = alpha_cleaned.shape
    top_ignore = int(h * 0.22)
    top_region = alpha_cleaned[:top_ignore, :]
    _, top_labels = cv2.connectedComponents(top_region > 128)
    if top_labels.max() > 0:
        unique, counts = np.unique(top_labels[top_labels > 0], return_counts=True)
        # 작은 컴포넌트 제거 (전체의 5% 미만)
        min_area = (h * w) * 0.05
        for comp_id, count in zip(unique, counts):
            if count < min_area:
                top_region[top_labels == comp_id] = 0
        alpha_cleaned[:top_ignore, :] = top_region
    
    return alpha_cleaned.astype(np.float32) / 255.0

def generate_trimap(alpha, fg_thresh=230, bg_thresh=15, kernel_size=8):
    """Trimap 생성 (pymatting용)"""
    fg = alpha > (fg_thresh / 255.0)
    bg = alpha < (bg_thresh / 255.0)
    unknown = ~(fg | bg)
    
    trimap = np.full(alpha.shape, 128, dtype=np.uint8)
    trimap[fg] = 255
    trimap[bg] = 0
    
    # Dilation으로 unknown 영역 확장
    trimap = dilation(trimap, disk(kernel_size))
    return trimap

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """서버 상태 확인"""
    if request.method == 'OPTIONS':
        return '', 200
    return {'status': 'ok'}, 200

@app.route('/api/remove_bg', methods=['POST', 'OPTIONS'])
def remove_bg():
    """배경 제거 API"""
    if request.method == 'OPTIONS':
        return '', 200
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
        original_size = image.size
        
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
        np_img = np.array(result_image)
        alpha = np_img[..., 3].astype(np.float32) / 255.0
        
        # 알파 마스크 정제
        alpha_refined = refine_alpha_mask(alpha)
        
        # Trimap 생성 및 pymatting으로 엣지 개선
        trimap = generate_trimap((alpha_refined * 255).astype(np.uint8))
        try:
            alpha_matted = estimate_alpha_cf(np_img[..., :3] / 255.0, trimap / 255.0)
            alpha_final = (alpha_matted * 255).astype(np.uint8)
        except:
            # pymatting 실패 시 정제된 알파 사용
            alpha_final = (alpha_refined * 255).astype(np.uint8)
        
        # 최종 알파 마스크로 이미지 생성
        np_img[..., 3] = alpha_final
        result_image = Image.fromarray(np_img, 'RGBA')
        
        # 바운딩 박스 계산 (알파 > 0인 영역)
        mask = alpha_final > 0
        if np.any(mask):
            ys, xs = np.where(mask)
            ymin, ymax = ys.min(), ys.max()
            xmin, xmax = xs.min(), xs.max()
            # 패딩 추가 (3% 또는 최소 20px)
            padding = max(20, int(min(original_size) * 0.03))
            xmin = max(0, xmin - padding)
            ymin = max(0, ymin - padding)
            xmax = min(original_size[0] - 1, xmax + padding)
            ymax = min(original_size[1] - 1, ymax + padding)
            
            # 크롭
            result_image = result_image.crop((xmin, ymin, xmax + 1, ymax + 1))
        
        # 리사이징: thumbnail 방식 (비율 유지, 큰 쪽만 축소)
        result_w, result_h = result_image.size
        if result_w > width or result_h > height:
            scale = min(width / result_w, height / result_h)
            new_w = int(result_w * scale)
            new_h = int(result_h * scale)
            result_image = result_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            new_w, new_h = result_w, result_h
        
        # 중앙 정렬
        new_img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        paste_x = (width - new_w) // 2
        paste_y = (height - new_h) // 2
        new_img.paste(result_image, (paste_x, paste_y), result_image)
        
        # PNG로 변환 (투명도 포함)
        output = BytesIO()
        new_img.save(output, format='PNG', optimize=False)
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


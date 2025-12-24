from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
from io import BytesIO
from rembg import remove, new_session
import threading
import numpy as np
import cv2
from skimage.morphology import dilation, disk
# pymatting은 메모리 부족으로 인한 크래시 방지를 위해 선택적 import
try:
    from pymatting import estimate_alpha_cf
    PYMATTING_AVAILABLE = True
except ImportError:
    PYMATTING_AVAILABLE = False
    print("Warning: pymatting not available, using simplified alpha refinement")
import traceback

app = Flask(__name__)
# CORS 설정 - 모든 origin 허용 (개발/프로덕션 모두)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

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
    """알파 마스크 정제: morphology + connected components (상단 텍스트 제거)"""
    try:
        alpha_uint8 = (alpha * 255).astype(np.uint8)
        h, w = alpha_uint8.shape
        
        # 1. Morphology로 노이즈 제거
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        alpha_cleaned = cv2.morphologyEx(alpha_uint8, cv2.MORPH_OPEN, kernel, iterations=1)
        alpha_cleaned = cv2.morphologyEx(alpha_cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # 2. Connected components로 상단 텍스트 제거 (메모리 효율적으로)
        # 상단 22% 영역에서만 작은 컴포넌트 제거
        top_region_height = int(h * 0.22)
        if top_region_height > 0:
            try:
                # 이진 마스크 생성 (알파 > 128인 영역)
                binary = (alpha_cleaned > 128).astype(np.uint8) * 255
                
                # Connected components 분석 (최소 면적만 계산)
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
                
                if num_labels > 1:  # 배경(0) 외에 컴포넌트가 있으면
                    # 전체 이미지에서 가장 큰 컴포넌트 찾기
                    # stats 구조: [left, top, width, height, area]
                    CC_STAT_AREA = 4
                    largest_area = 0
                    largest_label = 1
                    for label in range(1, num_labels):
                        area = stats[label, CC_STAT_AREA]
                        if area > largest_area:
                            largest_area = area
                            largest_label = label
                    
                    # 상단 영역의 작은 컴포넌트 제거
                    mask = np.zeros_like(alpha_cleaned, dtype=np.uint8)
                    for label in range(1, num_labels):
                        if label == largest_label:
                            # 가장 큰 컴포넌트는 항상 유지
                            mask[labels == label] = 255
                        else:
                            # 상단 영역에 있는 작은 컴포넌트만 제거
                            y_center = int(centroids[label, 1])
                            area = stats[label, CC_STAT_AREA]
                            if y_center < top_region_height and area < (w * h * 0.05):  # 상단 + 작은 면적
                                continue  # 제거
                            else:
                                mask[labels == label] = 255
                    
                    # 마스크 적용
                    alpha_cleaned = np.where(mask > 0, alpha_cleaned, 0)
            except Exception as e:
                print(f"Connected components 실패, morphology만 사용: {str(e)}")
        
        # 3. Gaussian blur (가볍게)
        alpha_cleaned = cv2.GaussianBlur(alpha_cleaned, (3, 3), 0.5)
        
        return alpha_cleaned.astype(np.float32) / 255.0
    except Exception as e:
        print(f"refine_alpha_mask 실패, 원본 사용: {str(e)}")
        return alpha

def generate_trimap(alpha, fg_thresh=230, bg_thresh=15, kernel_size=8):
    """Trimap 생성 (pymatting용) - 현재 비활성화"""
    # 메모리 절약을 위해 간단한 버전만
    alpha_uint8 = alpha if isinstance(alpha, np.ndarray) and alpha.dtype == np.uint8 else (alpha * 255).astype(np.uint8)
    fg = alpha_uint8 > fg_thresh
    bg = alpha_uint8 < bg_thresh
    unknown = ~(fg | bg)
    
    trimap = np.full(alpha_uint8.shape, 128, dtype=np.uint8)
    trimap[fg] = 255
    trimap[bg] = 0
    
    # Dilation은 메모리 절약을 위해 작은 커널만
    try:
        trimap = dilation(trimap, disk(min(kernel_size, 5)))
    except:
        pass
    return trimap

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """서버 상태 확인"""
    try:
        if request.method == 'OPTIONS':
            return '', 200
        return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/remove_bg', methods=['POST', 'OPTIONS'])
def remove_bg():
    """배경 제거 API"""
    if request.method == 'OPTIONS':
        return '', 200
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
        
        # 알파 마스크 정제 (간단한 버전만)
        try:
            alpha_refined = refine_alpha_mask(alpha)
            alpha_final = (alpha_refined * 255).astype(np.uint8)
        except Exception as e:
            # 정제 실패 시 원본 알파 사용
            print(f"알파 정제 실패, 원본 사용: {str(e)}")
            alpha_final = (alpha * 255).astype(np.uint8)
        
        # pymatting은 메모리 부족으로 인한 크래시 방지를 위해 비활성화
        # 필요시 주석 해제 (메모리 여유 있을 때만)
        # try:
        #     trimap = generate_trimap(alpha_final)
        #     alpha_matted = estimate_alpha_cf(np_img[..., :3] / 255.0, trimap / 255.0)
        #     alpha_final = (alpha_matted * 255).astype(np.uint8)
        # except Exception as e:
        #     print(f"Pymatting 실패, 정제된 알파 사용: {str(e)}")
        
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
        error_msg = f"배경 제거 실패: {str(e)}"
        error_trace = traceback.format_exc()
        print(f"ERROR: {error_msg}\n{error_trace}")
        # 에러 메시지는 간단하게, 상세는 서버 로그에만
        return jsonify({'error': 'Background removal failed', 'message': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("배경 제거 백엔드 서버 시작")
    print("=" * 50)
    print("서버 주소: http://localhost:5001")
    print("API 엔드포인트: /api/remove_bg")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)


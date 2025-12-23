import logging
import numpy as np
from PIL import Image
from io import BytesIO
from rembg import remove, new_session
import multiprocessing
import cv2

# 전역에서 1회만 모델 세션 로딩 (지연 로딩)
u2net_session = None

def get_session():
    """모델 세션을 지연 로딩 (첫 사용 시에만 다운로드)"""
    global u2net_session
    if u2net_session is None:
        logging.info("u2net 모델 세션 초기화 중...")
        u2net_session = new_session('u2net')
        logging.info("u2net 모델 세션 초기화 완료")
    return u2net_session

def is_mostly_white(image, threshold=220, ratio=0.9):
    gray = image.convert("L")
    np_img = np.array(gray)
    white_pixels = np.sum(np_img > threshold)
    total_pixels = np_img.size
    return (white_pixels / total_pixels) > ratio

def remove_background(image, bg_size):
    try:
        # NOTE:
        # 기존에는 거의 전체가 흰색인 이미지는 is_mostly_white() 판단 후
        # 배경제거를 생략했는데, 실제 상품 사진(하얀 배경 위 상품)에서도
        # 이 조건이 자주 걸려 버려서 \"배경제거 안됨\" 현상이 발생함.
        # → 최종적으로 항상 rembg/u2net을 거치도록 변경.
        img = image.convert("RGB")
        buf = BytesIO()
        img.save(buf, format="PNG")
        input_bytes = buf.getvalue()
        # 전역 세션 재사용
        session = get_session()
        result_bytes = remove(
            input_bytes,
            session=session,
            alpha_matting=False
        )
        result = Image.open(BytesIO(result_bytes)).convert("RGBA")
        np_img = np.array(result)
        alpha = np_img[..., 3]

        # 소금/후추 노이즈 제거 + 경계 매끄럽게 (작은 점 사라지도록)
        alpha_denoised = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        alpha_denoised = cv2.morphologyEx(alpha_denoised, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        alpha_denoised = cv2.GaussianBlur(alpha_denoised, (0, 0), sigmaX=1.5)
        alpha_denoised = np.clip(alpha_denoised, 0, 255).astype(np.uint8)

        # Trimap 생성 및 pymatting 적용 (조금 더 관대한 임계값으로 텍스트·금속 보존)
        from skimage.morphology import dilation, disk
        from pymatting import estimate_alpha_cf
        def generate_trimap(alpha, fg_thresh=230, bg_thresh=15, kernel_size=8):
            fg = alpha > fg_thresh
            bg = alpha < bg_thresh
            unknown = ~(fg | bg)
            trimap = np.full(alpha.shape, 128, dtype=np.uint8)
            trimap[fg] = 255
            trimap[bg] = 0
            trimap = dilation(trimap, disk(kernel_size))
            return trimap
        trimap = generate_trimap(alpha_denoised)
        alpha_matted = estimate_alpha_cf(np_img[..., :3]/255.0, trimap/255.0)
        alpha_matted_uint8 = (alpha_matted * 255).astype(np.uint8)

        # 객체만 crop: 가장 큰 연결 성분만 남기기 (텍스트/잡영역 제거)
        mask = alpha_matted_uint8 > 0
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
        if num_labels > 1:
            # label 0은 배경
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            mask = labels == largest_label
            alpha_matted_uint8 = (mask * 255).astype(np.uint8)
        if not np.any(mask):
            # 객체가 없으면 흰색 배경만 반환
            return Image.new("RGB", bg_size, (255,255,255))
        ys, xs = np.where(mask)
        ymin, ymax = ys.min(), ys.max()
        xmin, xmax = xs.min(), xs.max()
        cropped = result.crop((xmin, ymin, xmax+1, ymax+1))
        # 흰색 배경 생성 및 중앙에 붙여넣기
        background = Image.new("RGB", bg_size, (255,255,255))
        cw, ch = cropped.size
        bx, by = (bg_size[0] - cw)//2, (bg_size[1] - ch)//2
        background.paste(cropped.convert("RGB"), (bx, by), mask=cropped.split()[-1])
        return background
    except Exception as e:
        logging.error(f"배경제거 실패: {e}")
        return image.convert("RGB")



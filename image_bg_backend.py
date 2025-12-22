import logging
from io import BytesIO

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image

from background_removal import remove_background


app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/remove_bg", methods=["POST"])
def api_remove_bg():
    """
    프론트엔드에서 전송한 이미지를 rembg/u2net으로 배경제거 후 PNG로 반환.

    요청:
      - form-data: file=<이미지 파일>
      - 선택: width, height (정수, 없으면 원본 크기)

    응답:
      - image/png 바이너리 (투명 배경)
    """
    if "file" not in request.files:
        return jsonify({"error": "file 필드가 필요합니다."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "빈 파일명입니다."}), 400

    try:
        img = Image.open(file.stream).convert("RGB")

        # 원하는 출력 크기 (없으면 원본)
        try:
            width = int(request.form.get("width", 0))
            height = int(request.form.get("height", 0))
        except ValueError:
            width = height = 0

        if width > 0 and height > 0:
            bg_size = (width, height)
        else:
            bg_size = img.size

        logging.info("배경제거 요청: %s, size=%s -> bg_size=%s", file.filename, img.size, bg_size)

        result = remove_background(img, bg_size)

        buf = BytesIO()
        # 투명 배경을 위해 PNG 사용
        result.save(buf, format="PNG")
        buf.seek(0)

        return send_file(
            buf,
            mimetype="image/png",
            as_attachment=False,
        )
    except Exception as e:
        logging.exception("배경제거 처리 중 오류")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # 로컬 테스트용 엔트리포인트
    # python github_release/image_bg_backend.py
    app.run(host="0.0.0.0", port=5001, debug=False)



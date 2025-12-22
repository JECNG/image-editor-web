from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import subprocess
import shutil
import time
from pathlib import Path

app = Flask(__name__)
CORS(app)  # CORS 허용

# FFmpeg 경로 설정 (시스템 PATH에 있으면 'ffmpeg', 아니면 절대 경로)
FFMPEG_PATH = os.environ.get('FFMPEG_PATH', 'ffmpeg')

# 위치 좌표 매핑
POSITION_COORDS = {
    "top-left": ("10", "10"),
    "top-center": ("(w-text_w)/2", "10"),
    "top-right": ("if(gte(text_w,(w-20)), 10, (w-text_w)-10)", "10"),
    "mid-left": ("10", "(h-text_h)/2"),
    "mid-center": ("(w-text_w)/2", "(h-text_h)/2"),
    "mid-right": ("if(gte(text_w,(w-20)), 10, (w-text_w)-10)", "(h-text_h)/2"),
    "bot-left": ("10", "(h-text_h)-10"),
    "bot-center": ("(w-text_w)/2", "(h-text_h)-10"),
    "bot-right": ("if(gte(text_w,(w-20)), 10, (w-text_w)-10)",
                  "if(gte(text_h,(h-20)), 10, (h-text_h)-10)")
}

def escape_text(text):
    """FFmpeg drawtext 필터용 텍스트 이스케이프"""
    return text.replace('\\', '\\\\').replace(':', '\\:').replace("'", "\\'")

def convert_video_to_webp(input_path, output_path, settings):
    """MP4를 WEBP로 변환"""
    try:
        width = settings.get('width', 600)
        watermark_text = settings.get('watermarkText', '')
        watermark_color = settings.get('watermarkColor', '#FFFFFF')
        font_size = settings.get('fontSize', 24)
        opacity = settings.get('opacity', 0.5)
        position = settings.get('position', 'mid-center')
        video_length = settings.get('videoLength', 'full')
        start_time = settings.get('startTime', '00:00:00')
        end_time = settings.get('endTime', '00:00:05')
        
        # FFmpeg 명령어 구성
        cmd = [FFMPEG_PATH, '-i', input_path]
        
        # 시간 구간 설정
        if video_length == 'partial':
            cmd.extend(['-ss', start_time, '-t', end_time])
        
        # 워터마크 추가
        if watermark_text:
            x, y = POSITION_COORDS.get(position, POSITION_COORDS['mid-center'])
            escaped_text = escape_text(watermark_text)
            
            # 색상 변환 (hex to RGB)
            color_hex = watermark_color.lstrip('#')
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            
            # drawtext 필터
            drawtext_filter = (
                f"drawtext=text='{escaped_text}':"
                f"fontsize={font_size}:"
                f"fontcolor={r:02x}{g:02x}{b:02x}@{int(opacity * 255):02x}:"
                f"x={x}:y={y}"
            )
            cmd.extend(['-vf', f"scale={width}:-1,{drawtext_filter}"])
        else:
            cmd.extend(['-vf', f"scale={width}:-1"])
        
        # WEBP 출력 설정
        cmd.extend([
            '-loop', '0',
            '-preset', 'default',
            '-an',  # 오디오 제거
            '-vsync', '0',
            output_path,
            '-y'  # 덮어쓰기
        ])
        
        # FFmpeg 실행
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5분 타임아웃
        )
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        return True
    except Exception as e:
        raise Exception(f"WEBP conversion failed: {str(e)}")

def convert_video_to_gif(input_path, output_path, settings):
    """MP4를 GIF로 변환"""
    try:
        width = settings.get('width', 600)
        watermark_text = settings.get('watermarkText', '')
        watermark_color = settings.get('watermarkColor', '#FFFFFF')
        font_size = settings.get('fontSize', 24)
        opacity = settings.get('opacity', 0.5)
        position = settings.get('position', 'mid-center')
        video_length = settings.get('videoLength', 'full')
        start_time = settings.get('startTime', '00:00:00')
        end_time = settings.get('endTime', '00:00:05')
        
        # 임시 디렉토리 생성
        temp_dir = tempfile.mkdtemp()
        palette_path = os.path.join(temp_dir, 'palette.png')
        temp_gif_path = os.path.join(temp_dir, 'temp.gif')
        
        try:
            # 1단계: 팔레트 생성
            palette_cmd = [FFMPEG_PATH, '-i', input_path]
            if video_length == 'partial':
                palette_cmd.extend(['-ss', start_time, '-t', end_time])
            palette_cmd.extend([
                '-vf', f"fps=12,scale={width}:-1:flags=lanczos,palettegen",
                '-y', palette_path
            ])
            
            result = subprocess.run(palette_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise Exception(f"Palette generation failed: {result.stderr}")
            
            # 2단계: GIF 생성
            gif_cmd = [FFMPEG_PATH, '-i', input_path, '-i', palette_path]
            if video_length == 'partial':
                gif_cmd.extend(['-ss', start_time, '-t', end_time])
            
            # 워터마크 추가
            if watermark_text:
                x, y = POSITION_COORDS.get(position, POSITION_COORDS['mid-center'])
                escaped_text = escape_text(watermark_text)
                
                color_hex = watermark_color.lstrip('#')
                r = int(color_hex[0:2], 16)
                g = int(color_hex[2:4], 16)
                b = int(color_hex[4:6], 16)
                
                drawtext_filter = (
                    f"drawtext=text='{escaped_text}':"
                    f"fontsize={font_size}:"
                    f"fontcolor={r:02x}{g:02x}{b:02x}@{int(opacity * 255):02x}:"
                    f"x={x}:y={y}"
                )
                gif_cmd.extend([
                    '-filter_complex',
                    f"[0:v]fps=12,scale={width}:-1:flags=lanczos[scaled];"
                    f"[scaled][1:v]paletteuse[pal];"
                    f"[pal]{drawtext_filter}",
                    '-y', temp_gif_path
                ])
            else:
                gif_cmd.extend([
                    '-filter_complex',
                    f"[0:v]fps=12,scale={width}:-1:flags=lanczos[scaled];"
                    f"[scaled][1:v]paletteuse",
                    '-y', temp_gif_path
                ])
            
            result = subprocess.run(gif_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise Exception(f"GIF conversion failed: {result.stderr}")
            
            # 최종 파일로 이동
            shutil.move(temp_gif_path, output_path)
            return True
            
        finally:
            # 임시 파일 정리
            try:
                if os.path.exists(palette_path):
                    os.remove(palette_path)
                if os.path.exists(temp_gif_path):
                    os.remove(temp_gif_path)
                os.rmdir(temp_dir)
            except:
                pass
                
    except Exception as e:
        raise Exception(f"GIF conversion failed: {str(e)}")

@app.route('/api/convert', methods=['POST'])
def convert_video():
    """비디오 변환 API"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 설정 가져오기
        settings = {
            'watermarkText': request.form.get('watermarkText', ''),
            'watermarkColor': request.form.get('watermarkColor', '#FFFFFF'),
            'fontSize': int(request.form.get('fontSize', 24)),
            'opacity': float(request.form.get('opacity', 0.5)),
            'position': request.form.get('position', 'mid-center'),
            'videoLength': request.form.get('videoLength', 'full'),
            'startTime': request.form.get('startTime', '00:00:00'),
            'endTime': request.form.get('endTime', '00:00:05'),
            'width': int(request.form.get('width', 600)),
            'format': request.form.get('format', 'webp')
        }
        
        # 임시 파일 저장
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, file.filename)
        file.save(input_path)
        
        # 출력 파일 경로
        output_format = settings['format']
        output_filename = os.path.splitext(file.filename)[0] + f'.{output_format}'
        output_path = os.path.join(temp_dir, output_filename)
        
        try:
            # 변환 실행
            if output_format == 'webp':
                convert_video_to_webp(input_path, output_path, settings)
            elif output_format == 'gif':
                convert_video_to_gif(input_path, output_path, settings)
            else:
                return jsonify({'error': f'Unsupported format: {output_format}'}), 400
            
            # 변환된 파일 반환
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype=f'image/{output_format}'
            )
            
        finally:
            # 임시 파일 정리 (약간의 지연 후)
            def cleanup():
                time.sleep(5)  # 파일 다운로드 대기
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
            
            import threading
            threading.Thread(target=cleanup, daemon=True).start()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    # FFmpeg 확인
    try:
        result = subprocess.run(
            [FFMPEG_PATH, '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        ffmpeg_available = result.returncode == 0
    except:
        ffmpeg_available = False
    
    return jsonify({
        'status': 'ok',
        'ffmpeg_available': ffmpeg_available
    })

if __name__ == '__main__':
    print("=" * 50)
    print("백엔드 서버 시작")
    print("=" * 50)
    print(f"FFmpeg 경로: {FFMPEG_PATH}")
    print("서버 주소: http://localhost:5000")
    print("API 엔드포인트: /api/convert")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)


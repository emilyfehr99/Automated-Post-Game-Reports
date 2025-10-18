from flask import Flask, render_template, request, jsonify, send_file
import os
import cv2
import numpy as np
import base64
from werkzeug.utils import secure_filename
import gc
import psutil
import pandas as pd
from datetime import datetime
import time # Added for time.time()

# Import only what we need for Roboflow
try:
    from roboflow_detector import get_inference_detector
    INFERENCE_AVAILABLE = True
    print("✅ Roboflow Inference Pipeline available")
except ImportError:
    INFERENCE_AVAILABLE = False
    print("❌ Roboflow Inference Pipeline not available")

app = Flask(__name__)
print("🏒 STRIDE ANALYSIS APP STARTING - ROBOFLOF ONLY! 🏒")
print("   Port: 8237 | Focus: Hockey player detection & stride analysis")

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_memory():
    """Clear memory to prevent slowdowns"""
    gc.collect()
    for i in range(3):
        gc.collect()

def log_memory_usage():
    """Log current memory usage"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        print(f"💾 Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
    except:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyze', methods=['POST'])
def analyze_video():
    data = request.get_json()
    analysis_type = data.get('analysis_type')
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    if analysis_type == 'stride':
        # For stride analysis, we need player selection first
        # Return a response that triggers the player selection modal
        return jsonify({
            'requires_interaction': True,
            'video_filename': filename,
            'analysis_type': 'stride',
            'message': 'Please select a player for stride analysis'
        })
    else:
        return jsonify({'error': 'Invalid analysis type'}), 400

def analyze_stride(filename, player_bbox):
    """Analyze stride metrics for a selected player using Roboflow video inference"""
    try:
        # Setup output paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"outputs/stride_metrics_{timestamp}.csv"
        output_video_path = f"outputs/stride_analysis_{timestamp}.mp4"
        skeleton_video_path = f"outputs/stride_skeleton_{timestamp}.mp4"
        
        # Ensure output directory exists
        os.makedirs("outputs", exist_ok=True)
        
        video_path = f"uploads/{filename}"
        if not os.path.exists(video_path):
            return jsonify({"error": "Video file not found"}), 404
        
        print(f"🎯 Starting stride analysis for {filename}")
        print(f"   Player bbox: {player_bbox}")
        
        # Get video properties
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        print(f"📹 Video: {width}x{height}, {fps} FPS, {total_frames} frames")
        
        # Use Roboflow video inference for much faster processing
        if not INFERENCE_AVAILABLE:
            return jsonify({"error": "Roboflow model not available - required for stride analysis"}), 500
        
        detector = get_inference_detector()
        print(f"🎯 Using Roboflow video inference for stride analysis")
        
        # Run video inference to get all player detections
        print(f"🚀 Running Roboflow video inference...")
        start_time = time.time()
        
        # Try hosted video inference first, but with timeout
        all_detections = []
        try:
            print(f"⏱️  Attempting hosted video inference (timeout: 120s)...")
            all_detections = detector.detect_players_in_video(video_path, max_fps=30)
            
            inference_time = time.time() - start_time
            if inference_time > 120:  # 2 minute timeout
                print(f"⚠️  Hosted video inference took too long ({inference_time:.1f}s), falling back to frame-by-frame")
                all_detections = []
            else:
                print(f"⚡ Video inference completed in {inference_time:.2f}s")
                print(f"📊 Found {len(all_detections)} total detections")
        except Exception as e:
            print(f"⚠️  Hosted video inference failed: {e}, falling back to frame-by-frame")
            all_detections = []
        
        # If hosted inference failed or timed out, use frame-by-frame processing
        if not all_detections:
            print(f"🔄 Falling back to frame-by-frame processing...")
            all_detections = process_video_frame_by_frame(video_path, player_bbox, fps, width, height)
            print(f"📊 Frame-by-frame processing found {len(all_detections)} detections")
        
        if not all_detections:
            return jsonify({"error": "No players detected in video"}), 400
        
        # Filter detections for our selected player
        target_center = (player_bbox[0] + player_bbox[2]/2, player_bbox[1] + player_bbox[3]/2)
        target_width = player_bbox[2]
        target_height = player_bbox[3]
        
        print(f"🎯 Target player: center={target_center}, size={target_width}x{target_height}")
        
        # Group detections by frame and find the best match for our target player
        frame_detections = {}
        
        for detection in all_detections:
            frame_num = detection.get('frame', 0)  # Default to frame 0 if not specified
            if frame_num not in frame_detections:
                frame_detections[frame_num] = []
            frame_detections[frame_num].append(detection)
        
        print(f"📊 Grouped detections into {len(frame_detections)} frames")
        
        # Create video writers
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        skeleton_out = cv2.VideoWriter(skeleton_video_path, fourcc, fps, (width, height))
        
        # Process video frames and apply detections
        cap = cv2.VideoCapture(video_path)
        joint_rows = []
        frame_count = 0
        stride_count = 0
        last_foot_position = None
        stride_lengths = []
        speed_measurements = []
        
        print(f"🎬 Processing video frames with detections...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Initialize frame data
            frame_data = {
                'frame': frame_count,
                'timestamp': frame_count / fps,
                'player_detected': False,
                'player_bbox': None,
                'player_center_x': None,
                'player_center_y': None,
                'stride_length': None,
                'stride_frequency': None,
                'player_speed': None
            }
            
            # Find the best player detection for this frame
            frame_detection = None
            best_match_score = 0
            
            # Check if we have detections for this frame
            if frame_count in frame_detections:
                for detection in frame_detections[frame_count]:
                    bbox = detection['bbox']
                    player_center = (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)
                    
                    # Calculate similarity score based on:
                    # 1. Distance to target center
                    # 2. Size similarity
                    # 3. Class type (prefer same class as target)
                    
                    # Distance score (closer = higher score)
                    distance = np.sqrt((player_center[0] - target_center[0])**2 + 
                                     (player_center[1] - target_center[1])**2)
                    distance_score = max(0, 100 - distance)  # 100 points for perfect match, decreasing with distance
                    
                    # Size similarity score
                    size_diff = abs(bbox[2] - target_width) + abs(bbox[3] - target_height)
                    size_score = max(0, 50 - size_diff/2)  # 50 points for perfect size match
                    
                    # Class bonus (if we can determine class)
                    class_bonus = 0
                    if 'class' in detection:
                        if detection['class'] in ['player', 'goalkeeper']:
                            class_bonus = 25  # Bonus for player-like objects
                    
                    # Total match score
                    match_score = distance_score + size_score + class_bonus
                    
                    if match_score > best_match_score:
                        best_match_score = match_score
                        frame_detection = detection
                
                print(f"   Frame {frame_count}: Best match score = {best_match_score:.1f}")
            
            if frame_detection and best_match_score > 30:  # Only use detection if score is good enough
                # Player detected in this frame
                bbox = frame_detection['bbox']
                x, y, w, h = bbox
                
                frame_data.update({
                    'player_detected': True,
                    'player_bbox': bbox,
                    'player_center_x': x + w/2,
                    'player_center_y': y + h/2
                })
                
                # Calculate stride metrics
                current_foot_position = (x + w/2, y + h)
                
                if last_foot_position is not None:
                    # Calculate stride length
                    stride_length = np.sqrt((current_foot_position[0] - last_foot_position[0])**2 + 
                                          (current_foot_position[1] - last_foot_position[1])**2)
                    
                    # Detect stride (significant movement)
                    if stride_length > 20:  # 20 pixel threshold
                        stride_count += 1
                        stride_lengths.append(stride_length)
                        
                        # Calculate speed
                        time_diff = 1 / fps
                        speed = stride_length / time_diff
                        speed_measurements.append(speed)
                        
                        frame_data.update({
                            'stride_length': stride_length,
                            'stride_frequency': stride_count / (frame_count / fps),
                            'player_speed': speed
                        })
                
                last_foot_position = current_foot_position
                
                # Draw annotations on frame
                annotated_frame = frame.copy()
                cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Add text overlay
                text = f"Target Player (Score: {best_match_score:.1f})"
                cv2.putText(annotated_frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Add stride info if available
                if frame_data['stride_length']:
                    stride_text = f"Stride: {frame_data['stride_length']:.1f}px"
                    cv2.putText(annotated_frame, stride_text, (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                out_video.write(annotated_frame)
                
                # Create skeleton frame
                skeleton_frame = create_stride_skeleton_frame(frame_detection, width, height)
                skeleton_out.write(skeleton_frame)
                
            else:
                # No good player match in this frame
                out_video.write(frame)
                skeleton_out.write(create_blank_grid_frame(width, height))
            
            joint_rows.append(frame_data)
            
            # Progress update
            if frame_count % 30 == 0:
                print(f"📊 Processed {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")
        
        cap.release()
        out_video.release()
        skeleton_out.release()
        
        # Calculate summary statistics
        total_time = total_frames / fps
        avg_stride_length = np.mean(stride_lengths) if stride_lengths else 0
        avg_speed = np.mean(speed_measurements) if speed_measurements else 0
        stride_frequency = stride_count / total_time if total_time > 0 else 0
        
        print(f"📊 Stride Analysis Complete:")
        print(f"   Total strides: {stride_count}")
        print(f"   Average stride length: {avg_stride_length:.1f} pixels")
        print(f"   Average speed: {avg_speed:.1f} pixels/s")
        print(f"   Stride frequency: {stride_frequency:.2f} strides/s")
        
        # Save to CSV
        df = pd.DataFrame(joint_rows)
        df.to_csv(csv_path, index=False)
        
        # Return results
        return {
            "success": True,
            "message": "Stride analysis completed successfully",
            "filename": filename,
            "total_frames": total_frames,
            "total_time": f"{total_time:.2f}s",
            "stride_count": stride_count,
            "avg_stride_length": f"{avg_stride_length:.1f}px",
            "avg_speed": f"{avg_speed:.1f}px/s",
            "stride_frequency": f"{stride_frequency:.2f}/s",
            "csv_path": csv_path,
            "output_video_path": output_video_path,
            "skeleton_video_path": skeleton_video_path
        }
        
    except Exception as e:
        print(f"❌ Stride analysis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Stride analysis failed: {str(e)}"}), 500

@app.route('/detect_players/<filename>')
def detect_players(filename):
    """Detect hockey players using Roboflow model ONLY"""
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video not found'}), 404
    
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return jsonify({'error': 'Could not read video frame'}), 500
    
    # Performance optimization: Resize frame to reduce memory usage
    height, width = frame.shape[:2]
    if width > 640:  # Limit frame width for performance
        scale = 640 / width
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Convert frame to base64 for web display (with compression)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # 70% quality for smaller size
    _, buffer = cv2.imencode('.jpg', frame, encode_param)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Log memory usage
    log_memory_usage()
    
    # Detect players using Roboflow model ONLY
    players = []
    
    print(f"🎯 Starting Roboflow hockey player detection...")
    print(f"   Frame size: {frame.shape[1]}x{frame.shape[0]}")
    print(f"   INFERENCE_AVAILABLE: {INFERENCE_AVAILABLE}")
    
    if INFERENCE_AVAILABLE:
        try:
            print(f"   Getting Roboflow detector...")
            detector = get_inference_detector()
            print(f"   Detector type: {type(detector)}")
            
            print(f"   Calling Roboflow detect_players_in_frame...")
            inference_players = detector.detect_players_in_frame(frame)
            print(f"   Raw Roboflow results: {inference_players}")
            
            for i, player in enumerate(inference_players):
                players.append({
                    'id': i,
                    'bbox': player['bbox'],
                    'confidence': player['confidence']
                })
            
            print(f"🎯 Roboflow detected {len(players)} hockey players")
            
        except Exception as e:
            print(f"❌ Roboflow detection error: {e}")
            import traceback
            traceback.print_exc()
            print("⚠️  Roboflow model failed - no fallback available")
    else:
        print("❌ Roboflow model not available")
    
    # Clear memory after processing
    clear_memory()
    
    return jsonify({
        'frame': frame_base64,
        'width': frame.shape[1],
        'height': frame.shape[0],
        'players': players
    })

@app.route('/process_stride_analysis', methods=['POST'])
def process_stride_analysis():
    """Process stride analysis with selected player coordinates"""
    data = request.get_json()
    filename = data.get('filename')
    player_bbox = data.get('player_bbox')
    
    if not filename or not player_bbox:
        return jsonify({'error': 'Missing filename or player bbox'}), 400
    
    try:
        print(f"🏒 Processing stride analysis for {filename} with bbox {player_bbox}")
        
        # Use the properly fixed analyze_stride function instead of custom processing
        result = analyze_stride(filename, player_bbox)
        
        if isinstance(result, tuple):
            # If analyze_stride returned an error response
            return result
        
        # If analyze_stride succeeded, return success
        return jsonify({
            'success': True,
            'message': 'Stride analysis completed successfully',
            'results': [
                {
                    'name': os.path.basename(result.get('output_video_path', '')),
                    'type': 'video',
                    'description': 'Annotated video with stride analysis and speed tracking',
                    'preview': True,
                    'download': True
                },
                {
                    'name': os.path.basename(result.get('csv_path', '')),
                    'type': 'csv',
                    'description': 'Stride metrics and biomechanics data',
                    'preview': False,
                    'download': True
                },
                {
                    'name': os.path.basename(result.get('skeleton_video_path', '')),
                    'type': 'video',
                    'description': 'Stride skeleton animation video',
                    'preview': True,
                    'download': True
                }
            ]
        })
        
    except Exception as e:
        print(f"❌ Stride analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Stride analysis failed: {str(e)}'}), 500

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    try:
        a_coords = np.array([a['x'], a['y']])
        b_coords = np.array([b['x'], b['y']])
        c_coords = np.array([c['x'], c['y']])
        
        radians = np.arctan2(c_coords[1] - b_coords[1], c_coords[0] - b_coords[0]) - np.arctan2(a_coords[1] - b_coords[1], a_coords[0] - b_coords[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    except:
        return None

def create_stride_skeleton_frame(player_data, width, height):
    """Create stride skeleton frame with Roboflow keypoints"""
    # Create white background with grid
    skeleton_frame = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw grid lines
    grid_size = 50
    for x in range(0, width, grid_size):
        cv2.line(skeleton_frame, (x, 0), (x, height), (200, 200, 200), 1)
    for y in range(0, height, grid_size):
        cv2.line(skeleton_frame, (0, y), (width, y), (200, 200, 200), 1)
    
    # Draw Roboflow keypoints and connections
    if 'keypoints' in player_data:
        keypoints = player_data['keypoints']
        
        # Draw keypoints as circles
        for kp in keypoints:
            x = int(kp.get('x', 0))
            y = int(kp.get('y', 0))
            confidence = kp.get('confidence', 0)
            
            # Color based on confidence
            if confidence > 0.7:
                color = (0, 255, 0)  # Green for high confidence
            elif confidence > 0.4:
                color = (0, 255, 255)  # Yellow for medium confidence
            else:
                color = (0, 0, 255)  # Red for low confidence
            
            cv2.circle(skeleton_frame, (x, y), 4, color, -1)
        
        # Draw basic connections between keypoints (if we have enough)
        if len(keypoints) >= 2:
            # Draw lines between consecutive keypoints
            for i in range(len(keypoints) - 1):
                pt1 = (int(keypoints[i]['x']), int(keypoints[i]['y']))
                pt2 = (int(keypoints[i+1]['x']), int(keypoints[i+1]['y']))
                cv2.line(skeleton_frame, pt1, pt2, (0, 0, 255), 2)
    
    return skeleton_frame

def create_blank_grid_frame(width, height):
    """Create blank white frame with grid"""
    frame = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw grid lines
    grid_size = 50
    for x in range(0, width, grid_size):
        cv2.line(frame, (x, 0), (x, height), (200, 200, 200), 1)
    for y in range(0, height, grid_size):
        cv2.line(frame, (0, y), (width, y), (200, 200, 200), 1)
    
    return frame

def process_video_frame_by_frame(video_path, player_bbox, fps, width, height):
    """Process video frame by frame as fallback when Roboflow video inference is too slow"""
    print(f"🎬 Processing video frame by frame...")
    
    # Get target player info
    target_center = (player_bbox[0] + player_bbox[2]/2, player_bbox[1] + player_bbox[3]/2)
    target_width = player_bbox[2]
    target_height = player_bbox[3]
    
    print(f"🎯 Target player: center={target_center}, size={target_width}x{target_height}")
    
    # Initialize detector
    detector = get_inference_detector()
    detections = []
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    # Sample every 3rd frame for performance (10 FPS equivalent)
    sample_rate = 3
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Only process every 3rd frame for performance
        if frame_count % sample_rate != 0:
            continue
        
        # Detect players in this frame
        try:
            frame_players = detector.detect_players_in_frame(frame)
            
            if frame_players:
                # Find the best match for our target player
                best_match = None
                best_score = 0
                
                for player in frame_players:
                    if 'bbox' in player:
                        bbox = player['bbox']
                        player_center = (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)
                        
                        # Calculate similarity score
                        distance = np.sqrt((player_center[0] - target_center[0])**2 + 
                                         (player_center[1] - target_center[1])**2)
                        distance_score = max(0, 100 - distance)
                        
                        size_diff = abs(bbox[2] - target_width) + abs(bbox[3] - target_height)
                        size_score = max(0, 50 - size_diff/2)
                        
                        total_score = distance_score + size_score
                        
                        if total_score > best_score:
                            best_score = total_score
                            best_match = player
                
                # If we found a good match, add it to detections
                if best_match and best_score > 30:
                    detections.append({
                        'frame': frame_count,
                        'bbox': best_match['bbox'],
                        'confidence': best_match.get('confidence', 0.5),
                        'center': (best_match['bbox'][0] + best_match['bbox'][2]/2, 
                                 best_match['bbox'][1] + best_match['bbox'][3]/2),
                        'keypoints': best_match.get('keypoints', [])
                    })
                    
                    if frame_count % 30 == 0:  # Log every 30 processed frames
                        print(f"   Frame {frame_count}: Player detected (score: {best_score:.1f})")
        
        except Exception as e:
            if frame_count % 30 == 0:
                print(f"   Frame {frame_count}: Detection error: {e}")
    
    cap.release()
    
    print(f"✅ Frame-by-frame processing complete: {len(detections)} detections across {frame_count} frames")
    return detections

@app.route('/clear_memory')
def clear_memory_endpoint():
    """Clear memory to improve performance"""
    try:
        clear_memory()
        log_memory_usage()
        return jsonify({'success': True, 'message': 'Memory cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/memory_status')
def memory_status():
    """Get current memory usage"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        return jsonify({
            'success': True,
            'memory_mb': round(memory_info.rss / 1024 / 1024, 1),
            'memory_percent': process.memory_percent()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/view/<filename>')
def view_file(filename):
    """View output files"""
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(file_path):
        if filename.endswith('.csv'):
            # For CSV files, return as text
            with open(file_path, 'r') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/plain'}
        elif filename.endswith(('.mp4', '.avi', '.mov')):
            # For video files, return as video
            return send_file(file_path, mimetype='video/mp4')
        else:
            # For other files, return as binary
            return send_file(file_path)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/download/<filename>')
def download_file(filename):
    """Download output files"""
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/files')
def list_files():
    """List all output files"""
    files = []
    output_dir = app.config['OUTPUT_FOLDER']
    
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path):
            files.append({
                'name': filename,
                'size': os.path.getsize(file_path),
                'type': filename.split('_')[0] if '_' in filename else 'unknown'
            })
    
    return jsonify(files)

if __name__ == '__main__':
    port = 8237
    print(f"🏒 Stride Analysis App starting on port {port}")
    print(f"   Roboflow model only - no YOLO fallback")
    app.run(debug=False, host='127.0.0.1', port=port, threaded=True)

from flask import Flask, render_template, request, jsonify, send_file
import os
import cv2
import numpy as np
import base64
from werkzeug.utils import secure_filename
import gc
import psutil
import mediapipe as mp
import pandas as pd
from datetime import datetime

# Initialize MediaPipe only
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

app = Flask(__name__)
print("🏋️ OFF-ICE ANALYSIS APP STARTING - MEDIAPIPE ONLY! 🏋️")
print("   Port: 8238 | Focus: General person detection & exercise analysis")

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
    
    if analysis_type == 'motion_capture':
        return analyze_motion_capture(filename)
    else:
        return jsonify({'error': 'Invalid analysis type'}), 400

def analyze_motion_capture(filename):
    """Off-ice analysis - requires person selection first"""
    try:
        print(f"🏋️ Motion capture analysis requested for: {filename}")
        
        # Generate output filenames
        base_name = os.path.splitext(filename)[0]
        output_csv = f"off_ice_metrics_{base_name}.csv"
        output_video = f"off_ice_analysis_{filename}"
        output_skeleton = f"off_ice_skeleton_{base_name}.mp4"
        
        print(f"✅ Motion capture analysis ready - waiting for person selection")
        print(f"🎯 Note: Off-ice analysis uses MediaPipe general person detection")
        
        return {
            'success': True,
            'analysis_id': 'motion_capture',
            'analysis_type': 'motion_capture',
            'message': 'Off-ice analysis requires person selection using MediaPipe detection. Use the interactive interface below.',
            'requires_interaction': True,
            'video_filename': filename,
            'results': [
                {
                    'name': output_csv,
                    'type': 'csv',
                    'description': 'Complete off-ice exercise data with joint trajectories',
                    'preview': False,
                    'download': True
                },
                {
                    'name': output_video,
                    'type': 'video',
                    'description': 'Annotated video with off-ice motion tracking',
                    'preview': True,
                    'download': True
                },
                {
                    'name': output_skeleton,
                    'type': 'video',
                    'description': 'Off-ice skeleton animation video',
                    'preview': True,
                    'download': True
                }
            ]
        }
        
    except Exception as e:
        print(f"❌ Error in motion capture analysis: {e}")
        return {
            'success': False,
            'analysis_id': 'motion_capture',
            'analysis_type': 'motion_capture',
            'message': f'Motion capture analysis failed: {str(e)}',
            'requires_interaction': False,
            'video_filename': filename,
            'results': []
        }

@app.route('/detect_people/<filename>')
def detect_people(filename):
    """Detect people using MediaPipe pose detection"""
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
    
    # Detect people using MediaPipe pose detection
    people = []
    
    print(f"🎯 Starting MediaPipe person detection...")
    print(f"   Frame size: {frame.shape[1]}x{frame.shape[0]}")
    
    try:
        # Initialize MediaPipe pose detection
        pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = pose.process(rgb_frame)
        
        if results.pose_landmarks:
            # Get bounding box from pose landmarks
            h, w, _ = frame.shape
            landmarks = results.pose_landmarks.landmark
            
            # Calculate bounding box from pose landmarks
            x_coords = [landmark.x * w for landmark in landmarks]
            y_coords = [landmark.y * h for landmark in landmarks]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # Add padding to bounding box
            padding = 20
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(w, x_max + padding)
            y_max = min(h, y_max + padding)
            
            people.append({
                'id': 0,
                'bbox': [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)],
                'confidence': 0.9,
                'type': 'person',
                'landmarks': len(landmarks)
            })
            
            print(f"🎯 MediaPipe detected 1 person with {len(landmarks)} landmarks")
        else:
            print(f"⚠️  No pose landmarks detected")
            
        # Clean up
        pose.close()
        
    except Exception as e:
        print(f"❌ MediaPipe detection error: {e}")
        import traceback
        traceback.print_exc()
    
    # Clear memory after processing
    clear_memory()
    
    return jsonify({
        'frame': frame_base64,
        'width': frame.shape[1],
        'height': frame.shape[0],
        'people': people
    })

@app.route('/process_motion_capture', methods=['POST'])
def process_motion_capture():
    """Process motion capture analysis with selected person coordinates"""
    data = request.get_json()
    filename = data.get('filename')
    person_bbox = data.get('person_bbox')
    
    if not filename or not person_bbox:
        return jsonify({'error': 'Missing filename or person bbox'}), 400
    
    try:
        print(f"🏋️ Processing motion capture analysis for {filename} with bbox {person_bbox}")
        
        # Generate output filenames
        base_name = os.path.splitext(filename)[0]
        output_video = f"off_ice_analysis_{filename}"
        output_csv = f"off_ice_metrics_{base_name}.csv"
        output_skeleton = f"off_ice_skeleton_{base_name}.mp4"
        
        # Process the video with MediaPipe pose detection
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Initialize MediaPipe pose detection
        pose = mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Prepare output video writers
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], output_video)
        skeleton_video_path = os.path.join(app.config['OUTPUT_FOLDER'], output_skeleton)
        
        out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        skeleton_out = cv2.VideoWriter(skeleton_video_path, fourcc, fps, (width, height))
        
        # Prepare CSV data
        joint_data = []
        frame_count = 0
        
        print(f"🎬 Processing {total_frames} frames for motion capture...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            if frame_count % 30 == 0:  # Log every 30 frames
                print(f"   Processing frame {frame_count}/{total_frames}")
            
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            results = pose.process(rgb_frame)
            
            # Create frame data for CSV
            frame_data = {
                'frame': frame_count,
                'timestamp': frame_count / fps,
                'frame_time': datetime.now().isoformat()
            }
            
            if results.pose_landmarks:
                # Extract all 33 pose landmarks
                landmarks = results.pose_landmarks.landmark
                
                # Add each landmark to frame data
                for i, landmark in enumerate(landmarks):
                    joint_name = mp_pose.PoseLandmark(i).name.lower()
                    frame_data[f'{joint_name}_x'] = landmark.x
                    frame_data[f'{joint_name}_y'] = landmark.y
                    frame_data[f'{joint_name}_z'] = landmark.z
                    frame_data[f'{joint_name}_visibility'] = landmark.visibility
                
                # Calculate additional metrics
                # Hip center (average of left and right hip)
                left_hip = landmarks[23]
                right_hip = landmarks[24]
                hip_center_x = (left_hip.x + right_hip.x) / 2
                hip_center_y = (left_hip.y + right_hip.y) / 2
                
                # Shoulder center
                left_shoulder = landmarks[11]
                right_shoulder = landmarks[12]
                shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
                shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
                
                # Add calculated metrics
                frame_data['hip_center_x'] = hip_center_x
                frame_data['hip_center_y'] = hip_center_y
                frame_data['shoulder_center_x'] = shoulder_center_x
                frame_data['shoulder_center_y'] = shoulder_center_y
                
                # Calculate spine length
                spine_length = np.sqrt((shoulder_center_x - hip_center_x)**2 + (shoulder_center_y - hip_center_y)**2)
                frame_data['spine_length'] = spine_length
                
                # Calculate arm angles
                left_elbow = landmarks[13]
                left_wrist = landmarks[15]
                left_shoulder = landmarks[11]
                
                # Left arm angle
                left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                frame_data['left_arm_angle'] = left_arm_angle
                
                # Right arm angle
                right_elbow = landmarks[14]
                right_wrist = landmarks[16]
                right_shoulder = landmarks[12]
                right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                frame_data['right_arm_angle'] = right_arm_angle
                
                # Calculate leg angles
                left_knee = landmarks[25]
                left_ankle = landmarks[27]
                left_hip = landmarks[23]
                left_leg_angle = calculate_angle(left_hip, left_knee, left_ankle)
                frame_data['left_leg_angle'] = left_leg_angle
                
                right_knee = landmarks[26]
                right_ankle = landmarks[28]
                right_hip = landmarks[24]
                right_leg_angle = calculate_angle(right_hip, right_knee, right_ankle)
                frame_data['right_leg_angle'] = right_leg_angle
                
                # Draw pose landmarks on frame
                annotated_frame = frame.copy()
                mp_drawing.draw_landmarks(
                    annotated_frame, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
                
                # Create skeleton frame
                skeleton_frame = create_skeleton_frame(results.pose_landmarks, width, height)
                
                # Write frames to output videos
                out_video.write(annotated_frame)
                skeleton_out.write(skeleton_frame)
                
            else:
                # No pose detected - add empty values
                for i in range(33):
                    joint_name = mp_pose.PoseLandmark(i).name.lower()
                    frame_data[f'{joint_name}_x'] = None
                    frame_data[f'{joint_name}_y'] = None
                    frame_data[f'{joint_name}_z'] = None
                    frame_data[f'{joint_name}_visibility'] = None
                
                # Add empty calculated metrics
                frame_data.update({
                    'hip_center_x': None, 'hip_center_y': None,
                    'shoulder_center_x': None, 'shoulder_center_y': None,
                    'spine_length': None, 'left_arm_angle': None,
                    'right_arm_angle': None, 'left_leg_angle': None,
                    'right_leg_angle': None
                })
                
                # Write original frame to output videos
                out_video.write(frame)
                skeleton_out.write(create_blank_grid_frame(width, height))
            
            joint_data.append(frame_data)
        
        # Clean up
        cap.release()
        out_video.release()
        skeleton_out.release()
        pose.close()
        
        # Save CSV data
        df = pd.DataFrame(joint_data)
        csv_path = os.path.join(app.config['OUTPUT_FOLDER'], output_csv)
        df.to_csv(csv_path, index=False)
        
        print(f"✅ Motion capture analysis completed!")
        print(f"   CSV saved: {csv_path}")
        print(f"   Annotated video: {output_video_path}")
        print(f"   Skeleton video: {skeleton_video_path}")
        
        return jsonify({
            'success': True,
            'message': 'Off-ice motion capture analysis completed successfully!',
            'results': [
                {
                    'name': output_video,
                    'type': 'video',
                    'description': 'Annotated video with off-ice motion tracking and joint analysis',
                    'preview': True,
                    'download': True
                },
                {
                    'name': output_csv,
                    'type': 'csv',
                    'description': 'Complete exercise metrics and joint trajectory data',
                    'preview': False,
                    'download': True
                },
                {
                    'name': output_skeleton,
                    'type': 'video',
                    'description': 'Off-ice skeleton animation video',
                    'preview': True,
                    'download': True
                }
            ]
        })
        
    except Exception as e:
        print(f"❌ Error processing motion capture analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    try:
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    except:
        return None

def create_skeleton_frame(pose_landmarks, width, height):
    """Create skeleton-only frame on white gridded background"""
    # Create white background with grid
    skeleton_frame = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw grid lines
    grid_size = 50
    for x in range(0, width, grid_size):
        cv2.line(skeleton_frame, (x, 0), (x, height), (200, 200, 200), 1)
    for y in range(0, height, grid_size):
        cv2.line(skeleton_frame, (0, y), (width, y), (200, 200, 200), 1)
    
    # Draw pose landmarks and connections
    if pose_landmarks:
        # Draw landmarks as circles
        for landmark in pose_landmarks.landmark:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(skeleton_frame, (x, y), 4, (0, 255, 0), -1)
        
        # Draw pose connections
        mp_drawing.draw_landmarks(
            skeleton_frame, 
            pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=0),
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=0)
        )
    
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
    port = 8238
    print(f"🏋️ Off-Ice Analysis App starting on port {port}")
    print(f"   MediaPipe pose detection only - lightweight and fast")
    app.run(debug=False, host='127.0.0.1', port=port, threaded=True)

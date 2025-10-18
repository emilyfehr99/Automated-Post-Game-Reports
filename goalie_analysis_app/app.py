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

# Initialize MediaPipe for goalie tracking
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

app = Flask(__name__)
print("🥅 GOALIE ANALYSIS APP STARTING - SPECIALIZED TRACKING! 🥅")
print("   Port: 8239 | Focus: Goalie movement & save mechanics")

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
    
    if analysis_type == 'goalie':
        return analyze_goalie(filename)
    else:
        return jsonify({'error': 'Invalid analysis type'}), 400

def analyze_goalie(filename):
    """Goalie biomechanics analysis"""
    try:
        print(f"🥅 Goalie analysis requested for: {filename}")
        
        # Generate output filenames
        base_name = os.path.splitext(filename)[0]
        output_video = f"goalie_annotated_{filename}"
        output_csv = f"goalie_metrics_{base_name}.csv"
        
        print(f"✅ Goalie analysis ready - waiting for goalie selection")
        print(f"🎯 Note: Goalie analysis uses specialized tracking algorithms")
        
        return {
            'success': True,
            'analysis_id': 'goalie',
            'analysis_type': 'goalie',
            'message': 'Goalie analysis requires goalie selection using specialized tracking. Use the interactive interface below.',
            'requires_interaction': True,
            'video_filename': filename,
            'results': [
                {
                    'name': output_csv,
                    'type': 'csv',
                    'description': 'Goalie movement metrics, save mechanics, and positioning data',
                    'preview': False,
                    'download': True
                },
                {
                    'name': output_video,
                    'type': 'video',
                    'description': 'Annotated video with goalie tracking and analysis',
                    'preview': True,
                    'download': True
                }
            ]
        }
        
    except Exception as e:
        print(f"❌ Error in goalie analysis: {e}")
        return {
            'success': False,
            'analysis_id': 'goalie',
            'analysis_type': 'goalie',
            'message': f'Goalie analysis failed: {str(e)}',
            'requires_interaction': False,
            'video_filename': filename,
            'results': []
        }

@app.route('/detect_goalie/<filename>')
def detect_goalie(filename):
    """Detect goalie using specialized tracking algorithms"""
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
    
    # Detect goalie using MediaPipe pose detection (specialized for goalie tracking)
    goalies = []
    
    print(f"🎯 Starting goalie detection...")
    print(f"   Frame size: {frame.shape[1]}x{frame.shape[0]}")
    
    try:
        # Initialize MediaPipe pose detection for goalie tracking
        pose = mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
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
            padding = 30
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(w, x_max + padding)
            y_max = min(h, y_max + padding)
            
            goalies.append({
                'id': 0,
                'bbox': [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)],
                'confidence': 0.9,
                'type': 'goalie',
                'landmarks': len(landmarks)
            })
            
            print(f"🎯 Goalie detected with {len(landmarks)} pose landmarks")
        else:
            print(f"⚠️  No goalie pose landmarks detected")
            
        # Clean up
        pose.close()
        
    except Exception as e:
        print(f"❌ Goalie detection error: {e}")
        import traceback
        traceback.print_exc()
    
    # Clear memory after processing
    clear_memory()
    
    return jsonify({
        'frame': frame_base64,
        'width': frame.shape[1],
        'height': frame.shape[0],
        'goalies': goalies
    })

@app.route('/process_goalie_analysis', methods=['POST'])
def process_goalie_analysis():
    """Process goalie analysis with selected goalie coordinates"""
    data = request.get_json()
    filename = data.get('filename')
    goalie_bbox = data.get('goalie_bbox')
    
    if not filename or not goalie_bbox:
        return jsonify({'error': 'Missing filename or goalie bbox'}), 400
    
    try:
        print(f"🥅 Processing goalie analysis for {filename} with bbox {goalie_bbox}")
        
        # Generate output filenames
        base_name = os.path.splitext(filename)[0]
        output_video = f"goalie_annotated_{filename}"
        output_csv = f"goalie_metrics_{base_name}.csv"
        
        # Process the video with goalie analysis
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Initialize MediaPipe pose detection for goalie tracking
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
        
        # Prepare output video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], output_video)
        out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        # Prepare CSV data for goalie analysis
        joint_data = []
        frame_count = 0
        
        # Goalie tracking variables
        goalie_positions = []
        movement_distances = []
        save_attempts = []
        positioning_metrics = []
        
        print(f"🎬 Processing {total_frames} frames for goalie analysis...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            if frame_count % 30 == 0:  # Log every 30 frames
                print(f"   Processing frame {frame_count}/{total_frames}")
            
            # Create frame data for CSV
            frame_data = {
                'frame': frame_count,
                'timestamp': frame_count / fps,
                'frame_time': datetime.now().isoformat()
            }
            
            # Extract goalie region based on bbox
            x, y, w, h = goalie_bbox
            
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            results = pose.process(rgb_frame)
            
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
                
                # Calculate goalie-specific metrics
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
                
                # Calculate goalie positioning metrics
                # Distance from center of frame (assuming goalie should be centered)
                frame_center_x = 0.5
                frame_center_y = 0.5
                goalie_center_x = hip_center_x
                goalie_center_y = hip_center_y
                
                distance_from_center = np.sqrt((goalie_center_x - frame_center_x)**2 + (goalie_center_y - frame_center_y)**2)
                frame_data['distance_from_center'] = distance_from_center
                
                # Calculate goalie stance width
                left_ankle = landmarks[27]
                right_ankle = landmarks[28]
                stance_width = np.sqrt((left_ankle.x - right_ankle.x)**2 + (left_ankle.y - right_ankle.y)**2)
                frame_data['stance_width'] = stance_width
                
                # Calculate goalie height (shoulder to hip)
                goalie_height = np.sqrt((shoulder_center_x - hip_center_x)**2 + (shoulder_center_y - hip_center_y)**2)
                frame_data['goalie_height'] = goalie_height
                
                # Calculate arm angles for save mechanics
                left_elbow = landmarks[13]
                left_wrist = landmarks[15]
                left_shoulder = landmarks[11]
                left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                frame_data['left_arm_angle'] = left_arm_angle
                
                right_elbow = landmarks[14]
                right_wrist = landmarks[16]
                right_shoulder = landmarks[12]
                right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                frame_data['right_arm_angle'] = right_arm_angle
                
                # Calculate leg angles for movement analysis
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
                
                # Track goalie movement
                goalie_positions.append((hip_center_x, hip_center_y))
                if len(goalie_positions) > 1:
                    # Calculate movement distance
                    prev_pos = goalie_positions[-2]
                    curr_pos = goalie_positions[-1]
                    movement_distance = np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)
                    movement_distances.append(movement_distance)
                    frame_data['movement_distance'] = movement_distance
                    
                    # Calculate movement speed
                    movement_speed = movement_distance * fps
                    frame_data['movement_speed'] = movement_speed
                
                # Detect save attempts (when arms are extended)
                left_arm_extended = left_arm_angle > 150 if left_arm_angle else False
                right_arm_extended = right_arm_angle > 150 if right_arm_angle else False
                
                if left_arm_extended or right_arm_extended:
                    save_attempts.append(frame_count)
                    frame_data['save_attempt'] = True
                    frame_data['save_arm'] = 'left' if left_arm_extended else 'right'
                else:
                    frame_data['save_attempt'] = False
                    frame_data['save_arm'] = None
                
                # Calculate positioning efficiency
                # Goalie should maintain good stance width and height
                optimal_stance_width = 0.3  # Normalized value
                optimal_height = 0.4  # Normalized value
                
                stance_efficiency = 1 - abs(stance_width - optimal_stance_width) / optimal_stance_width
                height_efficiency = 1 - abs(goalie_height - optimal_height) / optimal_height
                
                frame_data['stance_efficiency'] = max(0, stance_efficiency)
                frame_data['height_efficiency'] = max(0, height_efficiency)
                frame_data['overall_positioning_score'] = (stance_efficiency + height_efficiency) / 2
                
                # Draw goalie analysis on frame
                annotated_frame = frame.copy()
                cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(annotated_frame, f'Goalie Analysis', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Draw key metrics
                if 'movement_speed' in frame_data:
                    cv2.putText(annotated_frame, f'Speed: {frame_data["movement_speed"]:.2f}', 
                               (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                if 'stance_width' in frame_data:
                    cv2.putText(annotated_frame, f'Stance: {frame_data["stance_width"]:.3f}', 
                               (x, y+h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                if 'overall_positioning_score' in frame_data:
                    score = frame_data['overall_positioning_score']
                    color = (0, 255, 0) if score > 0.7 else (0, 255, 255) if score > 0.5 else (0, 0, 255)
                    cv2.putText(annotated_frame, f'Position: {score:.2f}', 
                               (x, y+h+60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                if 'save_attempt' in frame_data and frame_data['save_attempt']:
                    cv2.putText(annotated_frame, f'SAVE ATTEMPT!', 
                               (x+50, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 3)
                
                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    annotated_frame, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
                
                # Write frame to output video
                out_video.write(annotated_frame)
                
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
                    'spine_length': None, 'distance_from_center': None,
                    'stance_width': None, 'goalie_height': None,
                    'left_arm_angle': None, 'right_arm_angle': None,
                    'left_leg_angle': None, 'right_leg_angle': None,
                    'movement_distance': None, 'movement_speed': None,
                    'save_attempt': None, 'save_arm': None,
                    'stance_efficiency': None, 'height_efficiency': None,
                    'overall_positioning_score': None
                })
                
                # Write original frame to output video
                out_video.write(frame)
            
            joint_data.append(frame_data)
        
        # Clean up
        cap.release()
        out_video.release()
        pose.close()
        
        # Save CSV data
        df = pd.DataFrame(joint_data)
        csv_path = os.path.join(app.config['OUTPUT_FOLDER'], output_csv)
        df.to_csv(csv_path, index=False)
        
        # Calculate summary statistics
        summary_stats = {
            'total_frames': total_frames,
            'total_save_attempts': len(save_attempts),
            'avg_movement_speed': np.mean(movement_distances) if movement_distances else 0,
            'avg_positioning_score': np.mean([d['overall_positioning_score'] for d in joint_data if d['overall_positioning_score'] is not None]) if joint_data else 0,
            'total_movement_distance': sum(movement_distances) if movement_distances else 0
        }
        
        print(f"✅ Goalie analysis completed!")
        print(f"   Total save attempts: {summary_stats['total_save_attempts']}")
        print(f"   Average movement speed: {summary_stats['avg_movement_speed']:.3f}")
        print(f"   Average positioning score: {summary_stats['avg_positioning_score']:.2f}")
        print(f"   Total movement distance: {summary_stats['total_movement_distance']:.3f}")
        print(f"   CSV saved: {csv_path}")
        print(f"   Annotated video: {output_video_path}")
        
        return jsonify({
            'success': True,
            'message': 'Goalie analysis completed successfully!',
            'summary_stats': summary_stats,
            'results': [
                {
                    'name': output_video,
                    'type': 'video',
                    'description': 'Annotated video with goalie tracking, save mechanics, and positioning analysis',
                    'preview': True,
                    'download': True
                },
                {
                    'name': output_csv,
                    'type': 'csv',
                    'description': 'Complete goalie metrics including movement patterns, save efficiency, and positioning data',
                    'preview': False,
                    'download': True
                }
            ]
        })
        
    except Exception as e:
        print(f"❌ Error processing goalie analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    try:
        a_coords = np.array([a.x, a.y])
        b_coords = np.array([b.x, b.y])
        c_coords = np.array([c.x, c.y])
        
        radians = np.arctan2(c_coords[1] - b_coords[1], c_coords[0] - b_coords[0]) - np.arctan2(a_coords[1] - b_coords[1], a_coords[0] - b_coords[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    except:
        return None

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
    port = 8239
    print(f"🥅 Goalie Analysis App starting on port {port}")
    print(f"   Specialized goalie tracking algorithms - optimized for hockey")
    app.run(debug=False, host='127.0.0.1', port=port, threaded=True)

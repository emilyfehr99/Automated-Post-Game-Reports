import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
import os
import sys
import time
import threading
from functools import lru_cache

# Import Roboflow InferencePipeline for custom workflow
try:
    from inference import InferencePipeline
    INFERENCE_AVAILABLE = True
    print("✅ Roboflow InferencePipeline available")
except ImportError:
    INFERENCE_AVAILABLE = False
    print("❌ InferencePipeline not available. Install with: pip install inference")

class OptimizedRoboflowPlayerDetector:
    """Optimized Roboflow InferencePipeline hockey player detector using custom-workflow-4"""
    
    def __init__(self, api_key: str, workspace_name: str, workflow_id: str):
        self.api_key = api_key
        self.workspace_name = workspace_name
        self.workflow_id = workflow_id
        
        # Performance optimizations
        self._pipeline = None
        self._pipeline_ready = False
        self._loading_lock = threading.Lock()
        self._last_detection_time = 0
        self._detection_cache = {}
        self._cache_ttl = 30.0  # Cache results for 30 seconds
        
        if INFERENCE_AVAILABLE:
            self._initialize_pipeline_async()
    
    def _initialize_pipeline_async(self):
        """Initialize the Roboflow InferencePipeline asynchronously"""
        def load_pipeline():
            try:
                print(f"🚀 Initializing Roboflow InferencePipeline...")
                print(f"   API Key: {self.api_key[:8]}...")
                print(f"   Workspace: {self.workspace_name}")
                print(f"   Workflow: {self.workflow_id}")
                
                # Initialize InferencePipeline
                self._pipeline = InferencePipeline.init_with_workflow(
                    api_key=self.api_key,
                    workspace_name=self.workspace_name,
                    workflow_id=self.workflow_id,
                    video_reference=0,  # Will be set per video
                    max_fps=30,
                    on_prediction=self._handle_prediction
                )
                
                print(f"   Pipeline initialized successfully: {self._pipeline}")
                self._pipeline_ready = True
                print(f"✅ Roboflow InferencePipeline initialized successfully!")
                
            except Exception as e:
                print(f"❌ Failed to initialize InferencePipeline: {e}")
                print(f"   Exception type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                self._pipeline_ready = False
        
        # Start loading in background thread
        thread = threading.Thread(target=load_pipeline, daemon=True)
        thread.start()
    
    def _handle_prediction(self, result, video_frame):
        """Handle predictions from the InferencePipeline"""
        # This will be called for each frame processed
        # Store the result for later use
        if hasattr(self, '_current_predictions'):
            self._current_predictions.append(result)
    
    def _wait_for_pipeline(self, timeout: float = 30.0) -> bool:
        """Wait for pipeline to be ready with timeout"""
        start_time = time.time()
        while not self._pipeline_ready and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        return self._pipeline_ready
    
    def _get_cached_detection(self, cache_key: str) -> Optional[List[Dict]]:
        """Get cached detection result if still valid"""
        if cache_key in self._detection_cache:
            cache_time, result = self._detection_cache[cache_key]
            if time.time() - cache_time < self._cache_ttl:
                return result
            else:
                # Remove expired cache entry
                del self._detection_cache[cache_key]
        return None
    
    def _cache_detection(self, cache_key: str, result: List[Dict]):
        """Cache detection result with timestamp"""
        self._detection_cache[cache_key] = (time.time(), result)
        
        # Limit cache size to prevent memory issues
        if len(self._detection_cache) > 20:  # Reduced cache size for hosted inference
            # Remove oldest entries
            oldest_key = min(self._detection_cache.keys(), 
                           key=lambda k: self._detection_cache[k][0])
            del self._detection_cache[oldest_key]
    
    def detect_players_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect hockey players in a single frame using video frame detection
        
        Args:
            frame: OpenCV frame (BGR format) - should be a frame from the video
            
        Returns:
            List of player detections with bounding boxes and confidence scores
        """
        if not INFERENCE_AVAILABLE:
            print("❌ Roboflow InferencePipeline not available")
            return []
        
        # Check if we have a valid pipeline
        if self.workflow_id == "NO_WORKFLOW_FOUND":
            print("❌ No valid Roboflow workflow found. Please check your workspace for correct workflow IDs.")
            print("   You can find workflow IDs in your Roboflow dashboard under 'Workflows' section.")
            return []
        
        # For single frame detection, we'll use a simple cache key
        # This is mainly for the player selection modal
        frame_hash = f"frame_{hash(str(frame.shape))}"
        cached_result = self._get_cached_detection(frame_hash)
        if cached_result is not None:
            print(f"⚡ Using cached frame detection result ({len(cached_result)} players)")
            return cached_result
        
        # For video frames, we'll use the video inference approach
        # Save frame and run inference using the video model
        try:
            temp_path = f"temp_frame_{int(time.time())}.jpg"
            cv2.imwrite(temp_path, frame)
            
            if not self._wait_for_pipeline():
                print("❌ Pipeline failed to load within timeout")
                return []
            
            print(f"🎯 Running Roboflow detection on video frame...")
            print(f"   Frame shape: {frame.shape}")
            print(f"   Temp path: {temp_path}")
            print(f"   Pipeline ready: {self._pipeline_ready}")
            print(f"   Pipeline object: {self._pipeline}")
            start_time = time.time()
            
            # Use InferencePipeline for video frame
            if self._pipeline and self._pipeline_ready:
                print(f"   Calling pipeline.predict() on video frame...")
                
                # For video frames, we can use image prediction with video-optimized settings
                # Use the model's default confidence threshold (40) and overlap (30)
                result = self._pipeline.predict(temp_path)
                
                detection_time = time.time() - start_time
                print(f"⚡ Video frame detection completed in {detection_time:.3f}s")
                print(f"   Raw result: {result}")
                print(f"   Result type: {type(result)}")
                
                if result:
                    print(f"   Result has predictions: {hasattr(result, 'predictions')}")
                    if hasattr(result, 'predictions'):
                        print(f"   Predictions: {result.predictions}")
                    print(f"   Result keys: {result.keys() if hasattr(result, 'keys') else 'No keys'}")
                    
                    # Try to access the result as a list or dict
                    if hasattr(result, '__len__'):
                        print(f"   Result length: {len(result)}")
                    if hasattr(result, '__iter__'):
                        print(f"   Result is iterable")
                        try:
                            for i, item in enumerate(result):
                                print(f"   Item {i}: {item}")
                                if hasattr(item, 'keys'):
                                    print(f"     Item keys: {item.keys()}")
                        except Exception as e:
                            print(f"     Error iterating: {e}")
                    
                    players = self._extract_players_from_prediction(result)
                    print(f"✅ Extracted {len(players)} players from video frame")
                    
                    # Cache the result
                    self._cache_detection(frame_hash, players)
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    return players
                else:
                    print("⚠️  No predictions from video frame detection")
                    print("   Result is empty or None")
                    return []
            else:
                print(f"❌ Pipeline not ready: ready={self._pipeline_ready}, pipeline={self._pipeline}")
                return []
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return []
                
        except Exception as e:
            print(f"❌ Video frame detection error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def detect_players_in_video(self, video_path: str, max_fps: int = 30) -> List[Dict]:
        """
        Detect hockey players throughout a video using hosted video inference
        
        Args:
            video_path: Path to video file
            max_fps: Maximum FPS for processing
            
        Returns:
            List of player detections with frame information
        """
        if not INFERENCE_AVAILABLE:
            print("❌ Roboflow InferencePipeline not available")
            return []
        
        # Check cache first using video path and FPS as key
        cache_key = f"video_{hash(video_path)}_{max_fps}"
        cached_result = self._get_cached_detection(cache_key)
        if cached_result is not None:
            print(f"⚡ Using cached video detection result ({len(cached_result)} detections)")
            return cached_result
        
        # Wait for pipeline to be ready
        if not self._wait_for_pipeline():
            print("❌ Pipeline failed to load within timeout")
            return []
        
        try:
            print(f"🎬 Running Roboflow InferencePipeline...")
            print(f"   Video: {video_path}")
            print(f"   Target FPS: {max_fps}")
            
            start_time = time.time()
            
            # Use InferencePipeline for video inference
            if self._pipeline:
                print(f"🚀 Starting InferencePipeline...")
                
                # Submit video for processing
                                # The InferencePipeline handles its own video processing and polling
                # We just need to pass the video path and max_fps
                result = self._pipeline.predict_video(
                    video_path,
                    fps=max_fps,
                )
                
                inference_time = time.time() - start_time
                print(f"⚡ InferencePipeline completed in {inference_time:.2f}s")
                
                if result:
                    # Extract all detections from video result
                    video_detections = self._extract_video_detections(result, video_path, max_fps)
                    print(f"✅ Extracted {len(video_detections)} detections from video")
                    
                    # Cache the result
                    self._cache_detection(cache_key, video_detections)
                    
                    return video_detections
                else:
                    print("⚠️  No predictions from InferencePipeline")
                    return []
            else:
                print("❌ Pipeline not available")
                return []
                
        except Exception as e:
            print(f"❌ InferencePipeline error: {e}")
            return []
    
    def _extract_video_detections(self, results, video_path: str, max_fps: int) -> List[Dict]:
        """Extract detections from hosted video inference results"""
        detections = []
        
        try:
            # Get video properties for frame mapping
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            print(f"📹 Video: {fps:.1f} FPS, {total_frames} frames")
            
            # Handle different result formats from hosted inference
            if isinstance(results, dict):
                if 'predictions' in results:
                    predictions = results['predictions']
                elif 'data' in results:
                    predictions = results['data']
                else:
                    predictions = [results]
            else:
                predictions = [results]
            
            if predictions:
                for pred in predictions:
                    # Filter for player class
                    if pred.get('class') in ['player', 'person', 'hockey_player']:
                        # Extract frame information if available
                        frame_num = pred.get('frame', 0)
                        if frame_num == 0:
                            # If no frame info, estimate based on timestamp
                            timestamp = pred.get('timestamp', 0)
                            if timestamp > 0:
                                frame_num = int(timestamp * fps)
                        
                        # Extract bounding box
                        x = pred.get('x', 0)
                        y = pred.get('y', 0)
                        width = pred.get('width', 0)
                        height = pred.get('height', 0)
                        confidence = pred.get('confidence', 0.5)
                        
                        # Convert to OpenCV format [x, y, w, h]
                        bbox = [int(x - width/2), int(y - height/2), int(width), int(height)]
                        
                        detections.append({
                            'frame': frame_num,
                            'bbox': bbox,
                            'confidence': confidence,
                            'center': (int(x), int(y)),
                            'keypoints': self._extract_keypoints(pred)
                        })
                        
                        print(f"🎯 Frame {frame_num}: Player bbox={bbox}, confidence={confidence:.2f}")
            
        except Exception as e:
            print(f"❌ Error extracting video detections: {e}")
        
        return detections
    
    def _extract_players_from_prediction(self, result, scale: float = 1.0) -> List[Dict]:
        """Extract player detections from prediction result"""
        players = []
        
        try:
            print(f"🔍 Extracting players from result type: {type(result)}")
            print(f"   Result attributes: {dir(result) if hasattr(result, '__dict__') else 'No __dict__'}")
            
            # Handle different result formats from InferencePipeline
            predictions = []
            
            # Method 1: Try to get predictions directly
            if hasattr(result, 'predictions'):
                predictions = result.predictions
                print(f"   Using result.predictions: {len(predictions) if predictions else 0}")
            elif hasattr(result, 'data'):
                predictions = result.data
                print(f"   Using result.data: {len(predictions) if predictions else 0}")
            elif hasattr(result, '__len__') and hasattr(result, '__iter__'):
                # Handle PredictionGroup objects (directly iterable)
                predictions = result
                print(f"   Using result directly (iterable): {len(predictions) if predictions else 0}")
            elif isinstance(result, dict):
                if 'predictions' in result:
                    predictions = result['predictions']
                    print(f"   Using dict['predictions']: {len(predictions) if predictions else 0}")
                elif 'data' in result:
                    predictions = result['data']
                    print(f"   Using dict['data']: {len(predictions) if predictions else 0}")
                else:
                    predictions = [result]
                    print(f"   Using dict as single prediction")
            else:
                # Try to convert to list if possible
                try:
                    if hasattr(result, 'tolist'):
                        predictions = result.tolist()
                    else:
                        predictions = [result]
                    print(f"   Converted to list: {len(predictions)} items")
                except:
                    predictions = [result]
                    print(f"   Using result as single prediction")
            
            if predictions:
                print(f"   Processing {len(predictions)} predictions...")
                for i, pred in enumerate(predictions):
                    print(f"     Prediction {i}: {type(pred)} - {pred}")
                    
                    # Try multiple methods to extract player data
                    player_data = None
                    
                    # Method 1: Try to access as object attributes
                    if hasattr(pred, 'class_name') or hasattr(pred, 'class'):
                        class_name = getattr(pred, 'class_name', None) or getattr(pred, 'class', None)
                        confidence = getattr(pred, 'confidence', 0.5)
                        x = getattr(pred, 'x', 0)
                        y = getattr(pred, 'y', 0)
                        width = getattr(pred, 'width', 0)
                        height = getattr(pred, 'height', 0)
                        
                        if all(v is not None for v in [class_name, x, y, width, height]):
                            player_data = {
                                'class': class_name,
                                'confidence': confidence,
                                'x': x, 'y': y, 'width': width, 'height': height
                            }
                            print(f"       ✅ Extracted via object attributes")
                    
                    # Method 2: Try to convert to dict
                    if not player_data:
                        try:
                            if hasattr(pred, '__dict__'):
                                pred_dict = pred.__dict__
                            elif hasattr(pred, 'dict'):
                                pred_dict = pred.dict()
                            elif hasattr(pred, 'model_dump'):
                                pred_dict = pred.model_dump()
                            else:
                                pred_dict = {}
                            
                            print(f"       Converted to dict: {pred_dict}")
                            
                            # Handle nested json_prediction structure
                            if 'json_prediction' in pred_dict:
                                actual_pred = pred_dict['json_prediction']
                                class_name = actual_pred.get('class', None)
                                confidence = actual_pred.get('confidence', 0.5)
                                x = actual_pred.get('x', 0)
                                y = actual_pred.get('y', 0)
                                width = actual_pred.get('width', 0)
                                height = actual_pred.get('height', 0)
                            else:
                                class_name = pred_dict.get('class', None)
                                confidence = pred_dict.get('confidence', 0.5)
                                x = pred_dict.get('x', 0)
                                y = pred_dict.get('y', 0)
                                width = pred_dict.get('width', 0)
                                height = pred_dict.get('height', 0)
                            
                            if all(v is not None for v in [class_name, x, y, width, height]):
                                player_data = {
                                    'class': class_name,
                                    'confidence': confidence,
                                    'x': x, 'y': y, 'width': width, 'height': height
                                }
                                print(f"       ✅ Extracted via dict conversion")
                        
                        except Exception as e:
                            print(f"       ⚠️  Dict conversion failed: {e}")
                    
                    # Method 3: Try string parsing as last resort
                    if not player_data:
                        try:
                            pred_str = str(pred)
                            print(f"       Trying string parsing: {pred_str[:100]}...")
                            
                            if pred_str.startswith('{') and pred_str.endswith('}'):
                                import json
                                try:
                                    parsed = json.loads(pred_str)
                                    if 'class' in parsed and 'x' in parsed:
                                        player_data = parsed
                                        print(f"       ✅ Extracted via JSON parsing")
                                except:
                                    pass
                        except Exception as e:
                            print(f"       ⚠️  String parsing failed: {e}")
                    
                    # Process extracted player data
                    if player_data:
                        class_name = player_data['class']
                        confidence = player_data['confidence']
                        x = player_data['x']
                        y = player_data['y']
                        width = player_data['width']
                        height = player_data['height']
                        
                        print(f"       Extracted: class={class_name}, conf={confidence}, x={x}, y={y}, w={width}, h={height}")
                        
                        # Check if we have valid data
                        if class_name and confidence and x is not None and y is not None and width and height:
                            # Filter for player class (including goalkeeper)
                            if class_name.lower() in ['player', 'person', 'hockey_player', 'goalkeeper', 'skater']:
                                # Scale back to original frame size
                                if scale != 1.0:
                                    x = x / scale
                                    y = y / scale
                                    width = width / scale
                                    height = height / scale
                                
                                # Convert to OpenCV format [x, y, w, h]
                                bbox = [int(x - width/2), int(y - height/2), int(width), int(height)]
                                
                                players.append({
                                    'bbox': bbox,
                                    'confidence': confidence,
                                    'center': (int(x), int(y)),
                                    'keypoints': self._extract_keypoints(player_data, scale)
                                })
                                
                                print(f"       ✅ Added player: bbox={bbox}, confidence={confidence:.2f}")
                            else:
                                print(f"       ⚠️  Skipped non-player class: {class_name}")
                        else:
                            print(f"       ⚠️  Missing required attributes: class={class_name}, conf={confidence}, x={x}, y={y}, w={width}, h={height}")
                    else:
                        print(f"       ❌ Could not extract player data from prediction")
            
            print(f"   Final result: {len(players)} players extracted")
            
        except Exception as e:
            print(f"❌ Error extracting players: {e}")
            import traceback
            traceback.print_exc()
        
        return players
    
    def _extract_keypoints(self, pred: Dict, scale: float = 1.0) -> List[Dict]:
        """Extract keypoints if available in prediction"""
        keypoints = []
        
        try:
            if 'keypoints' in pred:
                for kp in pred['keypoints']:
                    x = kp.get('x', 0) / scale if scale != 1.0 else kp.get('x', 0)
                    y = kp.get('y', 0) / scale if scale != 1.0 else kp.get('y', 0)
                    confidence = kp.get('confidence', 0.5)
                    
                    keypoints.append({
                        'x': int(x),
                        'y': int(y),
                        'confidence': confidence
                    })
        except Exception as e:
            print(f"⚠️  Keypoint extraction failed: {e}")
        
        return keypoints
    
    def get_player_bounding_boxes(self, frame: np.ndarray) -> List[List[int]]:
        """Get list of bounding boxes for player selection modal"""
        players = self.detect_players_in_frame(frame)
        return [player['bbox'] for player in players]
    
    def track_player_across_frames(self, video_path: str, initial_bbox: List[int], max_fps: int = 30) -> List[Dict]:
        """Track a specific player across video frames using the proven Computer Vision for Hockey method"""
        if not INFERENCE_AVAILABLE:
            return []
        
        try:
            print(f"🎬 Starting Computer Vision for Hockey-style player tracking...")
            print(f"   Initial bbox: {initial_bbox}")
            print(f"   Video: {video_path}")
            print(f"   Max FPS: {max_fps}")
            
            # Initialize tracking state
            target_bbox = initial_bbox.copy()
            target_center = (target_bbox[0] + target_bbox[2]/2, target_bbox[1] + target_bbox[3]/2)
            
            # Tracking state variables
            self.next_player_id = 0
            self.player_tracks = {}  # Maps player_id to track info
            self.frame_player_matches = {}  # Maps frame_id to player_id mappings
            
            tracked_detections = []
            
            # Open video and process frame by frame
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"❌ Could not open video: {video_path}")
                return []
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_step = max(1, int(fps / max_fps))  # Process every nth frame to match target FPS
            
            print(f"   Video FPS: {fps}, Target FPS: {max_fps}, Frame step: {frame_step}")
            print(f"   Total frames: {total_frames}")
            
            frame_count = 0
            processed_frames = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every nth frame to match target FPS
                if frame_count % frame_step == 0:
                    processed_frames += 1
                    timestamp = frame_count / fps
                    
                    print(f"   Processing frame {frame_count} (processed: {processed_frames})")
                    
                    # Detect players in this frame
                    frame_players = self.detect_players_in_frame(frame)
                    
                    if frame_players:
                        # Find the best match for our target player
                        best_match = None
                        best_score = 0.5  # Minimum threshold for matching
                        
                        for player in frame_players:
                            score = self._calculate_player_similarity_cvh_style(
                                player, target_bbox, target_center, frame_count
                            )
                            
                            if score > best_score:
                                best_score = score
                                best_match = player
                        
                        if best_match:
                            # Update tracking state
                            new_bbox = best_match['bbox']
                            new_center = (new_bbox[0] + new_bbox[2]/2, new_bbox[1] + new_bbox[3]/2)
                            
                            # Update target state
                            target_bbox = new_bbox.copy()
                            target_center = new_center
                            
                            # Add to tracked detections
                            tracked_detections.append({
                                'frame': frame_count,
                                'bbox': new_bbox,
                                'confidence': best_match.get('confidence', 0.8),
                                'center': new_center,
                                'keypoints': best_match.get('keypoints', []),
                                'tracking_method': 'detection',
                                'similarity_score': best_score
                            })
                            
                            print(f"     ✅ Frame {frame_count}: Player tracked (score: {best_score:.3f})")
                        else:
                            # No good match found, use prediction based on previous movement
                            if len(tracked_detections) > 0:
                                last_detection = tracked_detections[-1]
                                last_bbox = last_detection['bbox']
                                last_center = last_detection['center']
                                
                                # Simple prediction: assume same position
                                predicted_bbox = last_bbox.copy()
                                tracked_detections.append({
                                    'frame': frame_count,
                                    'bbox': predicted_bbox,
                                    'confidence': 0.3,
                                    'center': last_center,
                                    'keypoints': [],
                                    'tracking_method': 'prediction'
                                })
                                print(f"     ⚠️  Frame {frame_count}: No good match, using prediction")
                            else:
                                print(f"     ❌ Frame {frame_count}: No good match and no previous data")
                    else:
                        # No players detected in this frame
                        if len(tracked_detections) > 0:
                            last_detection = tracked_detections[-1]
                            last_bbox = last_detection['bbox']
                            last_center = last_detection['center']
                            
                            # Use last known position
                            tracked_detections.append({
                                'frame': frame_count,
                                'bbox': last_bbox,
                                'confidence': 0.2,
                                'center': last_center,
                                'keypoints': [],
                                'tracking_method': 'no_detection'
                            })
                            print(f"     ⚠️  Frame {frame_count}: No players detected, using last position")
                        else:
                            print(f"     ❌ Frame {frame_count}: No players detected and no previous data")
                
                frame_count += 1
                
                # Progress update every 30 frames
                if frame_count % (30 * frame_step) == 0:
                    print(f"   📊 Progress: {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")
            
            cap.release()
            
            print(f"✅ Player tracking completed: {len(tracked_detections)} frames tracked")
            print(f"   Total frames processed: {processed_frames}")
            print(f"   Tracking success rate: {len([d for d in tracked_detections if d.get('tracking_method') == 'detection'])}/{len(tracked_detections)} frames")
            
            return tracked_detections
            
        except Exception as e:
            print(f"❌ Player tracking error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _calculate_player_similarity_cvh_style(self, player: Dict, target_bbox: List[int], target_center: Tuple[float, float], frame_count: int) -> float:
        """Calculate similarity score using the Computer Vision for Hockey method"""
        try:
            player_bbox = player['bbox']
            player_center = (player_bbox[0] + player_bbox[2]/2, player_bbox[1] + player_bbox[3]/2)
            
            # 1. Position similarity (using bounding box center)
            # Calculate Euclidean distance
            distance = np.sqrt((player_center[0] - target_center[0])**2 + (player_center[1] - target_center[1])**2)
            
            # Convert distance to similarity score (closer = higher score)
            # Assuming reasonable movement between frames (e.g., max 100 pixels)
            max_distance = 100.0
            position_score = max(0, 1.0 - (distance / max_distance))
            
            # 2. Size similarity (players shouldn't change size dramatically)
            target_size = (target_bbox[2], target_bbox[3])
            player_size = (player_bbox[2], player_bbox[3])
            size_diff = abs(player_size[0] - target_size[0]) + abs(player_size[1] - target_size[1])
            size_score = max(0, 1.0 - size_diff / 100)
            
            # 3. Class similarity (same Roboflow class = higher score)
            # For now, assume all detections are players
            class_score = 1.0
            
            # 4. Confidence score
            confidence_score = player.get('confidence', 0.5)
            
            # Combined score (weighted average) - same weights as CVH
            final_score = 0.7 * position_score + 0.2 * size_score + 0.1 * confidence_score
            
            return final_score
            
        except Exception as e:
            print(f"⚠️  Error calculating player similarity: {e}")
            return 0.0
    
    def _find_closest_player(self, players: List[Dict], target_bbox: List[int]) -> Optional[Dict]:
        """Find player closest to target bounding box"""
        if not players:
            return None
        
        target_center = (target_bbox[0] + target_bbox[2]/2, target_bbox[1] + target_bbox[3]/2)
        min_distance = float('inf')
        closest_player = None
        
        for player in players:
            bbox = player['bbox']
            player_center = (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)
            
            distance = np.sqrt((player_center[0] - target_center[0])**2 + 
                             (player_center[1] - target_center[1])**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_player = player
        
        return closest_player

# Global detector instance with lazy loading
_roboflow_detector = None
_detector_lock = threading.Lock()

def get_inference_detector():
    """Get the global Roboflow hosted inference detector instance (lazy loading)"""
    global _roboflow_detector
    
    if _roboflow_detector is None:
        with _detector_lock:
            if _roboflow_detector is None:
                print("🚀 Initializing Roboflow hosted detector (first time)...")
                
                # Your Roboflow InferencePipeline credentials
                API_KEY = "YDZxw1AQEvclkzV0ZLOz"
                WORKSPACE_NAME = "hockey-fghn7"
                WORKFLOW_ID = "custom-workflow-4"  # This is your custom workflow ID
                
                _roboflow_detector = OptimizedRoboflowPlayerDetector(API_KEY, WORKSPACE_NAME, WORKFLOW_ID)
                print("✅ Roboflow hosted detector initialized!")
    
    return _roboflow_detector

# Performance monitoring
def get_detector_stats():
    """Get performance statistics for the detector"""
    if _roboflow_detector:
        return {
            'pipeline_ready': _roboflow_detector._pipeline_ready,
            'cache_size': len(_roboflow_detector._detection_cache),
            'last_detection_time': _roboflow_detector._last_detection_time
        }
    return {'status': 'not_initialized'}

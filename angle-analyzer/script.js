// Angle Analyzer v2.0 - JavaScript functionality

class AngleAnalyzer {
    constructor() {
        // Image analysis elements
        this.imageCanvas = document.getElementById('imageCanvas');
        this.imageCtx = this.imageCanvas.getContext('2d');
        this.imageResultDiv = document.getElementById('imageResult');
        this.imageUploadInput = document.getElementById('imageUpload');
        this.imageResetButton = document.getElementById('imageReset');
        
        // Video analysis elements
        this.videoCanvas = document.getElementById('videoCanvas');
        this.videoCtx = this.videoCanvas.getContext('2d');
        this.videoPlayer = document.getElementById('videoPlayer');
        this.videoUploadInput = document.getElementById('videoUpload');
        this.videoResultDiv = document.getElementById('videoResult');
        this.frameInfoDiv = document.getElementById('frameInfo');
        
        // Video controls
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.stepBackBtn = document.getElementById('stepBackBtn');
        this.stepForwardBtn = document.getElementById('stepForwardBtn');
        this.progressSlider = document.getElementById('progressSlider');
        this.speedSlider = document.getElementById('speedSlider');
        this.speedValue = document.getElementById('speedValue');
        this.clearDrawingsBtn = document.getElementById('clearDrawingsBtn');
        
        // Drawing tools
        this.lineTool = document.getElementById('lineTool');
        this.angleTool = document.getElementById('angleTool');
        this.freehandTool = document.getElementById('freehandTool');
        this.eraserTool = document.getElementById('eraserTool');
        this.colorInput = document.getElementById('colorInput');
        
        // Tab elements
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
        
        // State variables
        this.points = [];
        this.img = new Image();
        this.originalCanvasSize = { width: 800, height: 600 };
        this.currentTool = 'line';
        this.isDrawing = false;
        this.drawingPath = [];
        this.drawings = []; // Store all drawings for persistence
        this.videoFrameCount = 0;
        this.totalFrames = 0;
        
        this.initializeEventListeners();
        this.setupCanvas();
        this.setupVideoCanvas();
    }

    initializeEventListeners() {
        // Tab switching
        this.tabButtons.forEach(button => {
            button.addEventListener('click', (event) => this.switchTab(event.target.dataset.tab));
        });
        
        // Image analysis events
        this.imageUploadInput.addEventListener('change', (event) => this.handleImageUpload(event));
        this.imageCanvas.addEventListener('click', (event) => this.handleImageCanvasClick(event));
        this.imageResetButton.addEventListener('click', () => this.resetImageAnalysis());
        
        // Video analysis events
        this.videoUploadInput.addEventListener('change', (event) => this.handleVideoUpload(event));
        this.videoCanvas.addEventListener('mousedown', (event) => this.handleVideoCanvasMouseDown(event));
        this.videoCanvas.addEventListener('mousemove', (event) => this.handleVideoCanvasMouseMove(event));
        this.videoCanvas.addEventListener('mouseup', (event) => this.handleVideoCanvasMouseUp(event));
        this.videoCanvas.addEventListener('click', (event) => this.handleVideoCanvasClick(event));
        
        // Prevent default behavior on canvas
        this.videoCanvas.addEventListener('contextmenu', (event) => event.preventDefault());
        this.videoCanvas.addEventListener('selectstart', (event) => event.preventDefault());
        
        // Video controls
        this.playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        this.stepBackBtn.addEventListener('click', () => this.stepBack());
        this.stepForwardBtn.addEventListener('click', () => this.stepForward());
        this.progressSlider.addEventListener('input', (event) => this.seekVideo(event.target.value));
        this.speedSlider.addEventListener('input', (event) => this.changeSpeed(event.target.value));
        this.clearDrawingsBtn.addEventListener('click', () => this.clearDrawings());
        
        // Drawing tools
        this.lineTool.addEventListener('click', () => this.selectTool('line'));
        this.angleTool.addEventListener('click', () => this.selectTool('angle'));
        this.freehandTool.addEventListener('click', () => this.selectTool('freehand'));
        this.eraserTool.addEventListener('click', () => this.selectTool('eraser'));
        
        // Video events
        this.videoPlayer.addEventListener('loadedmetadata', () => this.handleVideoLoaded());
        this.videoPlayer.addEventListener('timeupdate', () => this.updateFrameInfo());
        this.videoPlayer.addEventListener('resize', () => this.resizeVideoCanvas());
        
        // Window resize event
        window.addEventListener('resize', () => this.resizeVideoCanvas());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => this.handleKeyboard(event));
    }

    setupCanvas() {
        this.imageCanvas.width = this.originalCanvasSize.width;
        this.imageCanvas.height = this.originalCanvasSize.height;
        this.imageCtx.fillStyle = '#333';
        this.imageCtx.fillRect(0, 0, this.imageCanvas.width, this.imageCanvas.height);
        this.drawImageInstructions();
    }
    
    setupVideoCanvas() {
        // Canvas will be resized when video loads
        this.videoCtx.globalCompositeOperation = 'source-over';
    }

    drawImageInstructions() {
        this.imageCtx.fillStyle = '#00ffcc';
        this.imageCtx.font = '20px Courier New';
        this.imageCtx.textAlign = 'center';
        this.imageCtx.fillText('Upload an image to begin angle measurement', 
                         this.imageCanvas.width / 2, this.imageCanvas.height / 2 - 20);
        this.imageCtx.font = '16px Courier New';
        this.imageCtx.fillText('Click two points to measure the angle of the line', 
                         this.imageCanvas.width / 2, this.imageCanvas.height / 2 + 20);
    }
    
    drawVideoInstructions() {
        this.videoCtx.fillStyle = '#00ffcc';
        this.videoCtx.font = '20px Courier New';
        this.videoCtx.textAlign = 'center';
        this.videoCtx.fillText('Upload a video to begin analysis', 
                         this.videoCanvas.width / 2, this.videoCanvas.height / 2 - 20);
        this.videoCtx.font = '16px Courier New';
        this.videoCtx.fillText('Use drawing tools to annotate the video', 
                         this.videoCanvas.width / 2, this.videoCanvas.height / 2 + 20);
    }

    // Tab switching
    switchTab(tabName) {
        // Update tab buttons
        this.tabButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.tab === tabName);
        });
        
        // Update tab content
        this.tabContents.forEach(content => {
            content.classList.toggle('active', content.id === tabName);
        });
    }
    
    // Image analysis methods
    handleImageUpload(event) {
        const file = event.target.files[0];
        if (file) {
            this.showImageLoading();
            const reader = new FileReader();
            reader.onload = (e) => {
                this.img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    handleVideoUpload(event) {
        const file = event.target.files[0];
        if (file) {
            this.showVideoLoading();
            const url = URL.createObjectURL(file);
            this.videoPlayer.src = url;
            this.videoResultDiv.textContent = `Video: ${file.name}`;
            
            // Hide placeholder and show video wrapper when video loads
            this.videoPlayer.onloadeddata = () => {
                document.getElementById('videoPlaceholder').style.display = 'none';
                document.getElementById('videoWrapper').style.display = 'block';
                document.getElementById('videoControls').style.display = 'flex';
                document.getElementById('drawingTools').style.display = 'block';
                this.resizeVideoCanvas();
            };
        }
    }

    showImageLoading() {
        this.imageResultDiv.innerHTML = '<div class="loading"></div> Loading image...';
    }
    
    showVideoLoading() {
        this.videoResultDiv.innerHTML = '<div class="loading"></div> Loading video...';
    }

    handleImageLoad() {
        this.hideImageLoading();
        this.clearImageCanvas();
        this.drawImage();
        this.points = [];
        this.updateImageResult('Angle: Not measured yet');
    }
    
    handleVideoLoaded() {
        this.hideVideoLoading();
        this.totalFrames = Math.floor(this.videoPlayer.duration * 30); // Assume 30fps
        this.updateFrameInfo();
        this.resizeVideoCanvas();
    }

    hideImageLoading() {
        this.imageResultDiv.textContent = 'Angle: Not measured yet';
    }
    
    hideVideoLoading() {
        this.videoResultDiv.textContent = 'Video: Ready';
    }

    clearImageCanvas() {
        this.imageCtx.clearRect(0, 0, this.imageCanvas.width, this.imageCanvas.height);
    }
    
    clearVideoCanvas() {
        this.videoCtx.clearRect(0, 0, this.videoCanvas.width, this.videoCanvas.height);
        this.videoCtx.globalCompositeOperation = 'source-over';
    }

    drawImage() {
        const aspectRatio = this.img.width / this.img.height;
        let newWidth = this.originalCanvasSize.width;
        let newHeight = newWidth / aspectRatio;
        
        if (newHeight > this.originalCanvasSize.height) {
            newHeight = this.originalCanvasSize.height;
            newWidth = newHeight * aspectRatio;
        }
        
        this.imageCanvas.width = newWidth;
        this.imageCanvas.height = newHeight;
        this.imageCtx.drawImage(this.img, 0, 0, newWidth, newHeight);
    }
    
    resizeVideoCanvas() {
        // Wait for video to be ready
        if (this.videoPlayer.videoWidth && this.videoPlayer.videoHeight) {
            const videoRect = this.videoPlayer.getBoundingClientRect();
            this.videoCanvas.width = videoRect.width;
            this.videoCanvas.height = videoRect.height;
            this.videoCanvas.style.width = videoRect.width + 'px';
            this.videoCanvas.style.height = videoRect.height + 'px';
            
            // Clear canvas and make it transparent
            this.videoCtx.clearRect(0, 0, this.videoCanvas.width, this.videoCanvas.height);
            this.videoCtx.globalCompositeOperation = 'source-over';
        }
    }

    handleImageCanvasClick(event) {
        if (!this.img.src) return;
        
        const rect = this.imageCanvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        this.points.push({ x, y });
        this.drawImagePoint(x, y);
        
        if (this.points.length === 2) {
            const angle = this.calculateAngle(this.points[0], this.points[1]);
            this.updateImageResult(`Angle: ${angle.toFixed(2)}°`);
            this.updateAngleDisplay(angle);
            this.drawImageLines(this.points);
            this.points = []; // Reset for next measurement
        } else {
            this.updateImageResult(`Points: ${this.points.length}/2`);
            this.updateAngleDisplay(null);
        }
    }

    // Video control methods
    togglePlayPause() {
        if (this.videoPlayer.paused) {
            this.videoPlayer.play();
            this.playPauseBtn.textContent = '⏸️ Pause';
        } else {
            this.videoPlayer.pause();
            this.playPauseBtn.textContent = '▶️ Play';
        }
    }
    
    stepBack() {
        this.videoPlayer.currentTime = Math.max(0, this.videoPlayer.currentTime - 1/30);
    }
    
    stepForward() {
        this.videoPlayer.currentTime = Math.min(this.videoPlayer.duration, this.videoPlayer.currentTime + 1/30);
    }
    
    changeSpeed(speed) {
        this.videoPlayer.playbackRate = parseFloat(speed);
        this.speedValue.textContent = speed + 'x';
    }
    
    updateFrameInfo() {
        this.videoFrameCount = Math.floor(this.videoPlayer.currentTime * 30);
        this.frameInfoDiv.textContent = `Frame: ${this.videoFrameCount} / ${this.totalFrames}`;
        
        // Update progress slider
        if (this.videoPlayer.duration) {
            const progress = (this.videoPlayer.currentTime / this.videoPlayer.duration) * 100;
            this.progressSlider.value = progress;
        }
    }
    
    seekVideo(progress) {
        if (this.videoPlayer.duration) {
            const time = (progress / 100) * this.videoPlayer.duration;
            this.videoPlayer.currentTime = time;
        }
    }
    
    // Drawing tool methods
    selectTool(tool) {
        this.currentTool = tool;
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(tool + 'Tool').classList.add('active');
        
        // Update cursor
        const cursor = tool === 'eraser' ? 'crosshair' : 'crosshair';
        this.videoCanvas.style.cursor = cursor;
    }
    
    // Video canvas event handlers
    handleVideoCanvasMouseDown(event) {
        if (this.currentTool === 'freehand') {
            this.isDrawing = true;
            const rect = this.videoCanvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            this.drawingPath = [{ x, y }];
        }
    }
    
    handleVideoCanvasMouseMove(event) {
        if (this.isDrawing && this.currentTool === 'freehand') {
            const rect = this.videoCanvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            this.drawingPath.push({ x, y });
            this.drawFreehandPath();
        }
    }
    
    handleVideoCanvasMouseUp(event) {
        if (this.isDrawing) {
            this.isDrawing = false;
            if (this.drawingPath.length > 0) {
                this.drawings.push({
                    type: 'freehand',
                    path: [...this.drawingPath],
                    color: this.colorInput.value
                });
            }
            this.drawingPath = [];
        }
    }
    
    handleVideoCanvasClick(event) {
        if (this.currentTool === 'line' || this.currentTool === 'angle') {
            const rect = this.videoCanvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            this.points.push({ x, y });
            this.drawVideoPoint(x, y);
            
            if (this.currentTool === 'line' && this.points.length === 2) {
                this.drawings.push({
                    type: 'line',
                    points: [...this.points],
                    color: this.colorInput.value
                });
                this.drawVideoLine(this.points);
                this.points = [];
            } else if (this.currentTool === 'angle' && this.points.length === 2) {
                const angle = this.calculateAngle(this.points[0], this.points[1]);
                this.updateAngleDisplay(angle);
                this.drawings.push({
                    type: 'angle',
                    points: [...this.points],
                    angle: angle,
                    color: this.colorInput.value
                });
                this.drawVideoAngle(this.points, angle);
                this.points = [];
            }
        }
    }
    
    // Drawing methods
    drawImagePoint(x, y) {
        this.imageCtx.beginPath();
        this.imageCtx.arc(x, y, 6, 0, Math.PI * 2);
        this.imageCtx.fillStyle = '#ff4444';
        this.imageCtx.fill();
        this.imageCtx.strokeStyle = '#fff';
        this.imageCtx.lineWidth = 2;
        this.imageCtx.stroke();
        this.imageCtx.closePath();
        
        // Add point number
        this.imageCtx.fillStyle = '#fff';
        this.imageCtx.font = 'bold 14px Arial';
        this.imageCtx.textAlign = 'center';
        this.imageCtx.fillText(this.points.length.toString(), x, y + 5);
    }
    
    drawVideoPoint(x, y) {
        this.videoCtx.beginPath();
        this.videoCtx.arc(x, y, 6, 0, Math.PI * 2);
        this.videoCtx.fillStyle = this.colorInput.value;
        this.videoCtx.fill();
        this.videoCtx.strokeStyle = '#fff';
        this.videoCtx.lineWidth = 2;
        this.videoCtx.stroke();
        this.videoCtx.closePath();
        
        // Add point number
        this.videoCtx.fillStyle = '#fff';
        this.videoCtx.font = 'bold 14px Arial';
        this.videoCtx.textAlign = 'center';
        this.videoCtx.fillText(this.points.length.toString(), x, y + 5);
    }
    
    drawFreehandPath() {
        if (this.drawingPath.length < 2) return;
        
        this.videoCtx.beginPath();
        this.videoCtx.moveTo(this.drawingPath[0].x, this.drawingPath[0].y);
        for (let i = 1; i < this.drawingPath.length; i++) {
            this.videoCtx.lineTo(this.drawingPath[i].x, this.drawingPath[i].y);
        }
        this.videoCtx.strokeStyle = this.colorInput.value;
        this.videoCtx.lineWidth = 3;
        this.videoCtx.stroke();
    }
    
    drawVideoLine(points) {
        this.videoCtx.beginPath();
        this.videoCtx.moveTo(points[0].x, points[0].y);
        this.videoCtx.lineTo(points[1].x, points[1].y);
        this.videoCtx.strokeStyle = this.colorInput.value;
        this.videoCtx.lineWidth = 3;
        this.videoCtx.stroke();
    }
    
    drawVideoAngle(points, angle) {
        this.drawVideoLine(points);
        this.drawVideoAngleArc(points[0], points[1]);
        
        // Draw angle text
        this.videoCtx.fillStyle = this.colorInput.value;
        this.videoCtx.font = 'bold 16px Arial';
        this.videoCtx.textAlign = 'center';
        this.videoCtx.fillText(`${angle.toFixed(1)}°`, 
            (points[0].x + points[1].x) / 2, 
            (points[0].y + points[1].y) / 2 - 10);
    }
    
    drawVideoAngleArc(p1, p2) {
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        const lineAngle = Math.atan2(dy, dx);
        
        const radius = 30;
        const startAngle = 0;
        const endAngle = lineAngle;
        
        this.videoCtx.beginPath();
        this.videoCtx.arc(p1.x, p1.y, radius, startAngle, endAngle);
        this.videoCtx.strokeStyle = this.colorInput.value;
        this.videoCtx.lineWidth = 2;
        this.videoCtx.stroke();
        
        // Draw horizontal reference line
        this.videoCtx.beginPath();
        this.videoCtx.moveTo(p1.x - radius, p1.y);
        this.videoCtx.lineTo(p1.x + radius, p1.y);
        this.videoCtx.strokeStyle = this.colorInput.value;
        this.videoCtx.lineWidth = 1;
        this.videoCtx.setLineDash([5, 5]);
        this.videoCtx.stroke();
        this.videoCtx.setLineDash([]);
    }
    
    clearDrawings() {
        this.clearVideoCanvas();
        this.drawings = [];
        this.points = [];
        this.updateAngleDisplay(null);
    }

    calculateAngle(p1, p2) {
        // Calculate the angle of the line from p1 to p2 relative to horizontal (0°)
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        
        // Calculate angle in radians, then convert to degrees
        let angle = Math.atan2(dy, dx) * (180 / Math.PI);
        
        // Normalize to 0-360 degrees
        if (angle < 0) {
            angle += 360;
        }
        
        return angle;
    }

    drawImageLines(points) {
        this.imageCtx.beginPath();
        this.imageCtx.moveTo(points[0].x, points[0].y);
        this.imageCtx.lineTo(points[1].x, points[1].y);
        this.imageCtx.strokeStyle = '#ff4444';
        this.imageCtx.lineWidth = 3;
        this.imageCtx.stroke();
        this.imageCtx.closePath();
        
        // Draw angle arc
        this.drawImageAngleArc(points[0], points[1]);
    }

    drawImageAngleArc(p1, p2) {
        // Draw arc showing angle from horizontal (0°) to the line
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        const lineAngle = Math.atan2(dy, dx);
        
        const radius = 30;
        const startAngle = 0; // Horizontal reference
        const endAngle = lineAngle;
        
        this.imageCtx.beginPath();
        this.imageCtx.arc(p1.x, p1.y, radius, startAngle, endAngle);
        this.imageCtx.strokeStyle = '#00ffcc';
        this.imageCtx.lineWidth = 2;
        this.imageCtx.stroke();
        
        // Draw horizontal reference line
        this.imageCtx.beginPath();
        this.imageCtx.moveTo(p1.x - radius, p1.y);
        this.imageCtx.lineTo(p1.x + radius, p1.y);
        this.imageCtx.strokeStyle = '#00ffcc';
        this.imageCtx.lineWidth = 1;
        this.imageCtx.setLineDash([5, 5]);
        this.imageCtx.stroke();
        this.imageCtx.setLineDash([]);
    }

    updateImageResult(text) {
        this.imageResultDiv.textContent = text;
    }
    
    updateAngleDisplay(angle) {
        const angleDisplay = document.getElementById('angleMeasurement');
        if (angleDisplay) {
            if (angle !== null && angle !== undefined) {
                angleDisplay.textContent = `Angle: ${angle.toFixed(2)}°`;
            } else {
                angleDisplay.textContent = 'Angle: --°';
            }
        }
    }

    resetImageAnalysis() {
        this.clearImageCanvas();
        if (this.img.src) {
            this.drawImage();
        } else {
            this.drawImageInstructions();
        }
        this.points = [];
        this.updateImageResult('Angle: Not measured yet');
        this.updateAngleDisplay(null);
    }

    handleKeyboard(event) {
        switch(event.key) {
            case 'r':
            case 'R':
                if (document.getElementById('image-analysis').classList.contains('active')) {
                    this.resetImageAnalysis();
                } else {
                    this.clearDrawings();
                }
                break;
            case 'Escape':
                if (document.getElementById('image-analysis').classList.contains('active')) {
                    this.resetImageAnalysis();
                } else {
                    this.clearDrawings();
                }
                break;
            case ' ':
                event.preventDefault();
                if (document.getElementById('video-analysis').classList.contains('active')) {
                    this.togglePlayPause();
                }
                break;
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const analyzer = new AngleAnalyzer();
    analyzer.img.onload = () => analyzer.handleImageLoad();
});

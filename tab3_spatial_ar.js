class ArohaSpatialARPortal {
    constructor(readoutElementId) {
        this.readout = document.getElementById(readoutElementId);
        this.videoElement = null;
        this.isStreaming = false;
        this.alpha = 0;
        this.beta = 0;
        this.gamma = 0;
    }

    async toggleCamera() {
        if (this.isStreaming && this.videoElement) {
            const tracks = this.videoElement.srcObject ? this.videoElement.srcObject.getTracks() : [];
            tracks.forEach(t => t.stop());
            this.videoElement.remove();
            this.videoElement = null;
            this.isStreaming = false;
            window.AROHA_AR_TRANSPARENT = false;
            if (this.readout) this.readout.textContent = 'AR Camera Stopped (Deep Space Mode)';
            return false;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' },
                audio: false
            });
            this.videoElement = document.createElement('video');
            this.videoElement.srcObject = stream;
            this.videoElement.autoplay = true;
            this.videoElement.playsInline = true;
            this.videoElement.style.cssText = 'position:fixed; inset:0; width:100vw; height:100vh; object-fit:cover; z-index:0; opacity:0.55; pointer-events:none;';
            document.body.prepend(this.videoElement);
            this.isStreaming = true;
            window.AROHA_AR_TRANSPARENT = true;
            if (this.readout) this.readout.textContent = 'WebRTC Camera Overlay Active (Transparent GL)';
            return true;
        } catch (err) {
            if (this.readout) this.readout.textContent = `Camera unavailable: ${err.message}`;
            return false;
        }
    }

    initGyroscope(onTiltCallback) {
        if (window.DeviceOrientationEvent) {
            window.addEventListener('deviceorientation', (event) => {
                this.alpha = event.alpha || 0;
                this.beta = event.beta || 0;
                this.gamma = event.gamma || 0;
                if (this.readout) {
                    this.readout.textContent = `Tiki Tilt 6-DOF -> α:${this.alpha.toFixed(1)}° β:${this.beta.toFixed(1)}° γ:${this.gamma.toFixed(1)}°`;
                }
                if (onTiltCallback) onTiltCallback(this.alpha, this.beta, this.gamma);
            });
        }
    }
}
window.ArohaSpatialARPortal = ArohaSpatialARPortal;

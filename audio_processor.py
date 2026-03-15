import numpy as np
from scipy import signal
import soundfile as sf
from pydub import AudioSegment
import io
import asyncio
from collections import deque
import librosa
import scipy.fftpack

class AudioProcessor:
    def __init__(self):
        self.active_sessions = {}
        self.filters = {}
        self.delay_lines = {}  # For echo effects
        self.distortion_history = {}  # For distortion effect
        self.kernel_presets = {
            'light': {'gain': 1.5, 'bass': 0.8, 'distortion': 0.3, 'loudness': 0.7, 'clip': 0.6},
            'medium': {'gain': 2.0, 'bass': 1.5, 'distortion': 0.7, 'loudness': 0.8, 'clip': 0.8},
            'heavy': {'gain': 3.0, 'bass': 2.0, 'distortion': 1.0, 'loudness': 1.0, 'clip': 1.0},
            'kernel': {'gain': 4.0, 'bass': 3.0, 'distortion': 1.5, 'loudness': 1.2, 'clip': 1.5, 'saturation': 2.0}
        }
        
    def create_filter_chain(self, chat_id):
        """Create audio processing chain for a chat with kernel-like settings"""
        return {
            'gain': 2.0,  # Higher default gain
            'bass': 1.5,  # More bass
            'mid': 1.0,   # Mid boost
            'treble': 0.5, # Treble cut
            'echo': 0.2,
            'reverb': 0.3,
            'noise_reduction': 0.1,
            'loudness': 0.8,  # High loudness
            'distortion': 0.7,  # Distortion for kernel sound
            'saturation': 0.8,  # Saturation for warmth
            'compression': 0.9,  # Heavy compression
            'limiter': True,
            'eq': [1.5, 1.8, 2.0, 1.8, 1.5, 1.2, 1.0, 0.8, 0.6, 0.4],  # 10-band EQ (bass heavy)
            'clip_threshold': 0.9,  # Soft clip threshold
            'bit_depth': 16,  # Bit crushing effect
            'sample_rate': 48000
        }
    
    async def process_audio(self, audio_data, chat_id, source_chat):
        """Process audio with all applied filters for kernel-like sound"""
        if chat_id not in self.filters:
            self.filters[chat_id] = self.create_filter_chain(chat_id)
        
        filters = self.filters[chat_id]
        
        # Convert to numpy array for processing
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        audio_float = audio_array.astype(np.float32) / 32768.0
        
        # Apply filters in sequence for aggressive sound
        processed = audio_float.copy()
        
        # 1. Initial gain boost
        processed *= filters['gain'] * 1.5
        
        # 2. Apply bass boost (multiple stages for deep bass)
        if filters['bass'] > 0:
            processed = self.apply_kernel_bass(processed, filters['bass'])
        
        # 3. Apply mid boost for presence
        if filters.get('mid', 0) > 0:
            processed = self.apply_mid_boost(processed, filters['mid'])
        
        # 4. Apply EQ (bass-heavy)
        processed = self.apply_heavy_eq(processed, filters['eq'])
        
        # 5. Apply distortion for kernel character
        if filters['distortion'] > 0:
            processed = self.apply_kernel_distortion(processed, filters['distortion'])
        
        # 6. Apply saturation for warmth
        if filters['saturation'] > 0:
            processed = self.apply_saturation(processed, filters['saturation'])
        
        # 7. Apply compression for loudness
        if filters['compression'] > 0:
            processed = self.apply_heavy_compression(processed, filters['compression'])
        
        # 8. Apply loudness normalization (very aggressive)
        if filters['loudness'] > 0:
            processed = self.apply_kernel_loudness(processed, filters['loudness'])
        
        # 9. Apply echo/reverb
        if filters['echo'] > 0:
            processed = self.apply_kernel_echo(processed, filters['echo'])
        
        # 10. Apply bit crushing for that digital distortion
        processed = self.apply_bit_crushing(processed, filters)
        
        # 11. Final gain stage and clipping
        processed = self.apply_kernel_clipping(processed, filters['clip_threshold'])
        
        # 12. Normalize to prevent extreme values
        max_val = np.max(np.abs(processed))
        if max_val > 1.0:
            processed = processed / max_val * 0.95
        
        # Convert back to int16 with dithering
        processed_int16 = self.float_to_int16_with_dither(processed)
        
        return processed_int16.tobytes()
    
    def apply_kernel_bass(self, audio, amount):
        """Apply aggressive bass boost for kernel sound"""
        # Multi-band bass processing
        sample_rate = 48000
        
        # Sub-bass (20-60 Hz) - very heavy
        b_sub, a_sub = signal.butter(4, 60/(sample_rate/2), 'low')
        sub_bass = signal.filtfilt(b_sub, a_sub, audio)
        
        # Mid-bass (60-250 Hz)
        b_mid, a_mid = signal.butter(4, [60/(sample_rate/2), 250/(sample_rate/2)], 'band')
        mid_bass = signal.filtfilt(b_mid, a_mid, audio)
        
        # Combine with different gains
        result = audio.copy()
        result += sub_bass * (amount * 2.5)  # Heavy sub-bass
        result += mid_bass * (amount * 1.8)  # Strong mid-bass
        
        # Add some harmonic distortion to bass
        result = result + 0.3 * np.sign(result) * (result**2) * amount
        
        return result
    
    def apply_mid_boost(self, audio, amount):
        """Boost mid frequencies for presence"""
        sample_rate = 48000
        # Boost 800Hz - 2kHz for aggressive presence
        b, a = signal.butter(2, [800/(sample_rate/2), 2000/(sample_rate/2)], 'band')
        mids = signal.filtfilt(b, a, audio)
        return audio + mids * amount
    
    def apply_heavy_eq(self, audio, eq_bands):
        """Apply heavy EQ with boosted lows"""
        # Simple FFT-based EQ
        fft_audio = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1/48000)
        
        # Apply EQ bands
        for i, gain in enumerate(eq_bands):
            # Map band index to frequency range
            start_freq = 20 * (2 ** i)  # 20, 40, 80, 160, 320, 640, 1280, 2560, 5120, 10240
            end_freq = start_freq * 2
            
            mask = (freqs >= start_freq) & (freqs < end_freq)
            fft_audio[mask] *= gain
        
        return np.fft.irfft(fft_audio)
    
    def apply_kernel_distortion(self, audio, amount):
        """Apply aggressive distortion for kernel sound"""
        # Soft clipping with waveshaping
        distorted = np.tanh(audio * (1 + amount * 3))
        
        # Add even/odd harmonics
        distorted = distorted + 0.3 * np.power(audio, 3) * amount
        
        # Add some crossover distortion
        distorted = np.where(np.abs(distorted) < 0.1 * amount, 0, distorted)
        
        # Blend with original
        return audio * (1 - amount * 0.3) + distorted * (amount * 1.3)
    
    def apply_saturation(self, audio, amount):
        """Apply tape-like saturation"""
        # Tube saturation emulation
        saturated = np.sign(audio) * (1 - np.exp(-np.abs(audio) * (5 * amount)))
        
        # Add some warmth
        saturated = saturated + 0.2 * np.sin(audio * np.pi * 2) * amount
        
        return saturated
    
    def apply_heavy_compression(self, audio, amount):
        """Apply heavy compression for loudness"""
        # RMS calculation
        window_size = int(0.01 * 48000)  # 10ms window
        rms = np.zeros_like(audio)
        
        for i in range(len(audio)):
            start = max(0, i - window_size)
            end = min(len(audio), i + window_size)
            rms[i] = np.sqrt(np.mean(audio[start:end]**2))
        
        # Compression curve
        threshold = 0.1
        ratio = 1 + amount * 10
        makeup_gain = 1 + amount * 3
        
        # Apply compression
        compressed = np.where(
            np.abs(audio) > threshold,
            np.sign(audio) * (threshold + (np.abs(audio) - threshold) / ratio),
            audio
        )
        
        # Apply makeup gain
        compressed *= makeup_gain
        
        return compressed
    
    def apply_kernel_loudness(self, audio, amount):
        """Apply aggressive loudness normalization"""
        # Multi-band loudness
        sample_rate = 48000
        
        # Split into bands
        b_low, a_low = signal.butter(2, 200/(sample_rate/2), 'low')
        b_mid, a_mid = signal.butter(2, [200/(sample_rate/2), 4000/(sample_rate/2)], 'band')
        b_high, a_high = signal.butter(2, 4000/(sample_rate/2), 'high')
        
        low = signal.filtfilt(b_low, a_low, audio)
        mid = signal.filtfilt(b_mid, a_mid, audio)
        high = signal.filtfilt(b_high, a_high, audio)
        
        # Apply different gains per band
        low *= (1 + amount * 2)
        mid *= (1 + amount * 1.5)
        high *= (1 + amount * 0.8)
        
        # Combine and normalize
        combined = low + mid + high
        
        # Aggressive RMS normalization
        target_rms = 0.3 + (amount * 0.4)
        current_rms = np.sqrt(np.mean(combined**2))
        if current_rms > 0:
            combined *= target_rms / current_rms
        
        return combined
    
    def apply_kernel_echo(self, audio, amount):
        """Apply aggressive echo with feedback"""
        chat_id = id(audio)  # Temporary identifier
        if chat_id not in self.delay_lines:
            self.delay_lines[chat_id] = deque(maxlen=int(0.5 * 48000))  # 500ms delay
        
        delay_line = self.delay_lines[chat_id]
        
        # Add current audio to delay line
        for sample in audio:
            delay_line.append(sample)
        
        # Create echo with feedback
        echo = np.zeros_like(audio)
        if len(delay_line) >= len(audio):
            echo = np.array(list(delay_line)[-len(audio):]) * amount
        
        # Add multiple echoes
        if len(delay_line) > len(audio) * 2:
            echo2 = np.array(list(delay_line)[-len(audio)*2:-len(audio)]) * (amount * 0.5)
            echo[:len(echo2)] += echo2
        
        return audio + echo * 1.5
    
    def apply_bit_crushing(self, audio, filters):
        """Apply bit crushing for digital distortion"""
        if filters.get('bit_depth', 16) < 16:
            # Reduce bit depth
            levels = 2 ** filters['bit_depth']
            audio = np.round(audio * levels) / levels
        
        # Sample rate reduction (aliasing)
        if filters.get('sample_rate', 48000) < 48000:
            # Simple decimation
            decimation = int(48000 / filters['sample_rate'])
            if decimation > 1:
                downsampled = audio[::decimation]
                # Upsample with hold
                audio = np.repeat(downsampled, decimation)[:len(audio)]
        
        return audio
    
    def apply_kernel_clipping(self, audio, threshold):
        """Apply soft and hard clipping for aggressive sound"""
        # Soft clip
        audio = np.tanh(audio / threshold) * threshold
        
        # Hard clip for peaks
        audio = np.clip(audio, -threshold * 1.2, threshold * 1.2)
        
        return audio
    
    def float_to_int16_with_dither(self, audio):
        """Convert float to int16 with dithering for better quality"""
        # Add dithering noise
        dither = np.random.uniform(-1/32768, 1/32768, audio.shape)
        audio_dithered = audio + dither
        
        # Scale and convert
        audio_scaled = audio_dithered * 32767
        return np.clip(audio_scaled, -32768, 32767).astype(np.int16)
    
    def set_kernel_preset(self, chat_id, preset_name='heavy'):
        """Set a kernel preset"""
        if chat_id not in self.filters:
            self.filters[chat_id] = self.create_filter_chain(chat_id)
        
        if preset_name in self.kernel_presets:
            preset = self.kernel_presets[preset_name]
            self.filters[chat_id].update(preset)
            return True
        return False
    
    def set_gain(self, chat_id, value):
        """Set gain value (0.0 to 5.0)"""
        if chat_id in self.filters:
            self.filters[chat_id]['gain'] = np.clip(value, 0.0, 5.0)
    
    def set_bass(self, chat_id, value):
        """Set bass boost (0.0 to 3.0)"""
        if chat_id in self.filters:
            self.filters[chat_id]['bass'] = np.clip(value, 0.0, 3.0)
    
    def set_distortion(self, chat_id, value):
        """Set distortion (0.0 to 2.0)"""
        if chat_id in self.filters:
            self.filters[chat_id]['distortion'] = np.clip(value, 0.0, 2.0)
    
    def set_saturation(self, chat_id, value):
        """Set saturation (0.0 to 2.0)"""
        if chat_id in self.filters:
            self.filters[chat_id]['saturation'] = np.clip(value, 0.0, 2.0)
    
    def set_compression(self, chat_id, value):
        """Set compression (0.0 to 1.5)"""
        if chat_id in self.filters:
            self.filters[chat_id]['compression'] = np.clip(value, 0.0, 1.5)
    
    def set_echo(self, chat_id, value):
        """Set echo effect (0.0 to 1.0)"""
        if chat_id in self.filters:
            self.filters[chat_id]['echo'] = np.clip(value, 0.0, 1.0)
    
    def set_loudness(self, chat_id, value):
        """Set loudness normalization (0.0 to 1.5)"""
        if chat_id in self.filters:
            self.filters[chat_id]['loudness'] = np.clip(value, 0.0, 1.5)
    
    def get_current_settings(self, chat_id):
        """Get current filter settings"""
        if chat_id in self.filters:
            return self.filters[chat_id]
        return None
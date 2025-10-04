import os
import re
import threading
import json
import html
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
import shutil
import subprocess
from math import floor
import hashlib

# --- START OF ASSETS ---

ADVANCED_STYLE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    --plyr-captions-font-size: 18px;
}
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #0f0f0f;
    color: #fff;
    overflow-x: hidden;
}
.header {
    background: #212121; height: 60px; position: fixed; top: 0; left: 0; right: 0;
    z-index: 1000; display: flex; align-items: center; padding: 0 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.header h1 { color: #ff6b6b; font-size: 20px; margin-right: auto; }
.toggle-sidebar {
    background: #3ea6ff; border: none; color: white; padding: 8px 16px;
    border-radius: 4px; cursor: pointer; font-size: 14px;
}
.toggle-sidebar:hover { background: #2196f3; }
.sidebar {
    position: fixed; top: 60px; left: 0; width: 300px; height: calc(100vh - 60px);
    background: #212121; border-right: 1px solid #3a3a3a; overflow-y: auto;
    transition: transform 0.3s ease; z-index: 999;
}
.sidebar.collapsed { transform: translateX(-100%); }
.sidebar-content { padding: 20px; }
.section-header {
    color: #ff6b6b; font-size: 16px; font-weight: bold; margin: 20px 0 10px 0;
    padding-bottom: 8px; border-bottom: 2px solid #3a3a3a;
}
.lesson-item {
    display: flex; align-items: center; padding: 12px 8px; margin: 4px 0;
    border-radius: 8px; cursor: pointer; transition: all 0.2s ease;
    background: #2a2a2a; text-decoration: none; color: #ccc;
}
.lesson-item:hover { background: #3a3a3a; color: #fff; transform: translateX(4px); }
.lesson-item.active { background: #3ea6ff; color: white; }
.lesson-number {
    background: #444; color: #fff; width: 24px; height: 24px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; margin-right: 12px; flex-shrink: 0;
}
.lesson-item.active .lesson-number { background: rgba(255,255,255,0.2); }
.lesson-title { flex: 1; font-size: 14px; line-height: 1.3; }
.main {
    margin-left: 300px; margin-top: 60px; padding: 20px;
    transition: margin-left 0.3s ease; min-height: calc(100vh - 60px);
}
.main.sidebar-collapsed { margin-left: 0; }
.lesson-header { margin-bottom: 20px; }
.lesson-title-main { font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 8px; }
.lesson-meta { color: #aaa; font-size: 14px; }
.video-container {
    background: #000; border-radius: 12px; overflow: hidden; margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3); position: relative;
    transition: max-width 0.3s ease;
}
.video-container .plyr { border-radius: 12px; }
.video-container .plyr__video-wrapper { border-radius: 12px; }
.plyr__captions { font-size: var(--plyr-captions-font-size, 18px) !important; }

/* Theater Mode */
body.theater-mode .main { max-width: 100%; padding: 20px 0; }
body.theater-mode .video-container { max-width: 90vw; max-height: calc(100vh - 100px); margin: 0 auto; }
body.theater-mode .sidebar { transform: translateX(-100%); }
body.theater-mode .main { margin-left: 0; }

/* Shortcuts Overlay */
.shortcuts-overlay {
    display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.8); z-index: 2000; justify-content: center; align-items: center;
}
.shortcuts-modal {
    background: #2a2a2a; color: #fff; padding: 30px; border-radius: 12px;
    width: 90%; max-width: 600px; box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    border: 1px solid #444;
}
.shortcuts-modal h2 { color: #ff6b6b; margin-bottom: 20px; text-align: center; }
.shortcuts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px 30px; }
.shortcut-item { display: flex; justify-content: space-between; }
.shortcut-key { font-weight: bold; color: #3ea6ff; background: #1a1a1a; padding: 2px 8px; border-radius: 4px; }

/* Enhanced Plyr styling */
.plyr--video { background: #000; }
.plyr__controls { background: linear-gradient(transparent, rgba(0,0,0,0.8)); color: #fff; }
.plyr__control--overlaid { background: rgba(62, 166, 255, 0.9); border: 3px solid rgba(255,255,255,0.3); }
.plyr__control--overlaid:hover { background: rgba(62, 166, 255, 1); }
.plyr__progress__buffer { color: rgba(255,255,255,0.3); }
.plyr__volume--display { color: #fff; }
.plyr__menu { background: rgba(0,0,0,0.9); border: 1px solid #3a3a3a; border-radius: 8px; }
.plyr__menu__container { background: transparent; }
.plyr__control[data-plyr="settings"] svg { animation: none; }
.plyr__tooltip { background: rgba(0,0,0,0.8); border-radius: 4px; color: #fff; }
.transcript {
    background: #1a1a1a; border: 1px solid #3a3a3a; border-radius: 12px;
    padding: 20px; margin-top: 20px; max-height: 400px; overflow-y: auto;
}
.transcript-header { color: #ff6b6b; font-size: 18px; font-weight: bold; margin-bottom: 15px; }
.transcript-content { line-height: 1.6; color: #ccc; white-space: pre-wrap; }
.search-container { margin-bottom: 20px; padding: 0 20px; }
.search-input {
    width: 100%; padding: 12px 16px; background: #2a2a2a;
    border: 1px solid #3a3a3a; border-radius: 8px; color: #fff; font-size: 14px;
}
.search-input:focus { outline: none; border-color: #3ea6ff; box-shadow: 0 0 0 2px rgba(62, 166, 255, 0.2); }
@media (max-width: 768px) {
    .sidebar { width: 100%; transform: translateX(-100%); }
    .main { margin-left: 0; }
    .lesson-title-main { font-size: 22px; }
}
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #1a1a1a; }
::-webkit-scrollbar-thumb { background: #3a3a3a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #4a4a4a; }
.back-link {
    display: inline-block; margin-top: 20px; padding: 10px 16px; background: #666;
    color: white; text-decoration: none; border-radius: 6px; transition: background 0.2s ease;
}
.back-link:hover { background: #777; }
"""

ADVANCED_SCRIPT_JS = """
class CoursePlayer {
    constructor(player) {
        this.player = player;
        this.settings = { 
            autoplay: false, 
            speed: 1, 
            volume: 1, 
            captions: true,
            quality: 'auto',
            captionSize: 18
        };
        this.init();
    }

    init() {
        this.loadSettings();
        this.applySavedState();
        this.setupEventListeners();
        this.buildSearchIndex();
        this.setupPlayerEvents();
        this.setupAdvancedShortcuts();
    }

    applySavedState() {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            document.querySelector('.sidebar')?.classList.add('collapsed');
            document.querySelector('.main')?.classList.add('sidebar-collapsed');
        }
        document.documentElement.style.setProperty('--plyr-captions-font-size', `${this.settings.captionSize}px`);
    }

    setupEventListeners() {
        document.querySelector('.toggle-sidebar')?.addEventListener('click', () => this.toggleSidebar());
    }

    setupPlayerEvents() {
        if (!this.player) return;
        this.player.on('ended', () => this.onVideoEnded());
        this.player.on('volumechange', () => { this.settings.volume = this.player.volume; this.saveSettings(); });
        this.player.on('ratechange', () => { this.settings.speed = this.player.speed; this.saveSettings(); });
        this.player.on('captionsenabled', () => { this.settings.captions = true; this.saveSettings(); });
        this.player.on('captionsdisabled', () => { this.settings.captions = false; this.saveSettings(); });
        this.player.on('ready', () => { this.player.volume = this.settings.volume; this.player.speed = this.settings.speed; });
        this.player.on('timeupdate', () => {
            if (this.player.duration) {
                const progress = (this.player.currentTime / this.player.duration) * 100;
                localStorage.setItem(`lesson_progress_${window.location.pathname}`, progress);
            }
        });
        this.player.on('loadedmetadata', () => {
            const savedProgress = localStorage.getItem(`lesson_progress_${window.location.pathname}`);
            if (savedProgress && savedProgress > 5) {
                const resumeTime = (parseFloat(savedProgress) / 100) * this.player.duration;
                if (resumeTime > 10 && resumeTime < this.player.duration - 30) {
                    if (confirm(`Resume from ${this.formatTime(resumeTime)}?`)) {
                        this.player.currentTime = resumeTime;
                    }
                }
            }
        });
    }

    setupAdvancedShortcuts() {
        const shortcutsHTML = `
            <div class="shortcuts-overlay" style="display: none;">
                <div class="shortcuts-modal">
                    <h2>Keyboard Shortcuts</h2>
                    <div class="shortcuts-grid">
                        <div class="shortcut-item"><span>Play / Pause</span><span class="shortcut-key">Space / K</span></div>
                        <div class="shortcut-item"><span>Mute / Unmute</span><span class="shortcut-key">M</span></div>
                        <div class="shortcut-item"><span>Seek Forward / Backward</span><span class="shortcut-key">→ / ←</span></div>
                        <div class="shortcut-item"><span>Increase / Decrease Volume</span><span class="shortcut-key">↑ / ↓</span></div>
                        <div class="shortcut-item"><span>Toggle Fullscreen</span><span class="shortcut-key">F</span></div>
                        <div class="shortcut-item"><span>Toggle Theater Mode</span><span class="shortcut-key">T</span></div>
                        <div class="shortcut-item"><span>Toggle Miniplayer (PiP)</span><span class="shortcut-key">I</span></div>
                        <div class="shortcut-item"><span>Toggle Captions</span><span class="shortcut-key">C</span></div>
                        <div class="shortcut-item"><span>Increase Caption Size</span><span class="shortcut-key">+</span></div>
                        <div class="shortcut-item"><span>Decrease Caption Size</span><span class="shortcut-key">-</span></div>
                        <div class="shortcut-item"><span>Increase / Decrease Speed</span><span class="shortcut-key">Shift + > / <</span></div>
                        <div class="shortcut-item"><span>Next / Previous Lesson</span><span class="shortcut-key">Shift + N / P</span></div>
                        <div class="shortcut-item"><span>Jump to Start / End</span><span class="shortcut-key">Home / End</span></div>
                        <div class="shortcut-item"><span>Jump to 10%-90%</span><span class="shortcut-key">1 - 9</span></div>
                        <div class="shortcut-item"><span>Focus Search Bar</span><span class="shortcut-key">/</span></div>
                        <div class="shortcut-item"><span>Close this overlay</span><span class="shortcut-key">Esc</span></div>
                    </div>
                </div>
            </div>`;
        document.body.insertAdjacentHTML('beforeend', shortcutsHTML);
        const overlay = document.querySelector('.shortcuts-overlay');
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) this.toggleShortcutsOverlay(false);
        });

        document.addEventListener('keydown', e => {
            if (!this.player && e.key !== '/') return;
            const activeEl = document.activeElement;
            if (activeEl && ['INPUT', 'TEXTAREA'].includes(activeEl.tagName)) {
                if (e.key === 'Escape') activeEl.blur();
                return;
            }

            const handle = (key, shift, ctrl, alt) => e.key.toLowerCase() === key && e.shiftKey === shift && e.ctrlKey === ctrl && e.altKey === alt;

            if (handle('?', true, false, false)) { e.preventDefault(); this.toggleShortcutsOverlay(); }
            if (overlay.style.display === 'flex' && handle('escape', false, false, false)) { e.preventDefault(); this.toggleShortcutsOverlay(false); }
            if (!this.player) return;

            switch (e.key.toLowerCase()) {
                case ' ': case 'k': e.preventDefault(); this.player.togglePlay(); break;
                case 'm': this.player.muted = !this.player.muted; break;
                case 'f': e.preventDefault(); this.player.fullscreen.toggle(); break;
                case 't': this.toggleTheaterMode(); break;
                case 'i': if (this.player.pip) this.player.pip = 'toggle'; break;
                case 'c': this.player.toggleCaptions(); break;
                case 'arrowleft': e.preventDefault(); this.player.rewind(e.shiftKey ? 10 : 5); break;
                case 'arrowright': e.preventDefault(); this.player.forward(e.shiftKey ? 10 : 5); break;
                case 'j': this.player.rewind(10); break;
                case 'l': this.player.forward(10); break;
                case 'arrowup': e.preventDefault(); this.player.increaseVolume(0.05); break;
                case 'arrowdown': e.preventDefault(); this.player.decreaseVolume(0.05); break;
                case 'home': e.preventDefault(); this.player.currentTime = 0; break;
                case 'end': e.preventDefault(); this.player.currentTime = this.player.duration; break;
                case '/': e.preventDefault(); document.querySelector('.search-input')?.focus(); break;
                case 'n': if (e.shiftKey) { e.preventDefault(); this.navigateToLesson('next'); } break;
                case 'p': if (e.shiftKey) { e.preventDefault(); this.navigateToLesson('previous'); } break;
                case '<': if (e.shiftKey) { this.player.speed = Math.max(0.25, this.player.speed - 0.25); } break;
                case '>': if (e.shiftKey) { this.player.speed = Math.min(3, this.player.speed + 0.25); } break;
                case '=': case '+': e.preventDefault(); this.changeCaptionSize(1); break;
                case '-': e.preventDefault(); this.changeCaptionSize(-1); break;
                default:
                    if (!isNaN(parseInt(e.key)) && parseInt(e.key) >= 0 && parseInt(e.key) <= 9) {
                        e.preventDefault();
                        this.player.currentTime = this.player.duration * (parseInt(e.key) / 10);
                    }
                    break;
            }
        });
    }
    
    toggleShortcutsOverlay(forceState) {
        const overlay = document.querySelector('.shortcuts-overlay');
        const shouldShow = forceState !== undefined ? forceState : overlay.style.display === 'none';
        overlay.style.display = shouldShow ? 'flex' : 'none';
    }

    toggleTheaterMode() {
        document.body.classList.toggle('theater-mode');
    }

    changeCaptionSize(delta) {
        this.settings.captionSize = Math.max(10, Math.min(32, this.settings.captionSize + delta));
        document.documentElement.style.setProperty('--plyr-captions-font-size', `${this.settings.captionSize}px`);
        this.saveSettings();
    }

    navigateToLesson(direction) {
        const active = document.querySelector('.lesson-item.active');
        if (!active) return;
        const target = direction === 'next' ? active.nextElementSibling : active.previousElementSibling;
        if (target && target.classList.contains('lesson-item')) {
            window.location.href = target.href;
        }
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const main = document.querySelector('.main');
        if (sidebar && main) {
            sidebar.classList.toggle('collapsed');
            main.classList.toggle('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        }
    }

    onVideoEnded() {
        localStorage.setItem(`lesson_completed_${window.location.pathname}`, 'true');
        if (this.settings.autoplay) this.navigateToLesson('next');
    }

    buildSearchIndex() {
        this.searchIndex = Array.from(document.querySelectorAll('.lesson-item')).map(lesson => ({
            element: lesson,
            title: lesson.querySelector('.lesson-title').textContent.toLowerCase(),
            section: lesson.dataset.section.toLowerCase()
        }));
        document.querySelector('.search-input')?.addEventListener('input', e => this.handleSearch(e.target.value));
    }

    handleSearch(query) {
        const searchTerm = query.toLowerCase().trim();
        const visibleSections = new Set();
        this.searchIndex.forEach(item => {
            const isVisible = !searchTerm || item.title.includes(searchTerm) || item.section.includes(searchTerm);
            item.element.style.display = isVisible ? 'flex' : 'none';
            if (isVisible) visibleSections.add(item.section);
        });
        document.querySelectorAll('.section-header').forEach(header => {
            header.style.display = visibleSections.has(header.textContent.toLowerCase()) ? 'block' : 'none';
        });
    }

    loadSettings() {
        try {
            const saved = localStorage.getItem('coursePlayerSettings');
            if (saved) this.settings = { ...this.settings, ...JSON.parse(saved) };
        } catch (e) { console.error('Failed to load settings:', e); }
    }

    saveSettings() {
        try {
            localStorage.setItem('coursePlayerSettings', JSON.stringify(this.settings));
        } catch (e) { console.error('Failed to save settings:', e); }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const videoElement = document.querySelector('#player');
    if (videoElement) {
        const player = new Plyr(videoElement, plyrConfig);
        window.coursePlayer = new CoursePlayer(player);
        window.player = player;
    } else {
        window.coursePlayer = new CoursePlayer(null);
    }
});

function updateLessonActive(newActiveHref) {
    document.querySelectorAll('.lesson-item').forEach(item => item.classList.remove('active'));
    const activeLesson = document.querySelector(`.lesson-item[href*="${newActiveHref}"]`);
    if (activeLesson) activeLesson.classList.add('active');
}
"""

# --- END OF ASSETS ---

def slugify(name):
    """Convert name to URL-safe slug"""
    return re.sub(r'[^a-zA-Z0-9]+', '-', str(name)).strip('-').lower() or "untitled"

def escape_html(text):
    """Escape HTML special characters"""
    return html.escape(str(text))

def get_file_hash(filepath):
    """Get MD5 hash of file for change detection"""
    try:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def should_regenerate_vtt(srt_path, vtt_path):
    """Check if VTT file needs regeneration"""
    if not os.path.exists(vtt_path):
        return True
    
    # Check if SRT is newer than VTT
    if os.path.getmtime(srt_path) > os.path.getmtime(vtt_path):
        return True
    
    return False

def convert_srt_to_vtt(srt_path):
    """Convert SRT subtitle to VTT format with caching"""
    vtt_path = Path(srt_path).with_suffix('.vtt')
    
    # Check if regeneration is needed
    if not should_regenerate_vtt(srt_path, vtt_path):
        print(f"Skipping VTT conversion for {Path(srt_path).name} (already exists and up to date)")
        return
    
    try:
        with open(srt_path, 'r', encoding='utf-8', errors='ignore') as srt_file:
            srt_content = srt_file.read()
        vtt_content = "WEBVTT\n\n" + re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', srt_content)
        with open(vtt_path, 'w', encoding='utf-8') as vtt_file:
            vtt_file.write(vtt_content)
        print(f"Converted {Path(srt_path).name} to {vtt_path.name}")
    except Exception as e:
        print(f"Warning: Could not convert SRT file {srt_path}: {e}")
        raise

def should_regenerate_thumbnails(video_path, sprite_path, vtt_path):
    """Check if thumbnails need regeneration"""
    # Both files must exist
    if not (os.path.exists(sprite_path) and os.path.exists(vtt_path)):
        return True
    
    # Check if video is newer than thumbnails
    video_mtime = os.path.getmtime(video_path)
    sprite_mtime = os.path.getmtime(sprite_path)
    vtt_mtime = os.path.getmtime(vtt_path)
    
    if video_mtime > sprite_mtime or video_mtime > vtt_mtime:
        return True
    
    # Check if files are not empty
    if os.path.getsize(sprite_path) == 0 or os.path.getsize(vtt_path) == 0:
        return True
    
    return False

def generate_thumbnails(video_path, status_callback):
    """Generate video thumbnails with smart caching"""
    lesson_dir = os.path.dirname(video_path)
    video_filename = os.path.basename(video_path)
    THUMB_WIDTH, SECONDS_PER_THUMB, SPRITE_COLUMNS = 160, 10, 10
    sprite_path = os.path.join(lesson_dir, "thumbnails.png")
    vtt_path = os.path.join(lesson_dir, "thumbnails.vtt")

    # Check if regeneration is needed
    if not should_regenerate_thumbnails(video_path, sprite_path, vtt_path):
        print(f"Skipping thumbnail generation for {video_filename} (already exists and up to date)")
        return True
    
    status_callback(f"Generating thumbnails for {video_filename}...")
    try:
        # Get video duration
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
             "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
            capture_output=True, text=True, check=True, timeout=30
        )
        duration = float(result.stdout.strip())
        
        if duration <= 0:
            print(f"Warning: Invalid video duration for {video_filename}")
            return False
        
        # Generate sprite
        subprocess.run(
            ["ffmpeg", "-i", str(video_path), 
             "-vf", f"fps=1/{SECONDS_PER_THUMB},scale={THUMB_WIDTH}:-1,tile={SPRITE_COLUMNS}x{SPRITE_COLUMNS}", 
             "-y", str(sprite_path)],
            capture_output=True, check=True, timeout=300
        )
        
        # Verify sprite was created
        if not os.path.exists(sprite_path) or os.path.getsize(sprite_path) == 0:
            print(f"Warning: Failed to create valid thumbnail sprite for {video_filename}")
            return False
        
        def format_time(s):
            return f"{floor(s/3600):02d}:{floor((s%3600)/60):02d}:{floor(s%60):02d}.{int((s-floor(s))*1000):03d}"
        
        num_thumbs = floor(duration / SECONDS_PER_THUMB)
        thumb_height = round(THUMB_WIDTH / (16/9))
        vtt_content = ["WEBVTT"]
        
        for i in range(num_thumbs):
            x = (i % SPRITE_COLUMNS) * THUMB_WIDTH
            y = floor(i / SPRITE_COLUMNS) * thumb_height
            vtt_content.extend([
                f"\n{i+1}", 
                f"{format_time(i*SECONDS_PER_THUMB)} --> {format_time((i+1)*SECONDS_PER_THUMB)}", 
                f"thumbnails.png#xywh={x},{y},{THUMB_WIDTH},{thumb_height}"
            ])
        
        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(vtt_content))
        
        print(f"Successfully generated thumbnails for {video_filename}")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"Timeout: Thumbnail generation took too long for {video_filename}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error for {video_filename}: {e}")
        return False
    except (FileNotFoundError, ValueError) as e:
        print(f"Could not process thumbnails for {video_filename}: {e}")
        return False

def should_regenerate_html(html_path, video_path, subtitle_paths, text_paths):
    """Check if HTML page needs regeneration"""
    if not os.path.exists(html_path):
        return True
    
    html_mtime = os.path.getmtime(html_path)
    
    # Check if video is newer
    if os.path.exists(video_path) and os.path.getmtime(video_path) > html_mtime:
        return True
    
    # Check if any subtitle is newer
    for sub_path in subtitle_paths:
        if os.path.exists(sub_path) and os.path.getmtime(sub_path) > html_mtime:
            return True
    
    # Check if any text file is newer
    for text_path in text_paths:
        if os.path.exists(text_path) and os.path.getmtime(text_path) > html_mtime:
            return True
    
    return False

def generate_advanced_lesson_page(section, lesson, files, relpath, output_dir, course_root, 
                                   lesson_number, total_lessons, generate_thumbs_flag, status_callback):
    """Generate lesson page with smart caching"""
    try:
        lesson_slug = f"coursera_rendered/{slugify(section)}_{slugify(lesson)}.html"
        html_path = os.path.join(output_dir, f"{slugify(section)}_{slugify(lesson)}.html")
        
        video_files = [f for f in files if f.lower().endswith((".mp4", ".webm", ".mov"))]
        subtitle_files = [f for f in files if f.lower().endswith((".srt", ".vtt"))]
        text_files = [f for f in files if f.lower().endswith(".txt")]
        
        # Build paths for change detection
        video_path_full = os.path.join(course_root, relpath, video_files[0]) if video_files else None
        subtitle_paths = [os.path.join(course_root, relpath, sf) for sf in subtitle_files]
        text_paths = [os.path.join(course_root, relpath, tf) for tf in text_files]
        
        # Check if HTML needs regeneration
        if not should_regenerate_html(html_path, video_path_full or "", subtitle_paths, text_paths):
            print(f"Skipping HTML generation for {lesson} (already exists and up to date)")
            return lesson_slug
        
        status_callback(f"Generating page for {lesson}...")
        
        plyr_config = {
            "controls": ['play-large', 'rewind', 'play', 'fast-forward', 'progress', 'current-time', 
                        'duration', 'mute', 'volume', 'captions', 'settings', 'pip', 'airplay', 'fullscreen'],
            "settings": ['captions', 'quality', 'speed', 'loop'],
            "speed": {"selected": 1, "options": [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]},
            "captions": {"active": True, "language": 'auto', "update": True},
            "keyboard": {"focused": True, "global": True},
            "tooltips": {"controls": True, "seek": True},
            "iconUrl": '/coursera_rendered/assets/plyr.svg',
            "storage": {"enabled": True, "key": 'plyr_course'},
            "ratio": '16:9',
        }

        # Handle thumbnails
        if generate_thumbs_flag and video_files and video_path_full:
            thumb_success = generate_thumbnails(video_path_full, status_callback)
            thumb_vtt_path = os.path.join(course_root, relpath, "thumbnails.vtt")
            if thumb_success and os.path.exists(thumb_vtt_path):
                plyr_config["previewThumbnails"] = {
                    "enabled": True, 
                    "src": f'/{Path(relpath, "thumbnails.vtt").as_posix()}'
                }
                print(f"Enabled preview thumbnails for {lesson}")

        # Build HTML
        html_content = [
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"<title>{escape_html(lesson)} - Course Player</title>",
            "<link rel='stylesheet' href='/coursera_rendered/assets/plyr.css'><link rel='stylesheet' href='/coursera_rendered/assets/styles.css'></head><body>",
            "<header class='header'><h1>📚 Course Player</h1><button class='toggle-sidebar'>☰ Navigation</button></header>",
            "<nav class='sidebar'><div class='sidebar-content'><div class='search-container'><input type='text' class='search-input' placeholder='🔍 Search lessons...'></div></div></nav>",
            f"<main class='main'><div class='lesson-header'><h1 class='lesson-title-main'>{escape_html(lesson)}</h1>",
            f"<div class='lesson-meta'>Lesson {lesson_number} of {total_lessons} • Section: {escape_html(section)}</div></div>"
        ]

        # Add video
        if video_files:
            video_path = Path(relpath, video_files[0]).as_posix()
            html_content.extend([
                "<div class='video-container'><video id='player' playsinline>", 
                f"<source src='/{video_path}' type='video/mp4'>"
            ])
            
            # Add subtitles
            for sub_file in subtitle_files:
                if sub_file.lower().endswith(".srt"):
                    try:
                        srt_full_path = os.path.join(course_root, relpath, sub_file)
                        convert_srt_to_vtt(srt_full_path)
                        sub_path = Path(relpath, Path(sub_file).with_suffix('.vtt').name).as_posix()
                    except Exception:
                        continue
                else:
                    sub_path = Path(relpath, sub_file).as_posix()
                html_content.append(f"<track kind='captions' label='English' srclang='en' src='/{sub_path}' default>")
            
            html_content.append("</video></div>")

        # Add transcripts
        for txt_file in text_files:
            try:
                txt_full_path = os.path.join(course_root, relpath, txt_file)
                with open(txt_full_path, 'r', encoding="utf-8", errors='ignore') as f:
                    transcript = f.read()
                html_content.extend([
                    "<div class='transcript'><div class='transcript-header'>📄 Transcript</div>", 
                    f"<div class='transcript-content'>{escape_html(transcript)}</div></div>"
                ])
            except Exception as e:
                print(f"Warning: Could not read transcript {txt_file}: {e}")

        # Footer
        html_content.extend([
            "<a href='/coursera_rendered/index.html' class='back-link'>← Back to Course Index</a></main>",
            "<script src='/coursera_rendered/assets/plyr.js'></script>",
            f"<script>const plyrConfig = {json.dumps(plyr_config)};</script>",
            "<script src='/coursera_rendered/assets/script.js'></script>",
            f"<script>updateLessonActive('{slugify(section)}_{slugify(lesson)}.html');</script>",
            "</body></html>"
        ])

        # Write HTML file
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_content))
        
        print(f"Generated HTML for {lesson}")
        return lesson_slug
        
    except Exception as e:
        print(f"Error generating lesson page for {lesson}: {e}")
        return None

def generate_advanced_index(course_structure, output_dir):
    """Generate index page with navigation"""
    try:
        sidebar_html = []
        lesson_counter = 1
        
        for section, lessons in course_structure.items():
            sidebar_html.append(f"<div class='section-header'>{escape_html(section)}</div>")
            for lesson, page_slug in lessons.items():
                if page_slug:
                    sidebar_html.extend([
                        f"<a href='/{page_slug}' class='lesson-item' data-section='{escape_html(section)}'>", 
                        f"<div class='lesson-number'>{lesson_counter}</div>", 
                        f"<div class='lesson-title'>{escape_html(lesson)}</div></a>"
                    ])
                    lesson_counter += 1
        
        sidebar_content = "\n".join(sidebar_html)
        
        # Update all lesson pages with sidebar
        for lessons in course_structure.values():
            for page_slug in lessons.values():
                if page_slug:
                    page_path = os.path.join(output_dir, page_slug.split('/')[-1])
                    try:
                        with open(page_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        placeholder = "<div class='search-container'><input type='text' class='search-input' placeholder='🔍 Search lessons...'></div>"
                        updated_content = content.replace(placeholder, placeholder + sidebar_content)
                        
                        with open(page_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                    except Exception as e:
                        print(f"Warning: Could not update sidebar for {page_slug}: {e}")

        # Generate main index
        html_content = [
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>Course Player</title>",
            "<link rel='stylesheet' href='/coursera_rendered/assets/styles.css'></head><body>",
            "<header class='header'><h1>📚 Course Player</h1><button class='toggle-sidebar'>☰</button></header>",
            "<nav class='sidebar'><div class='sidebar-content'><div class='search-container'><input type='text' class='search-input' placeholder='🔍 Search...'></div>",
            sidebar_content, "</div></nav>",
            "<main class='main'><div class='lesson-header'><h1>Welcome! 🎓</h1>",
            f"<div>You have {lesson_counter - 1} lessons ready. Select a lesson to begin.</div></div></main>",
            "<script src='/coursera_rendered/assets/script.js'></script></body></html>"
        ]
        
        with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write("\n".join(html_content))
        
        print("Generated index page successfully")
        
    except Exception as e:
        print(f"Error generating index page: {e}")

def create_server_scripts(output_dir):
    """Create server startup scripts"""
    parent_dir = os.path.dirname(output_dir)
    
    bat_content = f"""@echo off
title Coursera Local Server
cd /d "{parent_dir}"
echo Starting local server at http://localhost:8000
start http://localhost:8000/coursera_rendered/index.html
python -m http.server 8000
pause"""
    
    sh_content = f"""#!/bin/bash
cd "{parent_dir}"
echo "Starting local server at http://localhost:8000"
if command -v open &> /dev/null; then
    open http://localhost:8000/coursera_rendered/index.html
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000/coursera_rendered/index.html
fi
python3 -m http.server 8000 || python -m http.server 8000"""
    
    try:
        bat_path = os.path.join(output_dir, "server_windows.bat")
        sh_path = os.path.join(output_dir, "server_macos_linux.sh")
        
        with open(bat_path, "w") as f:
            f.write(bat_content)
        
        with open(sh_path, "w", newline='\n') as f:
            f.write(sh_content)
        
        os.chmod(sh_path, 0o755)
        print("Created server startup scripts")
        
    except Exception as e:
        print(f"Warning: Could not create server scripts: {e}")

def build_advanced_renderer(course_root, progress_callback, status_callback, done_callback, generate_thumbs_flag):
    """Main rendering function with smart caching"""
    try:
        # Validate FFmpeg if thumbnails requested
        if generate_thumbs_flag and not shutil.which("ffmpeg"):
            messagebox.showerror(
                "Dependency Missing", 
                "FFmpeg is required to generate thumbnails, but it was not found in your system's PATH.\n\n"
                "Please install FFmpeg or uncheck the thumbnail generation option."
            )
            done_callback(None)
            return

        output_dir = os.path.join(course_root, "coursera_rendered")
        assets_dir = os.path.join(output_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        # Copy Plyr assets
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            plyr_files = {
                'plyr.css': 'plyr.css', 
                'plyr.polyfilled.js': 'plyr.js', 
                'plyr.svg': 'plyr.svg'
            }
            
            for src_name, dest_name in plyr_files.items():
                src_path = os.path.join(script_dir, src_name)
                dest_path = os.path.join(assets_dir, dest_name)
                
                if not os.path.exists(src_path):
                    raise FileNotFoundError(f"Missing required file: {src_name}")
                
                # Only copy if source is newer or dest doesn't exist
                if not os.path.exists(dest_path) or os.path.getmtime(src_path) > os.path.getmtime(dest_path):
                    shutil.copy(src_path, dest_path)
                    print(f"Copied {src_name} to assets")
                else:
                    print(f"Skipped {src_name} (already up to date)")
                    
        except FileNotFoundError as e:
            messagebox.showerror(
                "Dependency Error", 
                f"Could not find a required Plyr file: {e}\n\n"
                "Please make sure 'plyr.css', 'plyr.polyfilled.js', and 'plyr.svg' "
                "are in the same folder as this script."
            )
            done_callback(None)
            return

        # Write CSS and JS
        css_path = os.path.join(assets_dir, "styles.css")
        js_path = os.path.join(assets_dir, "script.js")
        
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(ADVANCED_STYLE_CSS)
        
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(ADVANCED_SCRIPT_JS)
        
        print("Generated CSS and JS assets")

        # Find all lessons
        lessons_to_process = []
        for root, _, files in os.walk(course_root):
            if output_dir in root:
                continue
            
            relpath = os.path.relpath(root, course_root)
            if relpath != '.' and any(f.lower().endswith(('.mp4', '.webm', '.mov')) for f in files):
                parts = Path(relpath).parts
                if len(parts) >= 2:
                    lessons_to_process.append((parts[0], parts[-1], files, relpath))
        
        if not lessons_to_process:
            raise ValueError("No valid video lessons found in the selected directory.")

        lessons_to_process.sort(key=lambda x: (x[0], x[1]))
        total_lessons = len(lessons_to_process)
        course_structure = {}
        
        status_callback(f"Found {total_lessons} lessons to process...")
        
        # Process each lesson
        for i, (section, lesson, files, relpath) in enumerate(lessons_to_process, start=1):
            progress_callback(i, total_lessons, lesson)
            
            page = generate_advanced_lesson_page(
                section, lesson, files, relpath, output_dir, 
                course_root, i, total_lessons, generate_thumbs_flag, status_callback
            )
            
            if page:
                course_structure.setdefault(section, {})[lesson] = page

        # Generate index and scripts
        status_callback("Generating index page...")
        generate_advanced_index(course_structure, output_dir)
        
        status_callback("Creating server scripts...")
        create_server_scripts(output_dir)
        
        done_callback(output_dir)
        
    except Exception as e:
        print(f"Fatal error during rendering: {e}")
        messagebox.showerror("Rendering Failed", f"An error occurred during rendering:\n\n{e}")
        done_callback(None)

class AdvancedRendererApp(tk.Tk):
    """GUI Application for Course Renderer"""
    
    def __init__(self):
        super().__init__()
        self.title("Advanced Coursera Renderer")
        self.geometry("600x350")
        self.configure(bg='#2b2b2b')
        self.resizable(False, False)
        
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TLabel', foreground='#ffffff', background='#2b2b2b', font=('Arial', 10))
        style.configure('Title.TLabel', foreground='#ff6b6b', font=('Arial', 16, 'bold'))
        style.configure('TProgressbar', thickness=10, troughcolor='#3a3a3a', background='#3ea6ff')
        style.configure('TCheckbutton', foreground='#ccc', background='#2b2b2b', indicatorcolor='#555')
        style.map('TCheckbutton', 
                 indicatorcolor=[('selected', '#3ea6ff'), ('active', '#555')], 
                 background=[('active', '#3a3a3a')])

        self.create_widgets()

    def create_widgets(self):
        """Create GUI widgets"""
        main_frame = tk.Frame(self, bg='#2b2b2b', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(
            main_frame, 
            text="🎥 Advanced Coursera Renderer", 
            style='Title.TLabel'
        ).pack(pady=(0, 10))
        
        ttk.Label(
            main_frame, 
            text="Transform your course into a modern, offline player with smart caching.", 
            wraplength=550
        ).pack(pady=(0, 15))
        
        self.select_btn = tk.Button(
            main_frame, 
            text="📁 Select Course Folder & Render", 
            command=self.select_folder, 
            bg='#3ea6ff', 
            fg='white', 
            font=('Arial', 12, 'bold'), 
            relief='flat', 
            cursor='hand2', 
            borderwidth=0, 
            padx=15, 
            pady=8
        )
        self.select_btn.pack(pady=5)

        self.generate_thumbs_var = tk.BooleanVar(value=False)
        self.thumbs_check = ttk.Checkbutton(
            main_frame, 
            text="Generate Preview Thumbnails (requires FFmpeg)", 
            variable=self.generate_thumbs_var, 
            style='TCheckbutton'
        )
        self.thumbs_check.pack(pady=10)

        progress_frame = tk.Frame(main_frame, bg='#2b2b2b')
        progress_frame.pack(pady=15, fill='x', padx=20)
        
        self.progress = ttk.Progressbar(
            progress_frame, 
            orient="horizontal", 
            length=400, 
            mode="determinate", 
            style='TProgressbar'
        )
        self.progress.pack(pady=5, fill='x')
        
        self.status = ttk.Label(
            progress_frame, 
            text="Ready to transform your course! 🚀", 
            anchor='center'
        )
        self.status.pack(fill='x')

    def select_folder(self):
        """Handle folder selection"""
        folder = filedialog.askdirectory(
            title="Select Coursera Course Folder", 
            mustexist=True
        )
        if folder:
            self.start_rendering(folder)

    def start_rendering(self, folder):
        """Start the rendering process"""
        self.status.config(text="Starting advanced rendering... ⚡")
        self.progress["value"] = 0
        self.select_btn.config(state='disabled')
        self.thumbs_check.config(state='disabled')
        
        generate_thumbs = self.generate_thumbs_var.get()
        
        threading.Thread(
            target=build_advanced_renderer, 
            args=(folder, self.update_progress, self.update_status, self.done, generate_thumbs), 
            daemon=True
        ).start()

    def update_progress(self, current, total, lesson):
        """Update progress bar"""
        self.progress["maximum"] = total
        self.progress["value"] = current
        lesson_short = lesson[:35] + "..." if len(lesson) > 35 else lesson
        self.status.config(text=f"Processing: {lesson_short} ({current}/{total})")

    def update_status(self, text):
        """Update status text"""
        self.status.config(text=text)

    def done(self, output_dir_path):
        """Handle completion"""
        self.select_btn.config(state='normal')
        self.thumbs_check.config(state='normal')
        
        if output_dir_path:
            self.status.config(text="✅ Rendering complete! Ready to learn! 🎓")
            messagebox.showinfo(
                "Success!", 
                f"Rendering Complete!\n\n"
                f"Your course is ready in:\n{output_dir_path}\n\n"
                f"Double-click the 'server_windows.bat' or 'server_macos_linux.sh' file to start.\n\n"
                f"Tip: Files already processed were skipped to save time!"
            )
        else:
            self.status.config(text="❌ Rendering failed. Check console for details.")

if __name__ == "__main__":
    try:
        app = AdvancedRendererApp()
        app.mainloop()
    except Exception as e:
        print(f"Failed to start the application: {e}")
        input("Press Enter to exit...")
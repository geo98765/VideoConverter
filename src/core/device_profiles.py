"""Módulo para perfiles de dispositivo predefinidos"""
import json
import os

class DeviceProfiles:
    """Gestiona perfiles de codificación para diferentes dispositivos"""
    
    # Perfiles predefinidos
    PROFILES = {
        'youtube_1080p': {
            'name': 'YouTube 1080p',
            'description': 'Optimizado para YouTube en 1080p',
            'encoder': 'libx264',
            'preset': 'slow',
            'crf': 18,
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '192k',
            'format': 'mp4'
        },
        'youtube_4k': {
            'name': 'YouTube 4K',
            'description': 'Optimizado para YouTube en 4K',
            'encoder': 'libx264',
            'preset': 'slow',
            'crf': 18,
            'width': 3840,
            'height': 2160,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '192k',
            'format': 'mp4'
        },
        'instagram': {
            'name': 'Instagram',
            'description': 'Optimizado para Instagram (1:1)',
            'encoder': 'libx264',
            'preset': 'medium',
            'crf': 23,
            'width': 1080,
            'height': 1080,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '128k',
            'format': 'mp4'
        },
        'instagram_story': {
            'name': 'Instagram Stories',
            'description': 'Optimizado para Instagram Stories (9:16)',
            'encoder': 'libx264',
            'preset': 'medium',
            'crf': 23,
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '128k',
            'format': 'mp4'
        },
        'tiktok': {
            'name': 'TikTok',
            'description': 'Optimizado para TikTok',
            'encoder': 'libx264',
            'preset': 'medium',
            'crf': 23,
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '128k',
            'format': 'mp4'
        },
        'iphone': {
            'name': 'iPhone',
            'description': 'Compatible con iPhone',
            'encoder': 'libx264',
            'preset': 'medium',
            'crf': 23,
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '192k',
            'format': 'mp4'
        },
        'android': {
            'name': 'Android',
            'description': 'Compatible con Android',
            'encoder': 'libx264',
            'preset': 'medium',
            'crf': 23,
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '192k',
            'format': 'mp4'
        },
        'tv_4k': {
            'name': 'TV 4K',
            'description': 'Optimizado para televisores 4K',
            'encoder': 'libx264',
            'preset': 'slow',
            'crf': 18,
            'width': 3840,
            'height': 2160,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '320k',
            'format': 'mp4'
        },
        'web_streaming': {
            'name': 'Web Streaming',
            'description': 'Optimizado para streaming web',
            'encoder': 'libx264',
            'preset': 'fast',
            'crf': 23,
            'width': 1280,
            'height': 720,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '128k',
            'format': 'mp4'
        },
        'whatsapp': {
            'name': 'WhatsApp',
            'description': 'Optimizado para WhatsApp (comprimido)',
            'encoder': 'libx264',
            'preset': 'fast',
            'crf': 28,
            'width': 854,
            'height': 480,
            'fps': 30,
            'audio_codec': 'aac',
            'audio_bitrate': '96k',
            'format': 'mp4'
        }
    }
    
    @staticmethod
    def get_profile(profile_id):
        """Obtiene un perfil por ID"""
        return DeviceProfiles.PROFILES.get(profile_id)
    
    @staticmethod
    def get_all_profiles():
        """Obtiene todos los perfiles"""
        return DeviceProfiles.PROFILES
    
    @staticmethod
    def get_profile_list():
        """Obtiene lista de nombres de perfiles"""
        return [(key, profile['name']) for key, profile in DeviceProfiles.PROFILES.items()]
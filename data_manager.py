#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير البيانات والتخزين - KEVIN BOT
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional
import config

class DataManager:
    """مدير حفظ واستعادة البيانات"""
    
    def __init__(self):
        self.data_dir = "bot_data"
        self.sessions_dir = os.path.join(self.data_dir, "sessions")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.stats_file = os.path.join(self.data_dir, "stats.json")
        self.reports_file = os.path.join(self.data_dir, "saved_reports.json")
        
        # إنشاء المجلدات إذا لم تكن موجودة
        self.ensure_directories()
    
    def ensure_directories(self):
        """إنشاء المجلدات المطلوبة"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    # ==================== إدارة المستخدمين ====================
    
    def load_users(self) -> Dict:
        """تحميل بيانات المستخدمين"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات المستخدمين: {e}")
        
        return {}
    
    def save_users(self, users_data: Dict):
        """حفظ بيانات المستخدمين"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات المستخدمين: {e}")
            return False
    
    # ==================== إدارة الجلسات ====================
    
    def save_session(self, session_id: str, session_string: str, user_info: Dict) -> bool:
        """حفظ جلسة جديدة"""
        try:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.session")
            
            # حفظ session string في ملف
            with open(session_file, 'w', encoding='utf-8') as f:
                f.write(session_string)
            
            # حفظ معلومات الجلسة
            info_file = os.path.join(self.sessions_dir, f"{session_id}_info.json")
            session_info = {
                "session_id": session_id,
                "user_info": user_info,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "reports_sent": 0,
                "last_used": datetime.now().isoformat()
            }
            
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ الجلسة: {e}")
            return False
    
    def load_sessions(self) -> Dict:
        """تحميل جميع الجلسات"""
        sessions = {}
        
        try:
            if not os.path.exists(self.sessions_dir):
                return sessions
            
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('_info.json'):
                    session_id = filename.replace('_info.json', '')
                    info_file = os.path.join(self.sessions_dir, filename)
                    session_file = os.path.join(self.sessions_dir, f"{session_id}.session")
                    
                    if os.path.exists(session_file):
                        # تحميل معلومات الجلسة
                        with open(info_file, 'r', encoding='utf-8') as f:
                            session_info = json.load(f)
                        
                        # تحميل session string
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session_string = f.read().strip()
                        
                        sessions[session_id] = {
                            **session_info,
                            "session_string": session_string,
                            "session_file": session_file
                        }
        
        except Exception as e:
            print(f"❌ خطأ في تحميل الجلسات: {e}")
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """حذف جلسة"""
        try:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.session")
            info_file = os.path.join(self.sessions_dir, f"{session_id}_info.json")
            
            if os.path.exists(session_file):
                os.remove(session_file)
            
            if os.path.exists(info_file):
                os.remove(info_file)
            
            return True
        except Exception as e:
            print(f"❌ خطأ في حذف الجلسة: {e}")
            return False
    
    def get_sessions_count(self) -> int:
        """الحصول على عدد الجلسات"""
        try:
            if not os.path.exists(self.sessions_dir):
                return 0
            
            session_files = [f for f in os.listdir(self.sessions_dir) if f.endswith('.session')]
            return len(session_files)
        except:
            return 0
    
    # ==================== إدارة الإحصائيات ====================
    
    def load_stats(self) -> Dict:
        """تحميل الإحصائيات"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل الإحصائيات: {e}")
        
        return {
            "total_reports": 0,
            "successful_reports": 0,
            "failed_reports": 0,
            "sessions_added": 0,
            "last_reset": datetime.now().isoformat()
        }
    
    def save_stats(self, stats_data: Dict):
        """حفظ الإحصائيات"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ الإحصائيات: {e}")
            return False
    
    # ==================== إدارة البلاغات المحفوظة ====================
    
    def load_saved_reports(self) -> Dict:
        """تحميل البلاغات المحفوظة"""
        try:
            if os.path.exists(self.reports_file):
                with open(self.reports_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل البلاغات المحفوظة: {e}")
        
        return {}
    
    def save_saved_reports(self, reports_data: Dict):
        """حفظ البلاغات المحفوظة"""
        try:
            with open(self.reports_file, 'w', encoding='utf-8') as f:
                json.dump(reports_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ البلاغات المحفوظة: {e}")
            return False
    
    # ==================== إعادة ضبط المصنع ====================
    
    def factory_reset(self) -> bool:
        """إعادة ضبط المصنع - حذف جميع البيانات"""
        try:
            # إنشاء نسخة احتياطية قبل الحذف
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.data_dir):
                shutil.copytree(self.data_dir, backup_dir)
                print(f"✅ تم إنشاء نسخة احتياطية في: {backup_dir}")
            
            # حذف مجلد البيانات الجديد
            if os.path.exists(self.data_dir):
                shutil.rmtree(self.data_dir)
                print("✅ تم حذف مجلد البيانات الجديد")
            
            # حذف الملفات والمجلدات القديمة
            old_files_and_dirs = [
                "sessions.json",           # ملف الجلسات القديم
                "sessions",                # مجلد الجلسات القديم
                "authorized_users.json",   # ملف المستخدمين القديم
                "saved_reports.json"       # ملف البلاغات المحفوظة القديم
            ]
            
            for item in old_files_and_dirs:
                item_path = os.path.join(".", item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"✅ تم حذف الملف: {item}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        print(f"✅ تم حذف المجلد: {item}")
                except Exception as e:
                    print(f"⚠️ لم يتم حذف {item}: {e}")
            
            # حذف ملفات الجلسات المفردة
            import glob
            session_files = glob.glob("session_*.txt")
            for session_file in session_files:
                try:
                    os.remove(session_file)
                    print(f"✅ تم حذف ملف الجلسة: {session_file}")
                except Exception as e:
                    print(f"⚠️ لم يتم حذف {session_file}: {e}")
            
            # حذف ملفات السجلات
            log_files = ["kevin_bot.log"]
            for log_file in log_files:
                try:
                    if os.path.exists(log_file):
                        os.remove(log_file)
                        print(f"✅ تم حذف ملف السجل: {log_file}")
                except Exception as e:
                    print(f"⚠️ لم يتم حذف {log_file}: {e}")
            
            # إعادة إنشاء المجلدات الفارغة
            self.ensure_directories()
            
            print("✅ تم إعادة ضبط المصنع بنجاح - تم حذف جميع البيانات!")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إعادة ضبط المصنع: {e}")
            return False
    
    def get_data_size(self) -> str:
        """الحصول على حجم البيانات"""
        try:
            total_size = 0
            
            if os.path.exists(self.data_dir):
                for dirpath, dirnames, filenames in os.walk(self.data_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(filepath)
            
            # تحويل إلى وحدة مناسبة
            if total_size < 1024:
                return f"{total_size} بايت"
            elif total_size < 1024 * 1024:
                return f"{total_size / 1024:.1f} كيلوبايت"
            else:
                return f"{total_size / (1024 * 1024):.1f} ميجابايت"
                
        except Exception as e:
            return "غير معروف"
    
    def create_backup(self) -> str:
        """إنشاء نسخة احتياطية"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"backup_{timestamp}"
            
            if os.path.exists(self.data_dir):
                shutil.copytree(self.data_dir, backup_dir)
                return backup_dir
            
            return ""
        except Exception as e:
            print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
            return ""

# إنشاء مثيل عام
data_manager = DataManager()
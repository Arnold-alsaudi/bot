#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير الجلسات المحدث - KEVIN BOT
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from telethon import TelegramClient
from telethon.sessions import StringSession
import config
from data_manager import data_manager

class SessionManager:
    """مدير الجلسات المحدث مع دعم التخزين الدائم"""
    
    def __init__(self):
        self.active_sessions = {}
        self.load_all_sessions()
    
    def load_all_sessions(self):
        """تحميل جميع الجلسات من التخزين"""
        try:
            sessions_data = data_manager.load_sessions()
            self.active_sessions = sessions_data
            print(f"✅ تم تحميل {len(sessions_data)} جلسة")
        except Exception as e:
            print(f"❌ خطأ في تحميل الجلسات: {e}")
            self.active_sessions = {}
    
    def add_session_string(self, session_string: str) -> bool:
        """إضافة جلسة من session string (الطريقة القديمة)"""
        try:
            # إنشاء معرف جلسة
            import hashlib
            session_id = hashlib.md5(session_string.encode()).hexdigest()[:12]
            
            # معلومات افتراضية
            user_info = {
                "id": "unknown",
                "first_name": "مستخدم",
                "last_name": "",
                "username": "",
                "phone": "غير محدد"
            }
            
            # حفظ الجلسة
            success = data_manager.save_session(session_id, session_string, user_info)
            
            if success:
                # إضافة للجلسات النشطة
                self.active_sessions[session_id] = {
                    "session_id": session_id,
                    "user_info": user_info,
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                    "reports_sent": 0,
                    "last_used": datetime.now().isoformat(),
                    "session_string": session_string,
                    "session_file": f"bot_data/sessions/{session_id}.session"
                }
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ خطأ في إضافة الجلسة: {e}")
            return False
    
    def remove_session(self, session_id: str) -> bool:
        """حذف جلسة"""
        try:
            # حذف من التخزين
            success = data_manager.delete_session(session_id)
            
            if success and session_id in self.active_sessions:
                del self.active_sessions[session_id]
                return True
            
            return success
            
        except Exception as e:
            print(f"❌ خطأ في حذف الجلسة: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """الحصول على معلومات جلسة"""
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> Dict:
        """الحصول على جميع الجلسات"""
        return self.active_sessions.copy()
    
    def get_active_sessions_count(self) -> int:
        """عدد الجلسات النشطة"""
        return len([s for s in self.active_sessions.values() if s.get('status') == 'active'])
    
    def get_total_sessions_count(self) -> int:
        """إجمالي عدد الجلسات"""
        return len(self.active_sessions)
    
    async def test_session(self, session_id: str) -> tuple:
        """اختبار جلسة"""
        if session_id not in self.active_sessions:
            return False, "الجلسة غير موجودة"
        
        session_data = self.active_sessions[session_id]
        
        try:
            client = TelegramClient(
                StringSession(session_data['session_string']),
                config.API_ID,
                config.API_HASH
            )
            
            await client.start()
            me = await client.get_me()
            await client.disconnect()
            
            # تحديث حالة الجلسة
            session_data['status'] = 'active'
            session_data['last_used'] = datetime.now().isoformat()
            
            return True, f"✅ الجلسة تعمل - {me.first_name}"
            
        except Exception as e:
            # تحديث حالة الجلسة
            session_data['status'] = 'inactive'
            return False, f"❌ الجلسة لا تعمل: {str(e)}"
    
    def update_session_stats(self, session_id: str, reports_sent: int = 1):
        """تحديث إحصائيات الجلسة"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['reports_sent'] += reports_sent
            self.active_sessions[session_id]['last_used'] = datetime.now().isoformat()
    
    def get_sessions_summary(self) -> str:
        """ملخص الجلسات"""
        total = len(self.active_sessions)
        active = len([s for s in self.active_sessions.values() if s.get('status') == 'active'])
        inactive = total - active
        
        return f"""
📊 **ملخص الجلسات:**
• إجمالي الجلسات: {total}
• الجلسات النشطة: {active}
• الجلسات غير النشطة: {inactive}
        """
    
    def get_detailed_sessions_info(self) -> List[Dict]:
        """معلومات مفصلة عن الجلسات"""
        sessions_info = []
        
        for session_id, session_data in self.active_sessions.items():
            user_info = session_data.get('user_info', {})
            sessions_info.append({
                'id': session_id,
                'name': f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip(),
                'username': user_info.get('username', ''),
                'phone': user_info.get('phone', ''),
                'status': session_data.get('status', 'unknown'),
                'reports_sent': session_data.get('reports_sent', 0),
                'created_at': session_data.get('created_at', ''),
                'last_used': session_data.get('last_used', '')
            })
        
        return sessions_info

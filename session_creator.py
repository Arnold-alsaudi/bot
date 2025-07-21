#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منشئ الجلسات من داخل البوت - KEVIN BOT
"""

import asyncio
import random
import string
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberInvalidError
from telethon.sessions import StringSession
import config
from data_manager import data_manager

class SessionCreator:
    """منشئ الجلسات التفاعلي"""
    
    def __init__(self):
        self.active_creations = {}  # {user_id: creation_data}
    
    def generate_session_id(self) -> str:
        """إنشاء معرف جلسة عشوائي"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    async def start_session_creation(self, user_id: int, bot_client) -> str:
        """بدء عملية إنشاء جلسة جديدة"""
        
        # إنشاء معرف جلسة جديد
        session_id = self.generate_session_id()
        
        # إنشاء عميل تليجرام جديد
        client = TelegramClient(
            StringSession(),
            config.API_ID,
            config.API_HASH
        )
        
        # حفظ بيانات الإنشاء
        self.active_creations[user_id] = {
            "session_id": session_id,
            "client": client,
            "step": "waiting_phone",
            "phone": None,
            "phone_code_hash": None
        }
        
        return session_id
    
    async def process_phone_number(self, user_id: int, phone: str, bot_client) -> tuple:
        """معالجة رقم الهاتف"""
        if user_id not in self.active_creations:
            return False, "❌ لم يتم العثور على عملية إنشاء جلسة نشطة"
        
        creation_data = self.active_creations[user_id]
        client = creation_data["client"]
        
        try:
            # تنظيف رقم الهاتف
            phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not phone.startswith("+"):
                phone = "+" + phone
            
            # إرسال كود التحقق
            await client.connect()
            sent_code = await client.send_code_request(phone)
            
            # تحديث بيانات الإنشاء
            creation_data.update({
                "phone": phone,
                "phone_code_hash": sent_code.phone_code_hash,
                "step": "waiting_code"
            })
            
            return True, f"✅ تم إرسال كود التحقق إلى {phone}\n\nأرسل الكود المكون من 5 أرقام:"
            
        except PhoneNumberInvalidError:
            return False, "❌ رقم الهاتف غير صحيح. تأكد من الرقم وحاول مرة أخرى."
        except Exception as e:
            return False, f"❌ خطأ في إرسال الكود: {str(e)}"
    
    async def process_verification_code(self, user_id: int, code: str, bot_client) -> tuple:
        """معالجة كود التحقق"""
        if user_id not in self.active_creations:
            return False, "❌ لم يتم العثور على عملية إنشاء جلسة نشطة"
        
        creation_data = self.active_creations[user_id]
        client = creation_data["client"]
        
        try:
            # تنظيف الكود
            code = code.strip().replace(" ", "").replace("-", "")
            
            # تسجيل الدخول بالكود
            await client.sign_in(
                phone=creation_data["phone"],
                code=code,
                phone_code_hash=creation_data["phone_code_hash"]
            )
            
            # الحصول على معلومات المستخدم
            me = await client.get_me()
            user_info = {
                "id": me.id,
                "first_name": me.first_name or "",
                "last_name": me.last_name or "",
                "username": me.username or "",
                "phone": creation_data["phone"]
            }
            
            # الحصول على session string
            session_string = client.session.save()
            
            # حفظ الجلسة
            session_id = creation_data["session_id"]
            success = data_manager.save_session(session_id, session_string, user_info)
            
            if success:
                # تنظيف البيانات المؤقتة
                await client.disconnect()
                del self.active_creations[user_id]
                
                return True, f"""
✅ **تم إنشاء الجلسة بنجاح!**

📱 **معلومات الحساب:**
• الاسم: {user_info['first_name']} {user_info['last_name']}
• اليوزر: @{user_info['username'] or 'غير محدد'}
• الهاتف: {user_info['phone']}
• معرف الجلسة: `{session_id}`

🎉 الحساب جاهز للاستخدام في البلاغات!
                """
            else:
                return False, "❌ خطأ في حفظ الجلسة"
                
        except SessionPasswordNeededError:
            # الحساب محمي بكلمة مرور
            creation_data["step"] = "waiting_password"
            return True, "🔐 الحساب محمي بكلمة مرور التحقق بخطوتين\n\nأرسل كلمة المرور:"
            
        except PhoneCodeInvalidError:
            return False, "❌ كود التحقق غير صحيح. حاول مرة أخرى."
        except Exception as e:
            return False, f"❌ خطأ في التحقق: {str(e)}"
    
    async def process_password(self, user_id: int, password: str, bot_client) -> tuple:
        """معالجة كلمة مرور التحقق بخطوتين"""
        if user_id not in self.active_creations:
            return False, "❌ لم يتم العثور على عملية إنشاء جلسة نشطة"
        
        creation_data = self.active_creations[user_id]
        client = creation_data["client"]
        
        try:
            # تسجيل الدخول بكلمة المرور
            await client.sign_in(password=password)
            
            # الحصول على معلومات المستخدم
            me = await client.get_me()
            user_info = {
                "id": me.id,
                "first_name": me.first_name or "",
                "last_name": me.last_name or "",
                "username": me.username or "",
                "phone": creation_data["phone"]
            }
            
            # الحصول على session string
            session_string = client.session.save()
            
            # حفظ الجلسة
            session_id = creation_data["session_id"]
            success = data_manager.save_session(session_id, session_string, user_info)
            
            if success:
                # تنظيف البيانات المؤقتة
                await client.disconnect()
                del self.active_creations[user_id]
                
                return True, f"""
✅ **تم إنشاء الجلسة بنجاح!**

📱 **معلومات الحساب:**
• الاسم: {user_info['first_name']} {user_info['last_name']}
• اليوزر: @{user_info['username'] or 'غير محدد'}
• الهاتف: {user_info['phone']}
• معرف الجلسة: `{session_id}`

🎉 الحساب جاهز للاستخدام في البلاغات!
                """
            else:
                return False, "❌ خطأ في حفظ الجلسة"
                
        except Exception as e:
            return False, f"❌ كلمة المرور غير صحيحة: {str(e)}"
    
    def cancel_creation(self, user_id: int):
        """إلغاء عملية إنشاء الجلسة"""
        if user_id in self.active_creations:
            try:
                client = self.active_creations[user_id]["client"]
                asyncio.create_task(client.disconnect())
            except:
                pass
            
            del self.active_creations[user_id]
            return True
        return False
    
    def get_creation_step(self, user_id: int) -> str:
        """الحصول على خطوة الإنشاء الحالية"""
        if user_id in self.active_creations:
            return self.active_creations[user_id]["step"]
        return None

# إنشاء مثيل عام
session_creator = SessionCreator()
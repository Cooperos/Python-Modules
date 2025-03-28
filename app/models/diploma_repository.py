from datetime import datetime
from .database import Database
import json

class DiplomaRepository:    
    @classmethod
    def get_all_topics(cls):
        try:
            topics_data = Database.execute_query("""
                SELECT id, code, title, description, created_at
                FROM wds_topic
                ORDER BY title
            """)
            
            topics = []
            if topics_data:
                for row in topics_data:
                    topics.append({
                        "id": row[0],
                        "code": row[1],
                        "title": row[2],
                        "description": row[3],
                        "created_at": row[4]
                    })
            
            return topics
        except Exception as e:
            print(f"Ошибка получения списка тем: {e}")
            return []
    
    @classmethod
    def get_topic_by_id(cls, topic_id):
        try:
            topic_data = Database.execute_query("""
                SELECT id, code, title, description, created_at
                FROM wds_topic
                WHERE id = %s
            """, (topic_id,))
            
            if topic_data and len(topic_data) > 0:
                topic = {
                    "id": topic_data[0][0],
                    "code": topic_data[0][1],
                    "title": topic_data[0][2],
                    "description": topic_data[0][3],
                    "created_at": topic_data[0][4]
                }
                return topic
            else:
                print(f"Тема с ID {topic_id} не найдена")
                return None
        except Exception as e:
            print(f"Ошибка получения темы: {e}")
            return None
            
    @classmethod
    def get_all_users(cls):
        try:
            users_data = Database.execute_query("""
                SELECT id, username, first_name, last_name, middle_name, email, created_at
                FROM wds_user
                WHERE enabled = true
                ORDER BY last_name, first_name
            """)
            
            users = []
            if users_data:
                for row in users_data:
                    users.append({
                        "id": row[0],
                        "username": row[1],
                        "first_name": row[2],
                        "last_name": row[3],
                        "middle_name": row[4],
                        "email": row[5],
                        "created_at": row[6],
                        "full_name": f"{row[3] or ''} {row[2] or ''} {row[4] or ''}".strip()
                    })
            
            return users
        except Exception as e:
            print(f"Ошибка получения списка пользователей: {e}")
            return []
            
    @classmethod
    def get_user_by_id(cls, user_id):
        try:
            user_data = Database.execute_query("""
                SELECT id, username, first_name, last_name, middle_name, email, created_at
                FROM wds_user
                WHERE id = %s AND enabled = true
            """, (user_id,))
            
            if user_data and len(user_data) > 0:
                user = {
                    "id": user_data[0][0],
                    "username": user_data[0][1],
                    "first_name": user_data[0][2],
                    "last_name": user_data[0][3],
                    "middle_name": user_data[0][4],
                    "email": user_data[0][5],
                    "created_at": user_data[0][6],
                    "full_name": f"{user_data[0][3] or ''} {user_data[0][2] or ''} {user_data[0][4] or ''}".strip()
                }
                return user
            else:
                print(f"Пользователь с ID {user_id} не найден")
                return None
        except Exception as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
    
    @classmethod
    def get_all_diplomas(cls):
        try:
            diploma_data = Database.execute_query("""
                SELECT d.id, d.created_at, d.grade, d.topic_id, d.user_id, d.tasks,
                       t.title as topic_title, t.code as topic_code,
                       u.first_name, u.last_name, u.middle_name
                FROM wds_diploma d
                JOIN wds_topic t ON d.topic_id = t.id
                JOIN wds_user u ON d.user_id = u.id
                ORDER BY d.created_at DESC
            """)
            
            diplomas = []
            if diploma_data:
                for row in diploma_data:
                    full_name = f"{row[9] or ''} {row[8] or ''} {row[10] or ''}".strip()
                    tasks = json.loads(row[5]) if row[5] else {}
                    diplomas.append({
                        "id": row[0],
                        "created_at": row[1],
                        "grade": row[2],
                        "topic_id": row[3],
                        "user_id": row[4],
                        "tasks": tasks,
                        "topic_title": row[6],
                        "topic_code": row[7],
                        "student_name": full_name
                    })
            
            return diplomas
        except Exception as e:
            print(f"Ошибка получения списка дипломов: {e}")
            return []
            
    @classmethod
    def get_diploma_by_id(cls, diploma_id):
        try:
            diploma_data = Database.execute_query("""
                SELECT d.id, d.created_at, d.grade, d.topic_id, d.user_id, d.tasks,
                       t.title as topic_title, t.code as topic_code, t.description as topic_description,
                       u.first_name, u.last_name, u.middle_name, u.email
                FROM wds_diploma d
                JOIN wds_topic t ON d.topic_id = t.id
                JOIN wds_user u ON d.user_id = u.id
                WHERE d.id = %s
            """, (diploma_id,))
            
            if diploma_data and len(diploma_data) > 0:
                full_name = f"{diploma_data[0][11] or ''} {diploma_data[0][10] or ''} {diploma_data[0][12] or ''}".strip()
                
                diploma = {
                    "id": diploma_data[0][0],
                    "created_at": diploma_data[0][1],
                    "grade": diploma_data[0][2],
                    "topic_id": diploma_data[0][3],
                    "user_id": diploma_data[0][4],
                    "tasks": diploma_data[0][5],
                    "topic_title": diploma_data[0][6],
                    "topic_code": diploma_data[0][7],
                    "topic_description": diploma_data[0][8],
                    "student": {
                        "id": diploma_data[0][4],
                        "first_name": diploma_data[0][10],
                        "last_name": diploma_data[0][11],
                        "middle_name": diploma_data[0][12],
                        "email": diploma_data[0][13],
                        "full_name": full_name
                    }
                }
                if diploma["tasks"] and isinstance(diploma["tasks"], list):
                    assignments_results = []
                    for task in diploma["tasks"]:
                        if isinstance(task, dict):
                            task_data = {
                                "name": task.get("name", ""),
                                "score": task.get("grade", 0),
                                "time_spent": task.get("time", 0)
                            }
                            assignments_results.append(task_data)
                    
                    diploma["assignments_results"] = assignments_results
                
                return diploma
            else:
                print(f"Диплом с ID {diploma_id} не найден")
                return None
        except Exception as e:
            print(f"Ошибка получения диплома: {e}")
            return None
    
    @classmethod
    def get_diplomas_by_user_id(cls, user_id):
        try:
            diploma_data = Database.execute_query("""
                SELECT d.id, d.created_at, d.grade, d.topic_id, d.tasks,
                       t.title as topic_title, t.code as topic_code
                FROM wds_diploma d
                JOIN wds_topic t ON d.topic_id = t.id
                WHERE d.user_id = %s
                ORDER BY d.created_at DESC
            """, (user_id,))
            
            diplomas = []
            if diploma_data:
                for row in diploma_data:
                    diplomas.append({
                        "id": row[0],
                        "created_at": row[1],
                        "grade": row[2],
                        "topic_id": row[3],
                        "tasks": row[4],
                        "topic_title": row[5],
                        "topic_code": row[6]
                    })
            
            return diplomas
        except Exception as e:
            print(f"Ошибка получения дипломов пользователя: {e}")
            return []
    
    @classmethod
    def get_performed_tasks_by_user_id(cls, user_id):
        try:
            tasks_data = Database.execute_query("""
                SELECT pt.id, pt.created_at, pt.updated_at, pt.grade, pt.status, 
                       pt.system_grade_failed, pt.task_id, pt.mentor_id, 
                       pt.start_date, pt.end_date,
                       u.first_name, u.last_name, u.middle_name
                FROM wds_perfomed_task pt
                LEFT JOIN wds_user u ON pt.mentor_id = u.id
                WHERE pt.user_id = %s
                ORDER BY pt.created_at DESC
            """, (user_id,))
            
            tasks = []
            if tasks_data:
                for row in tasks_data:
                    mentor_name = None
                    if row[7]:  # если есть mentor_id
                        mentor_name = f"{row[11] or ''} {row[10] or ''} {row[12] or ''}".strip()
                    
                    tasks.append({
                        "id": row[0],
                        "created_at": row[1],
                        "updated_at": row[2],
                        "grade": row[3],
                        "status": row[4],
                        "system_grade_failed": row[5],
                        "task_id": row[6],
                        "mentor_id": row[7],
                        "start_date": row[8],
                        "end_date": row[9],
                        "mentor_name": mentor_name
                    })
            
            return tasks
        except Exception as e:
            print(f"Ошибка получения заданий пользователя: {e}")
            return []
    
    @classmethod
    def get_task_by_id(cls, task_id):
        try:
            task_data = Database.execute_query("""
                SELECT id, created_at, updated_at, grade, status, 
                       system_grade_failed, task_id, user_id, mentor_id,
                       start_date, end_date
                FROM wds_perfomed_task
                WHERE id = %s
            """, (task_id,))
            
            if task_data and len(task_data) > 0:
                task = {
                    "id": task_data[0][0],
                    "created_at": task_data[0][1],
                    "updated_at": task_data[0][2],
                    "grade": task_data[0][3],
                    "status": task_data[0][4],
                    "system_grade_failed": task_data[0][5],
                    "task_id": task_data[0][6],
                    "user_id": task_data[0][7],
                    "mentor_id": task_data[0][8],
                    "start_date": task_data[0][9],
                    "end_date": task_data[0][10]
                }
                
                if task["user_id"]:
                    user = cls.get_user_by_id(task["user_id"])
                    if user:
                        task["student"] = user
                
                if task["mentor_id"]:
                    mentor = cls.get_user_by_id(task["mentor_id"])
                    if mentor:
                        task["mentor"] = mentor
                
                return task
            else:
                print(f"Задание с ID {task_id} не найдено")
                return None
        except Exception as e:
            print(f"Ошибка получения задания: {e}")
            return None
    
    @classmethod
    def get_performed_tasks_by_diploma_id(cls, diploma_id):
        try:
            diploma = cls.get_diploma_by_id(diploma_id)
            if not diploma:
                return []
            user_id = diploma.get("user_id")
            if not user_id:
                return []
            user_tasks = cls.get_performed_tasks_by_user_id(user_id)
            if not user_tasks:
                return []            
            return user_tasks
        except Exception as e:
            print(f"Ошибка получения заданий диплома: {e}")
            return []
    
    @classmethod
    def get_user_by_username(cls, username: str) -> dict:
        """
        Получает информацию о пользователе по его имени пользователя
        
        Args:
            username (str): Имя пользователя
            
        Returns:
            dict: Данные пользователя или None, если пользователь не найден
        """
        try:
            user_data = Database.execute_query("""
                SELECT id, username, password, email, first_name, last_name, middle_name, enabled 
                FROM wds_user 
                WHERE username = %s
            """, (username,))
            
            if not user_data or len(user_data) == 0:
                return None
            
            user = user_data[0]
            
            # Формируем полное имя пользователя
            full_name = f"{user[4] or ''} {user[5] or ''}"
            if user[6]:  # Если есть отчество
                full_name += f" {user[6]}"
            
            return {
                "id": user[0],
                "username": user[1],
                "password": user[2],
                "email": user[3],
                "first_name": user[4],
                "last_name": user[5],
                "middle_name": user[6],
                "full_name": full_name.strip(),
                "enabled": user[7]
            }
        except Exception as e:
            print(f"Ошибка при получении пользователя по имени пользователя: {e}")
            return None 
        
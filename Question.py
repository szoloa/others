import sqlite3
import json
import random
# select id,  content,  choise,  answner,  resolve from questions
# 0,no 1,select 2,judge 3,

letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

class Questions:
    def __init__(self, DB='ask.db'):
        self.connect = sqlite3.connect(DB)
        self.cursor = self.connect.cursor() 
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """创建题目表如果不存在"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type INTEGER DEFAULT 1,
                stem TEXT,
                options TEXT DEFAULT NULL,
                answer TEXT DEFAULT NULL,
                analysis TEXT DEFAULT NULL,
                chapter INTEGER DEFAULT 0,
                bankid INTEGER DEFAULT 0,
                difficulty INTEGER DEFAULT 1,
                typeid INTEGER DEFAULT 0
            )
        ''')
        self.connect.commit()

    def add_question(self, stem, options=None, answer=None, analysis=None, 
                   question_type=1, bankid=0, chapter=0, difficulty=1, typeid=0):
        """添加题目"""
        self.cursor.execute(
            'INSERT INTO questions (type, stem, options, answer, analysis, chapter, bankid, difficulty, typeid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (question_type, stem, options, answer, analysis, chapter, bankid, difficulty, typeid)
        )
        self.connect.commit()
        return self.cursor.lastrowid
    
    def update_question(self, id, stem=None, options=None, answer=None, analysis=None, 
                      question_type=None, bankid=None, chapter=None, difficulty=None, typeid=None):
        """更新题目"""
        # 构建更新语句
        update_fields = []
        update_values = []
        
        if stem is not None:
            update_fields.append("stem = ?")
            update_values.append(stem)
        if options is not None:
            update_fields.append("options = ?")
            update_values.append(options)
        if answer is not None:
            update_fields.append("answer = ?")
            update_values.append(answer)
        if analysis is not None:
            update_fields.append("analysis = ?")
            update_values.append(analysis)
        if question_type is not None:
            update_fields.append("type = ?")
            update_values.append(question_type)
        if bankid is not None:
            update_fields.append("bankid = ?")
            update_values.append(bankid)
        if chapter is not None:
            update_fields.append("chapter = ?")
            update_values.append(chapter)
        if difficulty is not None:
            update_fields.append("difficulty = ?")
            update_values.append(difficulty)
        if typeid is not None:
            update_fields.append("typeid = ?")
            update_values.append(typeid)
            
        if update_fields:
            update_values.append(id)
            self.cursor.execute(
                f'UPDATE questions SET {", ".join(update_fields)} WHERE id = ?',
                update_values
            )
            self.connect.commit()
    
    def delete_question(self, id):
        """删除题目"""
        self.cursor.execute('DELETE FROM questions WHERE id = ?', (id,))
        self.connect.commit()
    
    def get_question(self, id):
        """获取题目"""
        self.cursor.execute('SELECT type, stem, options, answer, analysis, chapter, bankid, difficulty, typeid FROM questions WHERE id = ?', (id,))
        result = self.cursor.fetchone()
        if result:
            return {
                'id': id,
                'type': result[0],
                'stem': result[1],
                'options': eval(result[2]) if result[2] else [],
                'answer': result[3],
                'analysis': result[4],
                'chapter': result[5],
                'bankid': result[6],
                'difficulty': result[7],
                'typeid': result[8]
            }
        return None
    
    def get_all_questions(self, bankid=None, chapter=None, question_type=None):
        """获取所有题目"""
        query = 'SELECT id, type, stem, options, answer, analysis, chapter, bankid, difficulty, typeid FROM questions'
        conditions = []
        params = []
        
        if bankid is not None:
            conditions.append("bankid = ?")
            params.append(bankid)
        if chapter is not None:
            conditions.append("chapter = ?")
            params.append(chapter)
        if question_type is not None:
            conditions.append("typeid = ?")
            params.append(question_type)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        questions = []
        for result in results:
            questions.append({
                'id': result[0],
                'type': result[1],
                'stem': result[2],
                'options': eval(result[3]) if result[3] else [],
                'answer': result[4],
                'analysis': result[5],
                'chapter': result[6],
                'bankid': result[7],
                'difficulty': result[8],
                'typeid': result[9],
            })
        return questions
    
    def get_random_question(self, bankid=None, chapter=None, question_type=None):
        """随机获取一道题目"""
        questions = self.get_all_questions(bankid, chapter, question_type)
        if questions:
            return random.choice(questions)
        return None

    def close(self):
        self.connect.close()


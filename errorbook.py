import sqlite3

class Error:
    def __init__(self, DB='errorbook.db'):
        self.connect = sqlite3.connect(DB)
        self.cursor = self.connect.cursor()
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        """创建题目表如果不存在"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                questionid INTEGER,
                type INTEGER DEFAULT 1,
                stem TEXT DEFALUT NULL,
                options TEXT DEFAULT NULL,
                answer TEXT DEFAULT NULL,
                analysis TEXT DEFAULT NULL,
                chapter INTEGER DEFAULT 0,
                bankid INTEGER DEFAULT 0,
                difficulty INTEGER DEFAULT 1,
                typeid INTEGER DEFAULT 0,
                useranswer TEXT DEFAULT NULL,
                iscorrect INTEGER DEFAULT 0
            )
        ''')
        self.connect.commit()

    def add_question(self, questionid, stem=None, options=None, answer=None, analysis=None, 
                   question_type=1, bankid=0, chapter=0, difficulty=1, typeid=0, useranswer=None, iscorrect=0):
        """添加题目"""
        self.cursor.execute(
            'INSERT INTO errors (questionid, type, stem, options, answer, analysis, chapter, bankid, difficulty, typeid, useranswer, iscorrect) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (questionid, question_type , stem, str(options), answer, analysis, chapter, bankid, difficulty, typeid, useranswer, iscorrect)
        )
        self.connect.commit()
        return self.cursor.lastrowid

    def get_all_num(self):
        self.cursor.execute('select questionid from errors')
        return len(self.cursor.fetchall())
    def get_correct_num(self):
        self.cursor.execute('select questionid from errors where iscorrect = 1')
        return len(self.cursor.fetchall())



if __name__ == '__main__':
    e = Error()
    print(e.get_discorrect_num())
 

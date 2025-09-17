import sqlite3
import json
# select id,  content,  choise,  answner,  resolve from problems
# 0,no 1,select 2,judge 3,

letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

class Problems:
    def __init__(self, DB='problems.db'):
        self.connect = sqlite3.connect(DB)
        self.cursor = self.connect.cursor() 
        self._create_table_if_not_exists()  # Ensure table exists
    
    def _create_table_if_not_exists(self):
        """Create the problems table if it doesn't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT DEFAULT NULL,
                stem TEXT,
                options TEXT DEFAULT NULL,
                answer TEXT DEFAULT NULL,
                analysis TEXT DEFAULT NULL,
                capter INTEGER DEFAULT 0,
                bankid INTEGER DEFAULT 0
            )
        ''')
        self.connect.commit()

    def addProblem(self, stem, options=None, answer=None, analysis=None, TYPE=None, bankid=0, capter=0):
        self.cursor.execute(
                'INSERT INTO problems (type, stem, options, answer, analysis, capter, bankid) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (TYPE, stem, options, answer, analysis, capter, bankid)
            )
        self.connect.commit()
    
    def setContent(self, id, content, source, force=False):
        self.cursor.execute(f'select {content} from problems where id = ? ', (id,))
        Fetchone = self.cursor.fetchone()
        if Fetchone:
            content_ = Fetchone[0]
        else:
            content_ = 0

        if content_ == None or force:
            self.cursor.execute(
                f'Update problems set {content} = ? where id = ?',
                (source, id)
            )
            self.connect.commit()
        else:
            print('this content is not null')
            
    def getProblem(self, id):
        self.cursor.execute('select type, stem, options from problems where id = ?',(id,))
        result = self.cursor.fetchone()
        print('type:', result[0])
        print('stem:', result[1])
        if eval(result[2]):
            print('options:')
            for i,j in enumerate(eval(result[2])):
                print(f'{letter[i]}: {j}')

    def getResolve(self, id):
        self.cursor.execute('select answer, analysis from problems where id = ?',(id,))
        result = self.cursor.fetchone()
        print('answer:', result[0])
        print('analysis:', result[1])

    def close(self):
        self.connect.close()
if __name__ == '__main__':
    p = Problems('ask.db')
    p.getProblem(1322)

class Problems:
    def __init__(self, DB='ask.db'):
        self.connect = sqlite3.connect(DB)
        self.cursor = self.connect.cursor() 
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """创建题目表如果不存在"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type INTEGER DEFAULT 1,
                stem TEXT,
                options TEXT DEFAULT NULL,
                answer TEXT DEFAULT NULL,
                analysis TEXT DEFAULT NULL,
                chapter INTEGER DEFAULT 0,
                bankid INTEGER DEFAULT 0,
                difficulty INTEGER DEFAULT 1
            )
        ''')
        self.connect.commit()

    def add_problem(self, stem, options=None, answer=None, analysis=None, 
                   problem_type=1, bankid=0, chapter=0, difficulty=1):
        """添加题目"""
        self.cursor.execute(
            'INSERT INTO problems (type, stem, options, answer, analysis, chapter, bankid, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (problem_type, stem, options, answer, analysis, chapter, bankid, difficulty)
        )
        self.connect.commit()
        return self.cursor.lastrowid
    
    def update_problem(self, id, stem=None, options=None, answer=None, analysis=None, 
                      problem_type=None, bankid=None, chapter=None, difficulty=None):
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
        if problem_type is not None:
            update_fields.append("type = ?")
            update_values.append(problem_type)
        if bankid is not None:
            update_fields.append("bankid = ?")
            update_values.append(bankid)
        if chapter is not None:
            update_fields.append("chapter = ?")
            update_values.append(chapter)
        if difficulty is not None:
            update_fields.append("difficulty = ?")
            update_values.append(difficulty)
            
        if update_fields:
            update_values.append(id)
            self.cursor.execute(
                f'UPDATE problems SET {", ".join(update_fields)} WHERE id = ?',
                update_values
            )
            self.connect.commit()
    
    def delete_problem(self, id):
        """删除题目"""
        self.cursor.execute('DELETE FROM problems WHERE id = ?', (id,))
        self.connect.commit()
    
    def get_problem(self, id):
        """获取题目"""
        self.cursor.execute('SELECT type, stem, options, answer, analysis, chapter, bankid, difficulty FROM problems WHERE id = ?', (id,))
        result = self.cursor.fetchone()
        if result:
            return {
                'id': id,
                'type': result[0],
                'stem': result[1],
                'options': json.loads(result[2]) if result[2] else [],
                'answer': result[3],
                'analysis': result[4],
                'chapter': result[5],
                'bankid': result[6],
                'difficulty': result[7]
            }
        return None
    
    def get_all_problems(self, bankid=None, chapter=None, problem_type=None):
        """获取所有题目"""
        query = 'SELECT id, type, stem, options, answer, analysis, chapter, bankid, difficulty FROM problems'
        conditions = []
        params = []
        
        if bankid is not None:
            conditions.append("bankid = ?")
            params.append(bankid)
        if chapter is not None:
            conditions.append("chapter = ?")
            params.append(chapter)
        if problem_type is not None:
            conditions.append("type = ?")
            params.append(problem_type)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        problems = []
        for result in results:
            problems.append({
                'id': result[0],
                'type': result[1],
                'stem': result[2],
                'options': eval(result[3]) if result[3] else [],
                'answer': result[4],
                'analysis': result[5],
                'chapter': result[6],
                'bankid': result[7],
                'difficulty': result[8]
            })
        return problems
    
    def get_random_problem(self, bankid=None, chapter=None, problem_type=None):
        """随机获取一道题目"""
        problems = self.get_all_problems(bankid, chapter, problem_type)
        if problems:
            return random.choice(problems)
        return None
    
    def close(self):
        self.connect.close()
import sqlite3
import json
# select id,  content,  choise,  answner,  resolve from problems
# 0,no 1,select 2,judge 3,

types = {
    0 : 'no',
    1 : 'select',
    2 : 'judge',
}

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
                type INTEGER DEFAULT 0,
                content TEXT NOT NULL,
                choise TEXT DEFAULT 'null',
                answner TEXT DEFAULT 'null',
                resolve TEXT DEFAULT 'null'
            )
        ''')
        self.connect.commit()

    def addProblem(self, content, choise='null', answner='null', resolve='null', TYPE=0):
        self.cursor.execute(
                'INSERT INTO problems (type, content, choise, answner, resolve) VALUES (?, ?, ?, ?, ?)',
                (TYPE, content, choise, answner, resolve)
            )
        self.connect.commit()
    
    def setContent(self, id, content, source, force=False):
        self.cursor.execute(f'select {content} from problems where id = ? ', (id,))
        Fetchone = self.cursor.fetchone()
        if Fetchone:
            content_ = Fetchone[0]
        else:
            content_ = 0

        if content_ == 'null' or force:
            self.cursor.execute(
                f'Update problems set {content} = ? where id = ?',
                (source, id)
            )
            self.connect.commit()
        else:
            print('this content is not null')
            
    def getProblem(self, id):
        self.cursor.execute('select type,content,choise from problems where id = ?',(id,))
        result = self.cursor.fetchone()
        print('type:', types[result[0]])
        print('content:', result[1])
        if result[0] == 1:
            chioses = json.loads(result[2])
            for key,name in chioses.items():
                print(f'{key}: {name}')

    def getResolve(self, id):
        self.cursor.execute('select answner, resolve from problems where id = ?',(id,))
        result = self.cursor.fetchone()
        print('answner:', result[0])
        print('resolve:', result[1])

    def close(self):
        self.connect.close()

if __name__ == '__main__':
    p = Problems('ask.db')
    dict1 = {
        'A':'a',
        'B':'b',
        'C': 'c'
    }
    # p.addProblem('how to chane' ,TYPE=1)
    p.setContent(12, 'resolve' ,json.dumps(dict1))
    p.getProblem(11)
    p.getResolve(11)
    p.close()
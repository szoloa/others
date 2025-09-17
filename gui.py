import sqlite3
import json
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
                             QTextEdit, QRadioButton, QButtonGroup, QMessageBox,
                             QSpinBox, QComboBox, QTabWidget, QListWidget, QSplitter)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor
import random
from Problem import Problems

# 选项字母
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

class ProblemWidget(QWidget):
    """题目显示组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_problem = None
        self.user_answer = None
        self.font = QFont("Arial", 14)
        self.setFont(self.font)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 题目类型和ID
        self.type_label = QLabel("")
        layout.addWidget(self.type_label)
        
        # 题目内容
        self.stem_text = QTextEdit()
        self.stem_text.setReadOnly(True)
        layout.addWidget(self.stem_text)
        
        # 选项区域
        self.options_frame = QFrame()
        self.options_layout = QVBoxLayout(self.options_frame)
        self.options_group = QButtonGroup(self)
        self.options_group.buttonClicked.connect(self.on_option_selected)
        
        self.option_widgets = []
        for i in range(7):  # 最多7个选项
            option_widget = QWidget()
            option_layout = QHBoxLayout(option_widget)
            option_layout.setContentsMargins(0, 0, 0, 0)
            
            radio = QRadioButton()
            self.options_group.addButton(radio, i)
            label = QLabel("")
            label.setWordWrap(True)
            
            option_layout.addWidget(radio)
            option_layout.addWidget(label)
            option_layout.addStretch()
            
            self.option_widgets.append((radio, label))
            self.options_layout.addWidget(option_widget)
            
        layout.addWidget(self.options_frame)
        
        # 答案和解析
        self.answer_label = QLabel("")
        self.answer_label.setWordWrap(True)
        self.answer_label.setFont(QFont("Arial", 14))
        self.answer_label.hide()
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setFont(QFont("Arial", 14))
        self.analysis_text.hide()
        
        layout.addWidget(self.answer_label)
        layout.addWidget(self.analysis_text)
        
    def on_option_selected(self, button):
        self.user_answer = button.text()[0]  # 获取选项字母
    
    def set_problem(self, problem):
        self.current_problem = problem
        self.user_answer = None
        self.options_group.setExclusive(False)
        for radio, _ in self.option_widgets:
            radio.setChecked(False)
        self.options_group.setExclusive(True)
        
        # 隐藏解析
        self.answer_label.hide()
        self.analysis_text.hide()
        
        # 设置题目类型
        problem_type = problem['typeid']
        
        self.type_label.setText(f"题目ID: {problem['id']} | 类型: {problem['type']} | 难度: {problem['difficulty']}")
        
        # 设置题目内容
        self.stem_text.setPlainText(problem['stem'])
        
        # 设置选项
        options = problem['options']
        for i, (radio, label) in enumerate(self.option_widgets):
            if i < len(options):
                radio.setText(LETTERS[i])
                label.setText(options[i])
                radio.show()
                label.show()
            else:
                radio.hide()
                label.hide()
        
        # 判断题特殊处理
        if problem_type == 2:  # 判断题
            self.option_widgets[0][1].setText("正确")
            self.option_widgets[1][1].setText("错误")
            for i in range(2, 7):
                self.option_widgets[i][0].hide()
                self.option_widgets[i][1].hide()
    
    def show_answer(self):
        if self.current_problem:
            correct_answer = self.current_problem['answer']
            self.answer_label.setText(f"正确答案: {correct_answer}")
            self.answer_label.show()
            
            if self.current_problem['analysis']:
                self.analysis_text.setPlainText(self.current_problem['analysis'])
                self.analysis_text.show()
    
    def check_answer(self):
        letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        if not self.current_problem or self.user_answer is None:
            return None, "请先选择答案"
        
        correct_answer = self.current_problem['answer']
        is_correct = (self.user_answer.upper() == letter[int(correct_answer)])
        
        if is_correct:
            return True, "回答正确！"
        else:
            return False, f"回答错误！正确答案是: {letter[int(correct_answer)]}"

class ProblemManager(QWidget):
    """题目管理组件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_problem_id = None
        self.font = QFont("Arial", 14)
        self.setFont(self.font)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # 左侧题目列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.problem_list = QListWidget()
        self.problem_list.currentRowChanged.connect(self.on_problem_selected)
        left_layout.addWidget(QLabel("题目列表:"))
        left_layout.addWidget(self.problem_list)
        
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self.refresh_list)
        left_layout.addWidget(refresh_btn)
        
        # 右侧编辑区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 题目类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("题目类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["未知", "选择题", "判断题", "填空题", "名词解释" ,"简答题", "多选题", "实验题"])
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        right_layout.addLayout(type_layout)
        
        # 题目内容
        right_layout.addWidget(QLabel("题目内容:"))
        self.stem_edit = QTextEdit()
        right_layout.addWidget(self.stem_edit)
        
        # 选项区域
        self.options_widget = QWidget()
        options_layout = QVBoxLayout(self.options_widget)
        options_layout.addWidget(QLabel("选项:"))
        
        self.option_edits = []
        for i, letter in enumerate(LETTERS):
            option_layout = QHBoxLayout()
            option_layout.addWidget(QLabel(f"{letter}:"))
            option_edit = QLineEdit()
            self.option_edits.append(option_edit)
            option_layout.addWidget(option_edit)
            options_layout.addLayout(option_layout)
        
        right_layout.addWidget(self.options_widget)
        
        # 答案和解析
        answer_layout = QHBoxLayout()
        answer_layout.addWidget(QLabel("答案:"))
        self.answer_edit = QLineEdit()
        answer_layout.addWidget(self.answer_edit)
        right_layout.addLayout(answer_layout)
        
        right_layout.addWidget(QLabel("解析:"))
        self.analysis_edit = QTextEdit()
        right_layout.addWidget(self.analysis_edit)
        
        # 难度和章节
        meta_layout = QHBoxLayout()
        meta_layout.addWidget(QLabel("难度:"))
        self.difficulty_spin = QSpinBox()
        self.difficulty_spin.setRange(1, 5)
        meta_layout.addWidget(self.difficulty_spin)
        
        meta_layout.addWidget(QLabel("章节:"))
        self.chapter_spin = QSpinBox()
        self.chapter_spin.setRange(0, 100)
        meta_layout.addWidget(self.chapter_spin)
        
        meta_layout.addWidget(QLabel("题库ID:"))
        self.bankid_spin = QSpinBox()
        self.bankid_spin.setRange(0, 100)
        meta_layout.addWidget(self.bankid_spin)
        
        right_layout.addLayout(meta_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.new_btn = QPushButton("新建")
        self.new_btn.clicked.connect(self.new_problem)
        button_layout.addWidget(self.new_btn)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_problem)
        button_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_problem)
        button_layout.addWidget(self.delete_btn)
        
        right_layout.addLayout(button_layout)
        
        # 分割左右区域
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
        
        # 初始刷新列表
        self.refresh_list()
    
    def refresh_list(self):
        self.problem_list.clear()
        problems = self.db_manager.get_all_problems()
        for problem in problems:
            stem_preview = problem['stem'][:10] if problem['stem'] else 'Cant Preview'
            self.problem_list.addItem(f"{problem['id']}: {stem_preview}")
    
    def on_problem_selected(self, row):
        if row >= 0:
            problems = self.db_manager.get_all_problems()
            if row < len(problems):
                self.current_problem_id = problems[row]['id']
                self.load_problem(problems[row])
    
    def load_problem(self, problem):
        self.type_combo.setCurrentIndex(problem['typeid'])
        self.stem_edit.setPlainText(problem['stem'])
        
        # 加载选项
        options = problem['options']
        for i, edit in enumerate(self.option_edits):
            if i < len(options):
                edit.setText(options[i])
            else:
                edit.setText("")
        
        self.answer_edit.setText(problem['answer'] or "")
        self.analysis_edit.setPlainText(problem['analysis'] or "")
        self.difficulty_spin.setValue(problem['difficulty'])
        self.chapter_spin.setValue(problem['chapter'])
        self.bankid_spin.setValue(problem['bankid'])
    
    def new_problem(self):
        self.current_problem_id = None
        self.type_combo.setCurrentIndex(1)  # 默认选择题
        self.stem_edit.clear()
        for edit in self.option_edits:
            edit.clear()
        self.answer_edit.clear()
        self.analysis_edit.clear()
        self.difficulty_spin.setValue(1)
        self.chapter_spin.setValue(0)
        self.bankid_spin.setValue(0)
    
    def save_problem(self):
        # 收集数据
        problem_type = self.type_combo.currentIndex()
        stem = self.stem_edit.toPlainText()
        
        # 收集选项
        options = []
        for edit in self.option_edits:
            if edit.text().strip():
                options.append(edit.text().strip())
        
        answer = self.answer_edit.text().strip()
        analysis = self.analysis_edit.toPlainText()
        difficulty = self.difficulty_spin.value()
        chapter = self.chapter_spin.value()
        bankid = self.bankid_spin.value()
        
        # 验证数据
        if not stem:
            QMessageBox.warning(self, "警告", "题目内容不能为空")
            return
        
        if problem_type == 1 and not options:  # 选择题需要选项
            QMessageBox.warning(self, "警告", "选择题需要至少一个选项")
            return
        
        if not answer:
            QMessageBox.warning(self, "警告", "答案不能为空")
            return
        
        # 保存到数据库
        if self.current_problem_id:
            # 更新现有题目
            self.db_manager.update_problem(
                self.current_problem_id,
                stem=stem,
                options=json.dumps(options, ensure_ascii=False),
                answer=answer,
                analysis=analysis,
                problem_type=problem_type,
                bankid=bankid,
                chapter=chapter,
                difficulty=difficulty
            )
            QMessageBox.information(self, "成功", "题目更新成功")
        else:
            # 添加新题目
            self.db_manager.add_problem(
                stem=stem,
                options=json.dumps(options, ensure_ascii=False),
                answer=answer,
                analysis=analysis,
                problem_type=problem_type,
                bankid=bankid,
                chapter=chapter,
                difficulty=difficulty
            )
            QMessageBox.information(self, "成功", "题目添加成功")
        
        # 刷新列表
        self.refresh_list()
    
    def delete_problem(self):
        if not self.current_problem_id:
            QMessageBox.warning(self, "警告", "请先选择一个题目")
            return
        
        reply = QMessageBox.question(self, "确认", "确定要删除这个题目吗？", 
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db_manager.delete_problem(self.current_problem_id)
            QMessageBox.information(self, "成功", "题目删除成功")
            self.new_problem()
            self.refresh_list()


class PracticeWidget(QWidget):
    """练习组件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.problem_widget = ProblemWidget()
        self.font = QFont("Arial", 14)
        self.setFont(self.font)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        self.next_btn = QPushButton("下一题")
        self.next_btn.clicked.connect(self.next_problem)
        control_layout.addWidget(self.next_btn)
        
        self.check_btn = QPushButton("检查答案")
        self.check_btn.clicked.connect(self.check_answer)
        control_layout.addWidget(self.check_btn)
        
        self.show_btn = QPushButton("显示解析")
        self.show_btn.clicked.connect(self.show_answer)
        control_layout.addWidget(self.show_btn)
        
        control_layout.addStretch()
        
        # 筛选区域
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("题库:"))
        self.bank_combo = QComboBox()
        self.bank_combo.addItem("所有题库", None)
        self.bank_combo.addItem("分子生物学", 1)
        self.bank_combo.addItem("普通生物学", 2)
        self.bank_combo.addItem("生物化学", 3)
        self.bank_combo.addItem("微生物学", 4)
        self.bank_combo.addItem("细胞生物学", 5)
        filter_layout.addWidget(self.bank_combo)
        
        filter_layout.addWidget(QLabel("章节:"))
        self.chapter_combo = QComboBox()
        self.chapter_combo.addItem("所有章节", None)
        for i in range(0, 38):
            self.chapter_combo.addItem(f"第{i}章", i)
        filter_layout.addWidget(self.chapter_combo)
        
        filter_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("所有类型", None)
        self.type_combo.addItem("选择题", 1)
        self.type_combo.addItem("判断题", 2)
        self.type_combo.addItem("填空题", 3)
        self.type_combo.addItem("名词解释", 4)
        self.type_combo.addItem("简答题", 5)
        self.type_combo.addItem("多选题", 6)
        self.type_combo.addItem("实验题", 7)
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addStretch()
        
        layout.addLayout(control_layout)
        layout.addLayout(filter_layout)
        
        # 题目显示区域
        layout.addWidget(self.problem_widget)
        
        # 初始加载一道题
        self.next_problem()
    
    def next_problem(self):
        bankid = self.bank_combo.currentData()
        chapter = self.chapter_combo.currentData()
        problem_type = self.type_combo.currentData()
        
        problem = self.db_manager.get_random_problem(bankid, chapter, problem_type)
        if problem:
            self.problem_widget.set_problem(problem)
        else:
            QMessageBox.information(self, "提示", "没有找到符合条件的题目")
    
    def check_answer(self):
        is_correct, message = self.problem_widget.check_answer()
        if is_correct is not None:
            QMessageBox.information(self, "结果", message)
    
    def show_answer(self):
        self.problem_widget.show_answer()


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.db_manager = Problems('ask.db')
        self.font = QFont("Arial", 14)
        self.setFont(self.font)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('刷题软件')
        self.setGeometry(100, 100, 1000, 700)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
            }
        """)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 练习页面
        self.practice_widget = PracticeWidget(self.db_manager)
        self.tabs.addTab(self.practice_widget, "练习")
        
        # 管理页面
        self.manage_widget = ProblemManager(self.db_manager)
        self.tabs.addTab(self.manage_widget, "题目管理")
        
    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
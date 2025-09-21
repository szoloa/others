import sqlite3
import json
import sys
import random
from Question import Questions
from PyQt5.QtWebEngineWidgets import QWebEngineView  # 导入Web引擎组件
from bs4 import BeautifulSoup as soup
import errorbook
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
                             QTextEdit, QRadioButton, QButtonGroup, QMessageBox,
                             QSpinBox, QComboBox, QTabWidget, QListWidget, QSplitter,
                             QGroupBox, QCheckBox, QFileDialog, QProgressBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QTextDocument, QTextCursor
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import html

# 选项字母
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

class PaperGenerator(QWidget):
    """试卷生成组件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.generated_paper = []  # 存储生成的试卷题目
        self.seed = 42
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 试卷设置区域
        settings_group = QGroupBox("试卷设置")
        settings_layout = QVBoxLayout(settings_group)
        
        # 试卷标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("试卷标题:"))
        self.title_edit = QLineEdit("模拟考试试卷")
        title_layout.addWidget(self.title_edit)
        settings_layout.addLayout(title_layout)

        seed_layout = QHBoxLayout()
        seed_layout.addWidget(QLabel("随机种子:"))
        self.seed_edit = QLineEdit(str(self.seed))
        seed_layout.addWidget(self.seed_edit)
        settings_layout.addLayout(seed_layout)
        

        # 题目数量设置
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("选择题数量:"))
        self.choice_count = QSpinBox()
        self.choice_count.setRange(0, 100)
        self.choice_count.setValue(20)
        count_layout.addWidget(self.choice_count)
        
        count_layout.addWidget(QLabel("判断题数量:"))
        self.judge_count = QSpinBox()
        self.judge_count.setRange(0, 100)
        self.judge_count.setValue(10)
        count_layout.addWidget(self.judge_count)
        
        count_layout.addWidget(QLabel("填空题数量:"))
        self.full_empty_count = QSpinBox()
        self.full_empty_count.setRange(0, 100)
        self.full_empty_count.setValue(5)
        count_layout.addWidget(self.full_empty_count)

        count_layout.addWidget(QLabel("名词解释数量:"))
        self.name_explain_count = QSpinBox()
        self.name_explain_count.setRange(0, 100)
        self.name_explain_count.setValue(5)
        count_layout.addWidget(self.name_explain_count)
        
        count_layout.addWidget(QLabel("论述题数量:"))
        self.short_answer_count = QSpinBox()
        self.short_answer_count.setRange(0, 100)
        self.short_answer_count.setValue(5)
        count_layout.addWidget(self.short_answer_count)

        settings_layout.addLayout(count_layout)
        
        # 难度设置
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("难度范围:"))
        self.min_difficulty = QSpinBox()
        self.min_difficulty.setRange(0, 5)
        self.min_difficulty.setValue(0)
        difficulty_layout.addWidget(self.min_difficulty)
        
        difficulty_layout.addWidget(QLabel("到"))
        self.max_difficulty = QSpinBox()
        self.max_difficulty.setRange(0, 5)
        self.max_difficulty.setValue(5)
        difficulty_layout.addWidget(self.max_difficulty)
        
        settings_layout.addLayout(difficulty_layout)
        
        # 章节和题库筛选
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
        
        settings_layout.addLayout(filter_layout)
        
        # 是否包含解析
        self.include_analysis = QCheckBox("包含解析")
        self.include_analysis.setChecked(False)
        settings_layout.addWidget(self.include_analysis)
        
        # 是否随机排序
        self.random_order = QCheckBox("随机排序题目")
        self.random_order.setChecked(True)
        settings_layout.addWidget(self.random_order)
        
        layout.addWidget(settings_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成试卷")
        self.generate_btn.clicked.connect(self.generate_paper)
        button_layout.addWidget(self.generate_btn)
        
        self.preview_btn = QPushButton("预览试卷")
        self.preview_btn.clicked.connect(self.preview_paper)
        self.preview_btn.setEnabled(False)
        button_layout.addWidget(self.preview_btn)
        
        self.export_btn = QPushButton("导出试卷")
        self.export_btn.clicked.connect(self.export_paper)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        self.print_btn = QPushButton("打印试卷")
        self.print_btn.clicked.connect(self.print_paper)
        self.print_btn.setEnabled(False)
        button_layout.addWidget(self.print_btn)
        
        layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 试卷预览区域
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
    def generate_paper(self):
        """生成试卷"""
        # 获取设置
        choice_count = self.choice_count.value()
        judge_count = self.judge_count.value()
        full_empty_count = self.full_empty_count.value()
        name_explain_count = self.name_explain_count.value()
        short_answer_count = self.short_answer_count.value()
        min_difficulty = self.min_difficulty.value()
        max_difficulty = self.max_difficulty.value()
        bankid = self.bank_combo.currentData()
        chapter = self.chapter_combo.currentData()
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, choice_count + judge_count + short_answer_count)
        self.progress_bar.setValue(0)
        
        # 清空之前的试卷
        self.generated_paper = []
        
        # 获取所有符合条件的题目
        all_questions = self.db_manager.get_all_questions(
            bankid=bankid, 
            chapter=chapter
        )
        
        # 按类型和难度筛选
        choice_problems = [
            p for p in all_questions 
            if p['typeid'] == 1 and min_difficulty <= p['difficulty'] <= max_difficulty
        ]
        
        judge_problems = [
            p for p in all_questions 
            if p['typeid'] == 2 and min_difficulty <= p['difficulty'] <= max_difficulty
        ]
        full_empty_problems = [
            p for p in all_questions 
            if p['typeid'] == 3 and min_difficulty <= p['difficulty'] <= max_difficulty
        ]
        name_explain_problems = [
            p for p in all_questions 
            if p['typeid'] == 4 and min_difficulty <= p['difficulty'] <= max_difficulty
        ]
        short_answer_problems = [
            p for p in all_questions 
            if p['typeid'] == 5 and min_difficulty <= p['difficulty'] <= max_difficulty
        ]
        
        # 检查题目数量是否足够
        if len(choice_problems) < choice_count:
            QMessageBox.warning(self, "警告", 
                               f"选择题数量不足。需要 {choice_count} 道，但只有 {len(choice_problems)} 道可用。")
            choice_count = len(choice_problems)
            
        if len(judge_problems) < judge_count:
            QMessageBox.warning(self, "警告", 
                               f"判断题数量不足。需要 {judge_count} 道，但只有 {len(judge_problems)} 道可用。")
            judge_count = len(judge_problems)
            
        if len(full_empty_problems) < full_empty_count:
            QMessageBox.warning(self, "警告", 
                               f"填空题数量不足。需要 {full_empty_count} 道，但只有 {len(full_empty_problems)} 道可用。")
            full_empty_count = len(full_empty_problems)
        
        if len(name_explain_problems) < name_explain_count:
            QMessageBox.warning(self, "警告", 
                               f"名词解释数量不足。需要 {name_explain_count} 道，但只有 {len(name_explain_problems)} 道可用。")
            name_explain_count = len(name_explain_problems)
        
        if len(short_answer_problems) < short_answer_count:
            QMessageBox.warning(self, "警告", 
                               f"简答题数量不足。需要 {short_answer_count} 道，但只有 {len(short_answer_problems)} 道可用。")
            short_answer_count = len(short_answer_problems)
        

        random.seed(int(self.seed_edit.text()))
        # 随机选择题目
        if choice_count > 0:
            selected_choices = random.sample(choice_problems, choice_count)
            self.generated_paper.extend(selected_choices)
            self.progress_bar.setValue(choice_count)
            
        if judge_count > 0:
            selected_judges = random.sample(judge_problems, judge_count)
            self.generated_paper.extend(selected_judges)
            self.progress_bar.setValue(choice_count + judge_count)
            
        if full_empty_count > 0:
            selected_full_emptys = random.sample(full_empty_problems, full_empty_count)
            self.generated_paper.extend(selected_full_emptys)
            self.progress_bar.setValue(choice_count + judge_count + full_empty_count)
        
        if short_answer_count > 0:
            selected_name_explains = random.sample(name_explain_problems, name_explain_count)
            self.generated_paper.extend(selected_name_explains)
            self.progress_bar.setValue(choice_count + judge_count + full_empty_count + name_explain_count)

        if short_answer_count > 0:
            selected_short_answers = random.sample(short_answer_problems, short_answer_count)
            self.generated_paper.extend(selected_short_answers)
            self.progress_bar.setValue(choice_count + judge_count + full_empty_count + name_explain_count + short_answer_count)

        # 随机排序
        if self.random_order.isChecked():
            random.shuffle(self.generated_paper)
        
        # 启用按钮
        self.preview_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.print_btn.setEnabled(True)
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        QMessageBox.information(self, "成功", f"试卷生成完成！共 {len(self.generated_paper)} 道题目。")
        self.preview_paper()
    
    def preview_paper(self):
        """预览试卷"""
        if not self.generated_paper:
            QMessageBox.warning(self, "警告", "请先生成试卷")
            return
            
        # 生成HTML格式的试卷
        html_content = self.generate_html_paper()
        self.preview_text.setHtml(html_content)
    
    def generate_html_paper(self):
        """生成HTML格式的试卷内容"""
        title = self.title_edit.text()
        include_analysis = self.include_analysis.isChecked()
        bankid = self.bank_combo.currentData()
        chapter = self.chapter_combo.currentData()
        bank = ['所有题库', '分子生物学', '普通生物学', '生物化学', '微生物学', '细胞生物学'][bankid if bankid else 0] 
        #
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                h1 {{ text-align: center; color: #2c3e50; }}
                .question {{ margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                .question-number {{ font-weight: bold; color: #3498db; }}
                .options {{ margin-left: 20px; }}
                .option {{ margin-bottom: 5px; }}
                .answer {{ color: #27ae60; font-weight: bold; margin-top: 5px; }}
                .analysis {{ color: #7f8c8d; font-style: italic; margin-top: 5px; }}
                .section {{ margin-top: 30px; }}
            </style>
        </head>
        <body>
            <h1>{html.escape(title)}-{bank}-{ "第" + str(chapter) if chapter else "所有"}章节-{self.seed_edit.text()}</h1>
        """
        
        # 按题型分组
        choice_questions = [q for q in self.generated_paper if q['typeid'] == 1]
        judge_questions = [q for q in self.generated_paper if q['typeid'] == 2]
        full_empty_questions = [q for q in self.generated_paper if q['typeid'] == 3]
        name_explain_questions = [q for q in self.generated_paper if q['typeid'] == 4]
        short_answer_questions = [q for q in self.generated_paper if q['typeid'] == 5]
        
        # 添加选择题
        if choice_questions:
            html_content += '<div class="section"><h2>一、选择题</h2>'
            for i, question in enumerate(choice_questions, 1):
                html_content += f'<div class="question">'
                html_content += f'<div class="question-number">{i}. 题目ID {question["id"]}</div>'
                html_content += f'<div class="stem">{question["stem"]}</div>'
                
                html_content += '<div class="options">'
                for j, option in enumerate(question['options']):
                    html_content += f'<div class="option">{LETTERS[j]}. {html.escape(option)}</div>'
                html_content += '</div>'
                
                if include_analysis:
                    html_content += f'<div class="answer">答案: {html.escape(LETTERS[int(question["answer"])])}</div>'
                    if question['analysis']:
                        html_content += f'<div class="analysis">解析: {html.escape(soup(question["analysis"], "lxml").text)}</div>'
                
                html_content += '</div>'
            html_content += '</div>'
        
        # 添加判断题
        if judge_questions:
            html_content += '<div class="section"><h2>二、判断题</h2>'
            for i, question in enumerate(judge_questions, 1):
                html_content += f'<div class="question">'
                html_content += f'<div class="question-number">{i}. 题目ID {question["id"]}</div>'
                html_content += f'<div class="stem">{html.escape(question["stem"])}</div>'
                
                if include_analysis:
                    html_content += f'<div class="answer">答案: {html.escape(["错误","正确"][int(question["answer"])])}</div>'
                    if question['analysis']:
                        html_content += f'<div class="analysis">解析: {html.escape(soup(question["analysis"], "lxml").text)}</div>'
                
                html_content += '</div>'
            html_content += '</div>'

        if full_empty_questions:
            html_content += '<div class="section"><h2>三、填空题</h2>'
            for i, question in enumerate(full_empty_questions, 1):
                html_content += f'<div class="question">'
                html_content += f'<div class="question-number">{i}. 题目ID {question["id"]}</div>'
                html_content += f'<div class="stem">{html.escape(question["stem"])}</div>'
                
                if include_analysis:
                    html_content += f'<div class="answer">答案: {" ".join(eval(question['answer']))}</div>'
                    if question['analysis']:
                        html_content += f'<div class="analysis">解析: {soup(question["analysis"], "lxml").text}</div>'
                
                html_content += '</div>'
            html_content += '</div>'
        
        if name_explain_questions:
            html_content += '<div class="section"><h2>四、名词解释</h2>'
            for i, question in enumerate(name_explain_questions, 1):
                html_content += f'<div class="question">'
                html_content += f'<div class="question-number">{i}. 题目ID {question["id"]}</div>'
                html_content += f'<div class="stem">{question["stem"]}</div>'
                
                if include_analysis:
                    html_content += f'<div class="answer">答案: {html.escape(question["answer"])}</div>'
                    if question['analysis']:
                        html_content += f'<div class="analysis">解析: {soup(question["analysis"], "lxml").text}</div>'
                
                html_content += '</div>'
            html_content += '</div>'

        # 添加简答题
        if short_answer_questions:
            html_content += '<div class="section"><h2>五、论述题</h2>'
            for i, question in enumerate(short_answer_questions, 1):
                html_content += f'<div class="question">'
                html_content += f'<div class="question-number">{i}. 题目ID {question["id"]}</div>'
                html_content += f'<div class="stem">{html.escape(question["stem"])}</div>'
                
                if include_analysis:
                    html_content += f'<div class="answer">答案: {question["answer"]}</div>'
                    if question['analysis']:
                        html_content += f'<div class="analysis">解析: {soup(question["analysis"], "lxml").text}</div>'
                
                html_content += '</div>'
            html_content += '</div>'
        
        html_content += """
        </body>
        </html>
        """
        
        return html_content
    
    def export_paper(self):
        """导出试卷到文件"""
        if not self.generated_paper:
            QMessageBox.warning(self, "警告", "请先生成试卷")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存试卷", "", "HTML文件 (*.html);;文本文件 (*.txt)"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.html'):
                html_content = self.generate_html_paper()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            else:
                # 生成纯文本格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.title_edit.text() + "\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # 按题型分组
                    choice_questions = [q for q in self.generated_paper if q['type'] == 1]
                    judge_questions = [q for q in self.generated_paper if q['type'] == 2]
                    short_answer_questions = [q for q in self.generated_paper if q['type'] == 3]
                    
                    # 添加选择题
                    if choice_questions:
                        f.write("一、选择题\n")
                        for i, question in enumerate(choice_questions, 1):
                            f.write(f"{i}. {question['stem']}\n")
                            for j, option in enumerate(question['options']):
                                f.write(f"   {LETTERS[j]}. {option}\n")
                            f.write("\n")
                    
                    # 添加判断题
                    if judge_questions:
                        f.write("二、判断题\n")
                        for i, question in enumerate(judge_questions, 1):
                            f.write(f"{i}. {question['stem']}\n\n")
                    
                    # 添加简答题
                    if short_answer_questions:
                        f.write("三、简答题\n")
                        for i, question in enumerate(short_answer_questions, 1):
                            f.write(f"{i}. {question['stem']}\n\n")
            
            QMessageBox.information(self, "成功", "试卷导出成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def print_paper(self):
        """打印试卷"""
        if not self.generated_paper:
            QMessageBox.warning(self, "警告", "请先生成试卷")
            return
            
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            # 创建文档并打印
            document = QTextDocument()
            document.setHtml(self.generate_html_paper())
            document.print_(printer)



class questionWidget(QWidget):
    """题目显示组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_question = None
        self.user_answer = None
        self.errorbook = errorbook.Error('errorbook.db')
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
        self.answer_label.hide()
        
        self.analysis_webview = QWebEngineView()
        self.analysis_webview.hide()

        
        layout.addWidget(self.answer_label)
        layout.addWidget(self.analysis_webview)
        
    def on_option_selected(self, button):
        self.user_answer = button.text()[0]  # 获取选项字母
    
    def set_question(self, question):
        self.current_question = question
        self.user_answer = None
        self.options_group.setExclusive(False)
        for radio, _ in self.option_widgets:
            radio.setChecked(False)
        self.options_group.setExclusive(True)
        
        # 隐藏解析
        self.answer_label.hide()
        self.analysis_webview.hide()
        
        # 设置题目类型
        question_type = question['typeid']
        
        self.type_label.setText(f"题目ID: {question['id']} | 类型: {question['type']} | 难度: {question['difficulty']}")
        
        # 设置题目内容
        self.stem_text.setPlainText(question['stem'])
        
        # 设置选项
        options = question['options']
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
        if question_type == 2:  # 判断题
            self.option_widgets[0][1].setText("错误")
            self.option_widgets[1][1].setText("正确")
            self.option_widgets[0][0].show()
            self.option_widgets[1][1].show()
            self.option_widgets[0][1].show()
            self.option_widgets[1][0].show()
            for i in range(2, 7):
                self.option_widgets[i][0].hide()
                self.option_widgets[i][1].hide()
    
    def show_answer(self):
        if self.current_question:
            if self.current_question['typeid'] == 3:
                correct_answer = " ".join(eval(self.current_question['answer']))
                self.answer_label.setText(f"正确答案: {correct_answer}")
            elif self.current_question['typeid'] == 2:
                correct_answer = self.current_question['answer']
                self.answer_label.setText(['错误','正确'][int(self.current_question['answer'])])
            elif self.current_question['typeid'] == 1:
                correct_answer = self.current_question['answer']
                self.answer_label.setText(LETTERS[int(self.current_question['answer'])])
            else:
                correct_answer = self.current_question['answer']
                self.answer_label.setText(f"正确答案: {correct_answer}")
            self.answer_label.show()
            
            if self.current_question['analysis']:
                self.analysis_webview.setHtml(self.current_question['analysis'])
                self.analysis_webview.show()
    
    def check_answer(self):
        letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        if not self.current_question or self.user_answer is None:
            return None, "请先选择答案"
        
        correct_answer = self.current_question['answer']
        is_correct = (self.user_answer.upper() == letter[int(correct_answer)])
        wquestion = self.current_question.copy()
        wquestion['iscorrect'] = is_correct
        wquestion["questionid"] = wquestion.pop("id")
        wquestion["question_type"] = wquestion.pop("type")
        wquestion["useranswer"] = self.user_answer
        self.errorbook.add_question(**wquestion)

        if is_correct:
            return True, "回答正确！"
        else:
            return False, f"回答错误！正确答案是: {letter[int(correct_answer)]}"
        

class questionManager(QWidget):
    """题目管理组件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_question_id = None
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # 左侧题目列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.question_list = QListWidget()
        self.question_list.currentRowChanged.connect(self.on_question_selected)
        left_layout.addWidget(QLabel("题目列表:"))
        left_layout.addWidget(self.question_list)
        
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
        self.new_btn.clicked.connect(self.new_question)
        button_layout.addWidget(self.new_btn)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_question)
        button_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_question)
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
        self.question_list.clear()
        questions = self.db_manager.get_all_questions()
        for question in questions:
            stem_preview = question['stem'][:10] if question['stem'] else 'Cant Preview'
            self.question_list.addItem(f"{question['id']}: {stem_preview}")
    
    def on_question_selected(self, row):
        if row >= 0:
            questions = self.db_manager.get_all_questions()
            if row < len(questions):
                self.current_question_id = questions[row]['id']
                self.load_question(questions[row])
    
    def load_question(self, question):
        self.type_combo.setCurrentIndex(question['typeid'])
        self.stem_edit.setPlainText(question['stem'])
        
        # 加载选项
        options = question['options']
        for i, edit in enumerate(self.option_edits):
            if i < len(options):
                edit.setText(options[i])
            else:
                edit.setText("")
        
        self.answer_edit.setText(question['answer'] or "")
        self.analysis_edit.setPlainText(question['analysis'] or "")
        self.difficulty_spin.setValue(question['difficulty'])
        self.chapter_spin.setValue(question['chapter'])
        self.bankid_spin.setValue(question['bankid'])
    
    def new_question(self):
        self.current_question_id = None
        self.type_combo.setCurrentIndex(1)  # 默认选择题
        self.stem_edit.clear()
        for edit in self.option_edits:
            edit.clear()
        self.answer_edit.clear()
        self.analysis_edit.clear()
        self.difficulty_spin.setValue(1)
        self.chapter_spin.setValue(0)
        self.bankid_spin.setValue(0)
    
    def save_question(self):
        # 收集数据
        question_type = self.type_combo.currentIndex()
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
        
        if question_type == 1 and not options:  # 选择题需要选项
            QMessageBox.warning(self, "警告", "选择题需要至少一个选项")
            return
        
        if not answer:
            QMessageBox.warning(self, "警告", "答案不能为空")
            return
        
        # 保存到数据库
        if self.current_question_id:
            # 更新现有题目
            self.db_manager.update_question(
                self.current_question_id,
                stem=stem,
                options=json.dumps(options, ensure_ascii=False),
                answer=answer,
                analysis=analysis,
                question_type=question_type,
                bankid=bankid,
                chapter=chapter,
                difficulty=difficulty
            )
            QMessageBox.information(self, "成功", "题目更新成功")
        else:
            # 添加新题目
            self.db_manager.add_question(
                stem=stem,
                options=json.dumps(options, ensure_ascii=False),
                answer=answer,
                analysis=analysis,
                question_type=question_type,
                bankid=bankid,
                chapter=chapter,
                difficulty=difficulty
            )
            QMessageBox.information(self, "成功", "题目添加成功")
        
        # 刷新列表
        self.refresh_list()
    
    def delete_question(self):
        if not self.current_question_id:
            QMessageBox.warning(self, "警告", "请先选择一个题目")
            return
        
        reply = QMessageBox.question(self, "确认", "确定要删除这个题目吗？", 
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db_manager.delete_question(self.current_question_id)
            QMessageBox.information(self, "成功", "题目删除成功")
            self.new_question()
            self.refresh_list()


class PracticeWidget(QWidget):
    """练习组件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.question_widget = questionWidget()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        self.next_btn = QPushButton("刷新")
        self.next_btn.clicked.connect(self.next_question)
        control_layout.addWidget(self.next_btn)
        
        self.check_btn = QPushButton("检查答案")
        self.check_btn.clicked.connect(self.check_answer)
        control_layout.addWidget(self.check_btn)
        
        self.show_btn = QPushButton("显示解析")
        self.show_btn.clicked.connect(self.show_answer)
        control_layout.addWidget(self.show_btn)
       
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("题目ID:"))
        self.id_edit = QLineEdit("")
        id_layout.addWidget(self.id_edit)
        control_layout.addLayout(id_layout)
        
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
        layout.addWidget(self.question_widget)
        
        # 初始加载一道题
        self.next_question()
    
    def next_question(self):
        bankid = self.bank_combo.currentData()
        chapter = self.chapter_combo.currentData()
        question_type = self.type_combo.currentData()
        
        if self.id_edit.text():
            question = self.db_manager.get_question(self.id_edit.text())
            self.id_edit.setText('')
        else:
            question = self.db_manager.get_random_question(bankid, chapter, question_type)
        if question:
            self.question_widget.set_question(question)
        else:
            QMessageBox.information(self, "提示", "没有找到符合条件的题目")
    
    def check_answer(self):
        is_correct, message = self.question_widget.check_answer()
        if is_correct is not None:
            QMessageBox.information(self, "结果", message)

    def show_answer(self):
        self.question_widget.show_answer()


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.db_manager = Questions('ask.db')
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('刷题软件')
        self.setGeometry(100, 100, 800, 500)
        app.setStyleSheet("")
        
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
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 练习页面
        self.practice_widget = PracticeWidget(self.db_manager)
        self.tabs.addTab(self.practice_widget, "练习")
        
        # 管理页面
        self.manage_widget = questionManager(self.db_manager)
        self.tabs.addTab(self.manage_widget, "题目管理")

        self.paper_widget = PaperGenerator(self.db_manager)
        self.tabs.addTab(self.paper_widget, "试卷生成")
        
    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Dejavu Sans", 12)  # 你可以换成你喜欢的字体和字号
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

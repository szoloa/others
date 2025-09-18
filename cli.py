#!/bin/python

import argparse
import sys
import json
from Question import Questions
# ...existing code...

parser = argparse.ArgumentParser(description="题库管理命令行工具")
parser.add_argument('--add', action='store_true', help='添加题目')
parser.add_argument('--get', type=int, help='根据ID获取题目')
parser.add_argument('--delete', type=int, help='根据ID删除题目')
parser.add_argument('--list', action='store_true', help='列出所有题目')
parser.add_argument('--db', type=str, default='ask.db', help='数据库文件名')

# 添加题目参数
parser.add_argument('--stem', type=str, help='题干')
parser.add_argument('--options', type=str, help='选项，格式如：["A选项","B选项"]')
parser.add_argument('--answer', type=str, help='答案')
parser.add_argument('--analysis', type=str, help='解析')
parser.add_argument('--type', type=int, default=1, help='题目类型')
parser.add_argument('--bankid', type=int, default=0, help='题库ID')
parser.add_argument('--chapter', type=int, default=0, help='章节')
parser.add_argument('--difficulty', type=int, default=1, help='难度')
parser.add_argument('--typeid', type=int, default=0, help='类型ID')

args = parser.parse_args()
p = Questions(DB=args.db)

if args.add:
    if not args.stem:
        print("添加题目时必须提供 --stem")
        sys.exit(1)
    options = args.options if args.options else None
    if options:
        try:
            options = json.dumps(eval(options))
        except Exception:
            print("选项格式错误，应为Python列表字符串")
            sys.exit(1)
    pid = p.add_question(
        stem=args.stem,
        options=options,
        answer=args.answer,
        analysis=args.analysis,
        question_type=args.type,
        bankid=args.bankid,
        chapter=args.chapter,
        difficulty=args.difficulty,
        typeid=args.typeid
    )
    print(f"添加题目成功，ID={pid}")

elif args.get:
    prob = p.get_question(args.get)
    if prob:
        print(json.dumps(prob, ensure_ascii=False, indent=2))
    else:
        print("未找到该题目")

elif args.delete:
    p.delete_question(args.delete)
    print("题目已删除")

elif args.list:
    questions = p.get_all_questions()
    for prob in questions:
        print(f"ID={prob['id']} 题干={prob['stem'][:30]}...")

else:
    parser.print_help()

p.close()
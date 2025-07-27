# 导出为 Markdown
def export_result(text, summary, path="output.md"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# 会议全文\n\n")
        f.write(text + "\n\n")
        f.write("# 自动摘要\n\n")
        f.write(summary)

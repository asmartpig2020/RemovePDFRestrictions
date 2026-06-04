import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES
from pdf_processor import check_restrictions, remove_restrictions


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF限制移除工具")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.files = []
        self._build_ui()
        self._setup_drop()

    def _build_ui(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="选择PDF文件", command=self._select_files).pack(side=tk.LEFT)
        ttk.Button(top_frame, text="选择文件夹", command=self._select_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="清空列表", command=self._clear_files).pack(side=tk.LEFT)
        ttk.Label(top_frame, text="(支持拖拽文件到列表)", foreground="gray").pack(side=tk.LEFT, padx=10)

        pw_frame = ttk.Frame(self.root, padding=(10, 0))
        pw_frame.pack(fill=tk.X)
        ttk.Label(pw_frame, text="密码(如需要):").pack(side=tk.LEFT)
        self.pw_var = tk.StringVar()
        ttk.Entry(pw_frame, textvariable=self.pw_var, show="*", width=30).pack(side=tk.LEFT, padx=5)

        list_frame = ttk.LabelFrame(self.root, text="文件列表", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("file", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.tree.heading("file", text="文件路径")
        self.tree.heading("status", text="状态")
        self.tree.column("file", width=420)
        self.tree.column("status", width=120)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        info_frame = ttk.LabelFrame(self.root, text="权限信息", padding=5)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        self.info_text = tk.Text(info_frame, height=5, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)

        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="检测限制", command=self._check_restrictions).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="移除限制并保存", command=self._remove_restrictions).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="批量移除并保存", command=self._batch_remove).pack(side=tk.LEFT)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _setup_drop(self):
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event):
        raw = event.data
        paths = self._parse_dnd_paths(raw)
        for p in paths:
            p = p.strip()
            if not p:
                continue
            if os.path.isdir(p):
                self._add_folder(p)
            elif p.lower().endswith(".pdf") and p not in self.files:
                self.files.append(p)
                self.tree.insert("", tk.END, iid=p, values=(p, "未检测"))

    def _parse_dnd_paths(self, data):
        paths = []
        buf = ""
        in_brace = False
        for ch in data:
            if ch == "{":
                in_brace = True
                buf = ""
            elif ch == "}":
                in_brace = False
                paths.append(buf)
            elif ch == " " and not in_brace:
                if buf:
                    paths.append(buf)
                    buf = ""
            else:
                buf += ch
        if buf:
            paths.append(buf)
        return paths

    def _add_folder(self, folder):
        for f in os.listdir(folder):
            if f.lower().endswith(".pdf"):
                path = os.path.join(folder, f)
                if path not in self.files:
                    self.files.append(path)
                    self.tree.insert("", tk.END, iid=path, values=(path, "未检测"))

    def _select_files(self):
        paths = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")],
        )
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.tree.insert("", tk.END, iid=p, values=(p, "未检测"))

    def _select_folder(self):
        folder = filedialog.askdirectory(title="选择文件夹")
        if not folder:
            return
        self._add_folder(folder)

    def _clear_files(self):
        self.files.clear()
        self.tree.delete(*self.tree.get_children())
        self._set_info("")

    def _set_info(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state=tk.DISABLED)

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        path = sel[0]
        password = self.pw_var.get()
        try:
            info = check_restrictions(path, password)
            lines = [f"加密: {'是' if info.is_encrypted else '否'}"]
            if info.is_encrypted:
                lines.append(f"用户密码: {'有' if info.has_user_password else '无'}")
                lines.append(f"权限密码: {'有' if info.has_owner_password else '无'}")
            for label, allowed in info.permissions.items():
                lines.append(f"{label}: {'允许' if allowed else '禁止'}")
            self._set_info("\n".join(lines))
        except ValueError as e:
            self._set_info(f"检测失败: {e}")

    def _check_restrictions(self):
        password = self.pw_var.get()
        for path in self.files:
            try:
                info = check_restrictions(path, password)
                restricted = any(not v for v in info.permissions.values())
                status = "有限制" if restricted else "无限制"
                if info.is_encrypted:
                    status += " (已加密)"
                self.tree.set(path, "status", status)
            except ValueError as e:
                self.tree.set(path, "status", f"错误: {e}")

    def _remove_restrictions(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先选择一个文件")
            return
        path = sel[0]
        password = self.pw_var.get()

        output = filedialog.asksaveasfilename(
            title="保存为",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")],
            initialfile=os.path.basename(path),
        )
        if not output:
            return

        try:
            remove_restrictions(path, output, password)
            self.tree.set(path, "status", "已移除限制")
            messagebox.showinfo("成功", f"已保存到:\n{output}")
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def _batch_remove(self):
        if not self.files:
            messagebox.showwarning("提示", "请先添加文件")
            return

        output_dir = filedialog.askdirectory(title="选择输出文件夹")
        if not output_dir:
            return

        password = self.pw_var.get()
        success = 0
        fail = 0

        for path in self.files:
            try:
                output = os.path.join(output_dir, os.path.basename(path))
                remove_restrictions(path, output, password)
                self.tree.set(path, "status", "已移除限制")
                success += 1
            except ValueError as e:
                self.tree.set(path, "status", f"错误: {e}")
                fail += 1

        messagebox.showinfo("完成", f"成功: {success}\n失败: {fail}")

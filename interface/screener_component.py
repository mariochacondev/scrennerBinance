import tkinter as tk
import tkinter.ttk as ttk
import time
from functools import partial
from interface.styling import *


class SortableTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_auto_sort = time.time()
        self.last_sort = None

    def heading(self, column, sort_by=None, **kwargs):
        if sort_by and not hasattr(kwargs, 'command'):
            func = getattr(self, f"_sort_by_{sort_by}", None)
            if func:
                kwargs['command'] = partial(func, column, False)
        return super().heading(column, **kwargs)

    def sort_column(self, column, reverse, data_type, callback, keep_order=False):
        if column == "#0":
            l = [(k, k) for k in self.get_children('')]
        else:
            l = [(self.set(k, column), k) for k in self.get_children('')]
        l.sort(key=lambda t: data_type(str(t[0]).replace("%", "")), reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.move(k, '', index)

        if keep_order:
            self.heading(column, command=partial(callback, column, reverse))
        else:
            self.heading(column, command=partial(callback, column, not reverse))

        self.last_sort = (column, reverse, data_type, callback)

    def _sort_by_num(self, column, reverse):
        self.sort_column(column, reverse, float, self._sort_by_num)

    def _sort_by_name(self, column, reverse):
        self.sort_column(column, reverse, str, self._sort_by_name)


class Screener(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self._headers = ['symbol', 'close', 'high', 'low', 'open',
                         'twap', 'fibo_382', 'bbs_signal']

        def fixed_map(option):
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style = ttk.Style(self)
        style.theme_use("clam")  # Supports the fieldbackground option
        style.map('Treeview',
                  background=[('selected', SELECTED_BG)],
                  foreground=[('selected', SELECTED_FG)],
                  font=[('!selected', GLOBAL_FONT), ('selected', GLOBAL_FONT)])
        style.configure("Treeview", background=BG_COLOR, fieldbackground=BG_COLOR, foreground=FG_COLOR)
        style.map("Treeview", foreground=fixed_map("foreground"), background=fixed_map("background"))

        style.map("Treeview.Heading", background=[('selected', '!focus')])  # Disabble header highlight
        style.configure("Treeview.Heading", background=BG_COLOR_2, foreground=FG_COLOR, relief="flat", font=BOLD_FONT)

        # Create the Treeview

        self.tree = SortableTreeview(self, height=30)
        self.tree["columns"] = self._headers[1:]

        for col in self._headers[1:]:
            self.tree.column(col, anchor='w', width=150)
            self.tree.heading(col, text=col.capitalize(), anchor='w', sort_by="num")

        self.tree.column('#0', width=130)
        self.tree.heading('#0', text="Symbol", anchor='w', sort_by="name")

        self.tree.bind('<Button-1>', self.handle_click)

        self.tree.pack(side=tk.TOP, pady=15)

        self.symbols = []

    def handle_click(self, event):
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"  # So that Treeview columns are not resizable
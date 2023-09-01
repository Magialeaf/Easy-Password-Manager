'''
基本需求：
1.公私钥登录
2.界面：
    - 界面中有：分类，名称，账号，密码（私密（***），不可查看，点击后才能查看，可以复制），备注
3.设置：
    - 设置公钥，私钥，数据库路径。
______
basic:
1.签名数据生成方式修改
2.

extend:
1.拖拽输入私钥
# 2.拖拽修改ID
'''
import json
import os.path
from typing import Union
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, \
    QVBoxLayout, QHBoxLayout, QDesktopWidget, QStackedLayout, QTableWidget, QTableWidgetItem

import Content

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.table_name = ["ID", "分类", "应用", "账号", "密码", "备注", "解密", "删除"]

        self.init_font()
        self.init_window()

        self.stack = QStackedLayout(self)

        self.init_stack()

    def init_font(self):
        # 大字体
        self.title_font = QFont()
        self.title_font.setPointSize(20)
        self.title_font.setBold(True)

    def init_window(self, width=400, height=200, name="密码管理器") -> None:
        self.setWindowTitle(name)
        # 窗口属性 并 居中
        self.resize(width, height)
        center_point = QDesktopWidget().availableGeometry().center()
        x = center_point.x()
        y = center_point.y()
        self.move(x - width // 2, y - height // 2)

    def init_stack(self)->None:
        self.load_screen()
        self.register_screen()
        self.main_screen()

        self.stack.setCurrentIndex(0)

    def load_screen(self)->None:
        # 设置布局
        layout = QVBoxLayout()

        # 标题
        title_layout = QVBoxLayout()

        label_prompt = QLabel("密码管理器")
        label_prompt.setFont(self.title_font)

        title_layout.addWidget(label_prompt)

        # 数据库名称输入栏
        database_layout = QHBoxLayout()

        label_database = QLabel("数据库文件：")
        self.lineedit_database = QLineEdit()
        button_browse_database = QPushButton("浏览")

        database_layout.addWidget(label_database)
        database_layout.addWidget(self.lineedit_database)
        database_layout.addWidget(button_browse_database)

        # 签名输入栏
        sign_layout = QHBoxLayout()

        label_sign = QLabel("签名文件：  ")
        self.lineedit_sign = QLineEdit()
        button_browse_sign = QPushButton("浏览")

        sign_layout.addWidget(label_sign)
        sign_layout.addWidget(self.lineedit_sign)
        sign_layout.addWidget(button_browse_sign)

        # 确认栏
        login_layout = QHBoxLayout()

        button_login = QPushButton("登录")
        button_register = QPushButton("注册新账户")

        login_layout.addWidget(button_login)
        login_layout.addWidget(button_register)

        # 垂直布局加入水平布局中
        layout.addLayout(title_layout)
        layout.addLayout(database_layout)
        layout.addLayout(sign_layout)
        layout.addLayout(login_layout)
        self.setLayout(layout)

        # 连接信号和槽函数
        button_browse_database.clicked.connect(self.browse_database)
        button_browse_sign.clicked.connect(self.browse_sign)
        button_login.clicked.connect(self.login)
        button_register.clicked.connect(lambda: self.set_screen(1))

        widget = QWidget()
        widget.setLayout(layout)
        self.stack.addWidget(widget)

        self.default_database()

    def register_screen(self):
        # 创建垂直布局
        layout = QVBoxLayout()

        # 数据库名称输入栏
        database_layout = QHBoxLayout()

        database_label = QLabel("数据库名称:")
        database_entry = QLineEdit()

        database_layout.addWidget(database_label)
        database_layout.addWidget(database_entry)

        # 按钮栏
        register_layout = QHBoxLayout()

        back_button = QPushButton("返回")
        register_button = QPushButton("注册")

        register_layout.addWidget(back_button)
        register_layout.addWidget(register_button)

        # 将两个水平布局添加到垂直布局中
        layout.addLayout(database_layout)
        layout.addLayout(register_layout)

        # 绑定注册按钮的点击事件到注册函数
        back_button.clicked.connect(lambda: self.set_screen(0))
        register_button.clicked.connect(lambda: self.register(database_entry.text()))

        widget = QWidget()
        widget.setLayout(layout)
        self.stack.addWidget(widget)

    def main_screen(self):
        # 创建垂直布局
        layout = QVBoxLayout()

        # 创建第一个水平布局，包含 "+" 按钮、"-" 按钮、搜索框和搜索按键
        select_layout = QHBoxLayout()

        button_add = QPushButton("+")
        line_edit_search = QLineEdit()
        button_search = QPushButton("搜索")
        back_button = QPushButton("退出")

        select_layout.addWidget(button_add)
        select_layout.addWidget(line_edit_search)
        select_layout.addWidget(button_search)
        select_layout.addWidget(back_button)

        # 创建第二个水平布局，包含表格
        result_layout = QHBoxLayout()

        row = 8
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(row )  # 设置表格列数
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setHorizontalHeaderLabels(self.table_name)

        font = self.table_widget.horizontalHeader().font()
        font.setBold(True)
        self.table_widget.horizontalHeader().setFont(font)

        size = (45,90,120,120,200,200,50,50)
        for i in range(row):
            self.table_widget.horizontalHeader().resizeSection(i, size[i])

        self.table_widget.cellDoubleClicked.connect(self.inspect)  # 连接双击信号和 inspect 槽函数

        result_layout.addWidget(self.table_widget)

        # 将两个水平布局添加到垂直布局中
        layout.addLayout(select_layout)
        layout.addLayout(result_layout)

        # 绑定注册按钮的点击事件到注册函数
        button_add.clicked.connect(self.add_new_account)
        button_search.clicked.connect(lambda: self.search(line_edit_search.text()))
        back_button.clicked.connect(lambda: self.set_screen(0))

        # 创建 QWidget并设置属性，并将垂直布局设置为其布局
        widget = QWidget()
        widget.setLayout(layout)
        self.stack.addWidget(widget)

    def set_screen(self,index):
        if index == 0:
            global global_sign_path
            global global_private_key_verify
            global_sign_path = None
            global_private_key_verify = False

            self.lineedit_sign.clear()
            self.resize(400, 200)
        elif index == 2:
            self.init_table_row()
            width = 900
            height = 600
            self.resize(width, height)
            center_point = QDesktopWidget().availableGeometry().center()
            x = center_point.x()
            y = center_point.y()
            self.move(x - width // 2, y - height // 2)
        else:
            self.resize(400, 200)
        self.stack.setCurrentIndex(index)

    def new_table_item(self,text:str)->object:
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 禁用编辑功能
        item.setTextAlignment(Qt.AlignCenter)
        item.setBackground(QColor(255, 255, 255))
        return item

    def init_table_row(self,condition:Union[bool,list] = True):
        data = global_behavior.keyword_query(condition)
        row = len(data)
        self.table_widget.setRowCount(0)
        self.table_widget.setRowCount(row)

        for i, row_data in enumerate(data):
            for j, column_data in enumerate(row_data + ("解密","删除")):
                item = self.new_table_item(str(column_data)) # 将数据转换为字符串并创建表格项对象
                self.table_widget.setItem(i, j, item)  # 在指定位置添加表格项

    def inspect(self,row,col):
        mouse_event = QApplication.mouseButtons()
        if mouse_event == Qt.LeftButton:
            if col == 0:
                pass
            elif col == 1 or col == 5:
                self.modify_information_screen(self.table_widget.item(row, 0).text(),col,self.table_name[col],self.table_widget.item(row, col).text())
            elif col == 2 or col == 3:
                if global_private_key_verify == True:
                    self.modify_information_screen(self.table_widget.item(row, 0).text(), col, self.table_name[col],self.table_widget.item(row, col).text())
                else:
                    self.load_private_key_screen()
            elif col == 4:
                if self.table_widget.item(row, 6).text() == "加密":
                    self.modify_information_screen(self.table_widget.item(row, 0).text(),col,self.table_name[col],self.table_widget.item(row, col).text())
                else:
                    QMessageBox.warning(self, "修改失败", "请先解密再修改密码！")
            elif col == 6:
                if global_private_key_verify == True:
                    if self.table_widget.item(row, col).text() == "解密":
                        ciphertext = self.table_widget.item(row, 4).text()
                        plaintext = global_behavior.decode_password(global_private_path,ciphertext)
                        item = self.new_table_item(plaintext)
                        self.table_widget.setItem(row,4,item)

                        item = self.new_table_item("加密")
                        self.table_widget.setItem(row,col,item)
                    else:
                        plaintext  = self.table_widget.item(row, 4).text()
                        ciphertext = global_behavior.encode_password(global_private_path,plaintext)
                        item = self.new_table_item(ciphertext )
                        self.table_widget.setItem(row,4,item)

                        item = self.new_table_item("解密")
                        self.table_widget.setItem(row,col,item)
                else:
                    self.load_private_key_screen()
            elif col == 7:
                self.confirm_delete_screen(self.table_widget.item(row, 0).text())

    def default_database(self):
        # 判断config文件是否存在
        if not os.path.exists("Data\config.json"):
            global global_database_path
            global_database_path = None
            self.lineedit_database.clear()
        else:
            # 读取 config 文件中的 db_path 参数值
            with open("Data\config.json", "r") as f:
                data = json.load(f)
                db_path = data.get("db_path")
                if db_path:
                    global_database_path = db_path
                    base_name = os.path.basename(db_path)
                    self.lineedit_database.setText(base_name)
                else:
                    global_database_path = None
            f.close()

    def browse_database(self):
        default_dir = "./"
        file_dialog = QFileDialog()
        database_path, _ = file_dialog.getOpenFileName(self, "选择数据库",default_dir,'sqlite file (*.db);')
        global global_database_path
        global_database_path = database_path

        # 更新配置文件中的数据库路径
        config_file_path = "Data\config.json"  # 配置文件路径
        if os.path.isfile(config_file_path):  # 检查配置文件是否存在
            with open(config_file_path, "r+") as file:
                data = json.load(file)
                if "db_path" in data:  # 检查 "db_path" 是否存在于 JSON 中
                    data["db_path"] = database_path  # 更新 "db_path" 的值
                    file.seek(0)  # 将文件指针移到文件开头
                    json.dump(data, file, indent=4)  # 将更新后的数据写入文件
                    file.truncate()  # 截断文件，删除多余内容
        else:
            print("配置文件路径错误！")

        self.lineedit_database.setText(os.path.basename(database_path))

    def browse_sign(self):
        default_dir = "./"  # os.path.join(os.path.expanduser("~"), "Desktop")
        file_dialog = QFileDialog()
        sign_path, _ = file_dialog.getOpenFileName(self, "选择签名",default_dir,'txt file (*.txt);')
        global global_sign_path
        global_sign_path = sign_path
        self.lineedit_sign.setText("******")

    def login(self):
        database_path = global_database_path
        sign_path = global_sign_path

        if database_path and sign_path:
            res = global_behavior.verify_load(database_path,sign_path)
        else:
            res = False

        # 公私钥验证逻辑
        if res == True:
            QMessageBox.information(self, "登录成功", "密码正确！")
            # 进行跳转到下一界面
            self.set_screen(2)
        else:
            QMessageBox.warning(self, "登录失败", "数据库损坏或签名不匹配！")

    def register(self,DB_name):
        tip_tuple = global_behavior.register(DB_name)
        # 执行注册账户逻辑
        if tip_tuple[0] == True:
            QMessageBox.information(self, "注册成功", "数据和密钥已存入相应文件夹")
            self.set_screen(0)
        else:
            QMessageBox.warning(self, "注册失败", tip_tuple[1])

    def search(self,condition):
        """
        条件查询
        :param condition:查询或关键字查询（True表示全查询，否则就是关键字）
        """
        if condition == "":
            condition = True
        self.init_table_row(condition)

    def add_new_account(self):
        self.add_child_win = AddNewAccount()
        self.add_child_win.close_signal.connect(self.init_table_row)
        self.add_child_win.show()

    def confirm_delete_screen(self,id_value):
        if global_private_key_verify == True:
            self.delete_child_win = DeleteAccount(id_value)
            self.delete_child_win.close_signal.connect(self.init_table_row)
            self.delete_child_win.show()
        else:
            self.load_private_key_screen()

    def modify_information_screen(self,id_value,col,tip,text):
        self.modify_information_win = ModifyInformation(id_value,col,tip,text)
        self.modify_information_win.close_signal.connect(self.init_table_row)
        self.modify_information_win.show()

    def load_private_key_screen(self):
        self.load_private_key_win = LoadPrivate()
        self.load_private_key_win.show()

class AddNewAccount(QWidget):
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_window(400,200,"新增账号")

        self.init_window()
        self.add_new_screen()

    def init_window(self, width=400, height=200, name="添加账号") -> None:
        self.setWindowTitle(name)
        # 窗口属性 并 居中
        self.resize(width, height)
        center_point = QDesktopWidget().availableGeometry().center()
        x = center_point.x()
        y = center_point.y()
        self.move(x - width // 2, y - height // 2)

    def add_new_screen(self):
        # 创建垂直布局
        layout = QVBoxLayout()

        # "分类"和输入框水平布局
        category_layout = QHBoxLayout()
        category_label = QLabel("分类")
        self.category_input = QLineEdit()
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_input)

        # "应用"和输入框水平布局
        app_layout = QHBoxLayout()
        app_label = QLabel("应用")
        self.app_input = QLineEdit()
        app_layout.addWidget(app_label)
        app_layout.addWidget(self.app_input)

        # "账号"和输入框水平布局
        account_layout = QHBoxLayout()
        account_label = QLabel("账号")
        self.account_input = QLineEdit()
        account_layout.addWidget(account_label)
        account_layout.addWidget(self.account_input)

        # "密码"和输入框水平布局
        password_layout = QHBoxLayout()
        password_label = QLabel("密码")
        self.password_input = QLineEdit()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        # "备注"和输入框水平布局
        note_layout = QHBoxLayout()
        note_label = QLabel("备注")
        self.note_input = QLineEdit()
        note_layout.addWidget(note_label)
        note_layout.addWidget(self.note_input)

        # "取消"按钮和"确认"按钮水平布局
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("取消")
        confirm_button = QPushButton("确认")
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(confirm_button)

        # 将水平布局添加到垂直布局
        layout.addLayout(category_layout)
        layout.addLayout(app_layout)
        layout.addLayout(account_layout)
        layout.addLayout(password_layout)
        layout.addLayout(note_layout)
        layout.addLayout(buttons_layout)

        cancel_button.clicked.connect(self.exit_win)
        confirm_button.clicked.connect(self.add_new_account)

        # 添加其他代码...
        self.setLayout(layout)
        self.show()

    def add_new_account(self):
        class_value = self.category_input.text()
        name = self.app_input.text()
        account = self.account_input.text()
        password = self.password_input.text()
        note = self.note_input.text()

        data = [class_value,name,account,password,note]

        global global_private_key_verify
        if global_private_key_verify == False:
            self.load_private_key = LoadPrivate()
            self.load_private_key.show()
        else:
            res = global_behavior.insert_data(data,global_private_path)
            if res[0] == True:
                res = global_behavior.update_signature(global_sign_path,global_private_path,global_database_path)
                if res == True:
                    QMessageBox.information(self,"插入成功","数据插入成功！")
                    self.close_signal.emit()
                    self.exit_win()
                else:
                    QMessageBox.warning(self, "签名失败", "数据插入成功，签名失败！")
            else:
                QMessageBox.warning(self,"插入失败",res[1])

    def exit_win(self):
        self.close()

class DeleteAccount(QWidget):
    close_signal = pyqtSignal()

    def __init__(self,id_value):
        super().__init__()

        self.id_value = id_value
        self.init_window()
        self.confirm_delete_screen()

    def init_window(self, width=200, height=100, name="删除账号") -> None:
        self.setWindowTitle(name)
        # 窗口属性 并 居中
        self.resize(width, height)
        center_point = QDesktopWidget().availableGeometry().center()
        x = center_point.x()
        y = center_point.y()
        self.move(x - width // 2, y - height // 2)

    def confirm_delete_screen(self):
        # 创建垂直布局
        layout = QVBoxLayout()

        # 创建提示语标签
        label = QLabel("你确认要删除吗？")
        layout.addWidget(label)

        # 创建水平布局
        h_layout = QHBoxLayout()

        # 创建取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.exit_win)
        h_layout.addWidget(cancel_btn)

        # 创建确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.clicked.connect(self.confirm_delete)
        h_layout.addWidget(confirm_btn)

        # 将水平布局添加到垂直布局中
        layout.addLayout(h_layout)

        # 设置窗口布局
        self.setLayout(layout)

    def confirm_delete(self):
        res = global_behavior.delete_data(self.id_value)
        if res == True:
            res = global_behavior.update_signature(global_sign_path, global_private_path, global_database_path)
            if res == True:
                QMessageBox.information(self,"删除成功","第" + self.id_value + "条数据已被删除！")
                self.close_signal.emit()
                self.exit_win()
            else:
                QMessageBox.warning(self, "签名失败", "第" + self.id_value + "条数据已被删除，但签名失败！")
        else:
            QMessageBox.warning(self,"删除失败","删除失败！")

    def exit_win(self):
        self.close()

class LoadPrivate(QWidget):
    def __init__(self):
        super().__init__()

        self.init_window()
        self.load_private_key()

    def init_window(self, width=400, height=200, name="载入私钥") -> None:
        self.setWindowTitle(name)
        # 窗口属性 并 居中
        self.resize(width, height)
        center_point = QDesktopWidget().availableGeometry().center()
        x = center_point.x()
        y = center_point.y()
        self.move(x - width // 2, y - height // 2)

    def load_private_key(self):
        # 设置布局
        layout = QVBoxLayout()

        # 签名输入栏
        private_layout = QHBoxLayout()

        label_sign = QLabel("私钥")
        self.lineedit_private_key = QLineEdit()
        button_browse_private = QPushButton("浏览")

        private_layout.addWidget(label_sign)
        private_layout.addWidget(self.lineedit_private_key)
        private_layout.addWidget(button_browse_private)

        # "取消"按钮和"确认"按钮水平布局
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("取消")
        confirm_button = QPushButton("确认")
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(confirm_button)

        # 垂直布局加入水平布局中
        layout.addLayout(private_layout)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # 连接信号和槽函数
        button_browse_private.clicked.connect(self.browse_private)
        cancel_button.clicked.connect(self.exit_win)
        confirm_button.clicked.connect(self.verify_private_key)

    def browse_private(self):
        default_dir = "./"  # os.path.join(os.path.expanduser("~"), "Desktop")
        file_dialog = QFileDialog()
        private_key_path, _ = file_dialog.getOpenFileName(self, "选择私钥",default_dir,'pem file (*.pem);')
        global global_private_path
        global_private_path = private_key_path
        self.lineedit_private_key.setText("******")

    def verify_private_key(self):
        res = global_behavior.verify_private_key(global_sign_path,global_private_path)
        if res == True:
            QMessageBox.information(self,"验证结果","验证通过！")
            global global_private_key_verify
            global_private_key_verify = True
            self.exit_win()
        else:
            QMessageBox.warning(self,"验证结果","验证失败！")

    def exit_win(self):
        self.close()

class ModifyInformation(QWidget):
    close_signal = pyqtSignal()

    def __init__(self,id_value,col,tip,text):
        super().__init__()

        self.id_value = id_value
        self.col = col
        self.tip = tip
        self.text = text

        self.init_window()
        self.load_private_key()

    def init_window(self, width=400, height=200, name="修改信息") -> None:
        self.setWindowTitle(name)
        # 窗口属性 并 居中
        self.resize(width, height)
        center_point = QDesktopWidget().availableGeometry().center()
        x = center_point.x()
        y = center_point.y()
        self.move(x - width // 2, y - height // 2)

    def load_private_key(self):
        # 设置布局
        layout = QVBoxLayout()

        # 签名输入栏
        information_layout = QHBoxLayout()

        label_information= QLabel(self.tip)
        self.lineedit_information = QLineEdit()
        self.lineedit_information.setText(self.text)

        information_layout.addWidget(label_information)
        information_layout.addWidget(self.lineedit_information)

        # "取消"按钮和"确认"按钮水平布局
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("取消")
        confirm_button = QPushButton("确认")
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(confirm_button)

        # 垂直布局加入水平布局中
        layout.addLayout(information_layout)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # 连接信号和槽函数
        cancel_button.clicked.connect(self.exit_win)
        confirm_button.clicked.connect(self.modify_information)

    def modify_information(self):
        if self.lineedit_information.text() == "" and self.col != 5:
            QMessageBox.warning(self,"修改失败！",self.tip + "不能为空！")
        else:
            text = self.lineedit_information.text()
            if self.col == 4:
                text = global_behavior.encode_password(global_private_path,text)
            res = global_behavior.modify_data(self.id_value,self.col,text)
            if res == True:
                QMessageBox.information(self,"修改成功","数据修改成功！")
                self.close_signal.emit()
                self.exit_win()
            else:
                QMessageBox.warning(self, "修改失败", "数据修改失败！")

    def exit_win(self):
        self.close()

if __name__ == "__main__":
    # 全局变量
    global_database_path = None
    global_sign_path = None
    global_private_key_verify = False
    global_private_path = None

    global_behavior = Content.Behavior()

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


import sqlite3
import os
from typing import Union

from KeyMaker import CryptoControl
import json

class DBControl:
    """
    数据库操作函数
    """
    def __init__(self,DB_name = "NewDatabase"):
        self.__DBPath = "Data/" + DB_name + ".db"
        self.name_list = ["id","class","name","account","password","note"]

    def modify_database_path(self,DB_path)->None:
        """
        修改载入的数据库路径

        :param DB_path: 路径
        :return: None
        """
        self.__DBPath = DB_path

    def __connectDB(self)->None:
        """
        连接到数据库（如果数据库不存在，则会创建一个新的数据库文件）
        :return: None
        """
        self.__conn = sqlite3.connect(self.__DBPath)

    def __closeDB(self)->None:
        """
        提交更改并关闭连接
        :return: None
        """
        self.__conn.commit()
        self.__conn.close()

    def init_table(self)->tuple:
        """
        初始化数据库以及相关信息

        :return: （结果，结果语句）元组
        """
        try:
            if os.path.exists(self.__DBPath) == False:
                self.__connectDB()

                p = self.__conn.cursor()

                p.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='public_key'")
                result = p.fetchone()

                if result:
                    return False,"公钥表已存在"
                else:
                    publicKeySql = '''CREATE TABLE public_key (
                                pubkey nvarchar(600) NOT NULL
                            )'''
                    p.execute(publicKeySql)

                if self.__init_key() == False:
                    return False,"初始化密钥失败"

                p.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='password'")
                result = p.fetchone()

                if result:
                    return False,"密码表已存在"
                else:
                    passwordSql = '''CREATE TABLE password (
                                id integer primary key,
                                class nvarchar(10) NOT NULL,
                                name nvarchar(30) NOT NULL,
                                account nvarchar(30) NOT NULL,
                                password nvarchar(18) NOT NULL,
                                note nvarchar(50)
                            )'''
                    p.execute(passwordSql)

                self.__closeDB()

                res = self.__init_config()

                if res == False:
                    return False, "配置文件初始化失败"

                return True," "

            else:
                return False,"数据库已存在"
        except:
            return False,"未知异常！"

    def __init_key(self)->bool:
        """
        将公钥存入数据库
        :return: 是否成功
        """
        DB_name = os.path.splitext(os.path.basename(self.__DBPath))[0]
        public,private = CryptoControl.generate_rsa_key_pair()
        CryptoControl.save_rsa_key_pair(DB_name,public,private)

        cursor = self.__conn.cursor()
        cursor.execute("INSERT INTO public_key (pubkey) VALUES (?)", (public,))
        self.__conn.commit()

        res = CryptoControl.load_rsa_key_pair("Key/" + DB_name + "Publickey.pem", "Key/" + DB_name + "Privatekey.pem")

        if res != False:
            public_key = res[0]
            private_key = res[1]

            sign = CryptoControl.sign_database("", private_key)
            CryptoControl.save_signature(sign, DB_name)

            return CryptoControl.verify_signature(sign,"", public_key)
        else:
            return False

    def __init_config(self)->bool:
        """
        初始化配置文件

        :return: 是否成功初始化
        """
        try:
            if os.path.exists("Data\config.json") == False:
                data = {
                    "author": "Magialeaf",
                    "version": "0.9",
                    "db_path": self.__DBPath
                }

                # 将数据写入 JSON 文件
                with open("Data\config.json", "w") as file:
                    json.dump(data, file, indent=4)

                return True
            else:
                return True
        except:
            return False

    def select_public_key(self)->Union[bool,bytes]:
        """
        获得数据库中的公钥

        :return: False或者公钥
        """
        self.__connectDB()
        p = self.__conn.cursor()
        try:
            p.execute("SELECT pubkey FROM public_key")
            result = p.fetchone()

            self.__closeDB()

            if result is not None:
                first_row = result[0]  # 获取第一行的结果
            else:
                first_row = False
        except sqlite3.DatabaseError:
            first_row = False
        return first_row

    def select_verify_data(self):
        """
        获得数据库中的（应用+账号+密码）数据并联合用于验证数据正确性
        """
        self.__connectDB()

        p = self.__conn.cursor()
        p.execute("SELECT name,account,password FROM password")
        result = p.fetchall()

        self.__closeDB()

        res = ""
        count = 0
        if result is not None:
            for row in result:
                if count == 10:
                    res = str(CryptoControl.hash(res))
                    count = 0
                for i in range(len(row)):
                    res += row[i]
                count += 1

        return res

    def select_data(self, condition: Union[bool, str]) -> list:
        """
        按指定参数查询结果并返回
        :param: condition:全查询或关键字查询（True表示全查询，否则就是关键字）
        :return: 所有数据结果
        """
        self.__connectDB()
        p = self.__conn.cursor()
        if condition == True:
            p.execute("SELECT * FROM password")
        else:
            p.execute(
                "SELECT * FROM password WHERE id LIKE ? OR class LIKE ? OR name LIKE ? OR account LIKE ? OR note LIKE ?",
                ('%' + condition + '%', '%' + condition + '%', '%' + condition + '%', '%' + condition + '%',
                 '%' + condition + '%'))

        result = p.fetchall()
        self.__closeDB()
        return result

    def select_row(self)->int:
        """
        查询数据库的行数

        :return:行数
        """
        self.__connectDB()
        p = self.__conn.cursor()

        p.execute("SELECT COUNT(*) FROM password")
        result = p.fetchone()[0]

        self.__closeDB()
        return result

    def insert_data(self,data:list,private_path:str)->bool:
        """
        插入单条数据

        :param: data: 数据列表 [分类，应用名，账号，密码，备注]
        :param private_path: 私钥路径
        :return: 插入是否成功
        """
        id_value = self.select_row() + 1

        self.__connectDB()
        p = self.__conn.cursor()
        class_value,name,account,password,note = data
        key = CryptoControl.make_key(private_path)
        password = CryptoControl.en_AES(password,key)
        try:
            p.execute("INSERT INTO password (id, class, name, account, password, note) VALUES (?, ?, ?, ?, ?, ?)",
                      (id_value, class_value, name, account, password, note))
            self.__conn.commit()
            self.__closeDB()
            return True
        except:
            self.__conn.rollback()
            self.__closeDB()
            return False

    def delete_data(self, id_value: int) -> bool:
        """
        删除单条数据

        :param id_value: id号
        :return: 删除是否成功
        """
        self.__connectDB()
        p = self.__conn.cursor()

        try:
            # 先删除指定id的数据
            delete_sql = "DELETE FROM password WHERE id = ?"
            p.execute(delete_sql, (id_value,))
            self.__conn.commit()

            # 更新后续id号
            update_sql = "UPDATE password SET id = id - 1 WHERE id > ?"
            p.execute(update_sql, (id_value,))
            self.__conn.commit()

            self.__closeDB()
            return True
        except:
            self.__conn.rollback()
            self.__closeDB()
            return False
    def modify_data(self,id_value:int,col:int,new_data)->bool:
        """
        修改单条数据

        :param id_value: id号
        :param col: 修改的列
        :param new_data: 新数据
        :return: 修改是否成功
        """
        self.__connectDB()
        p = self.__conn.cursor()

        sql = f"UPDATE password SET " + self.name_list[col] + " = ? WHERE id = ?"
        try:
            p.execute(sql,(new_data,id_value))
            self.__conn.commit()
            self.__closeDB()
            return True
        except:
            self.__conn.rollback()
            self.__closeDB()
            return False
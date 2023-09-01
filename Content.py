from typing import Union

import DBSql
import os
from KeyMaker import CryptoControl

class Behavior:
    """
    开始登录的界面的相关函数
    """
    def __init__(self):
        self.key = None

        self.db = DBSql.DBControl()

    def verify_load(self,DB_path:str,sign_path:str)->bool:
        """
        验证数据库中的公钥能否验证数字签名

        :param DB_path: 数据库路径
        :param sign_path: 签名路径
        :return: 验证结果
        """
        self.db.modify_database_path(DB_path)
        pubkey = self.db.select_public_key()
        if pubkey != False:
            signature = CryptoControl.load_signature(sign_path)
            data = self.db.select_verify_data()
            res = CryptoControl.verify_signature(signature,data,pubkey)

            return res
        else:
            return False

    def register(self,DB_name:str)->tuple:
        """
        输入数据库名进行注册

        :param DB_name: 数据库名称
        :return:  （结果，结果语句）元组
        """
        if not os.path.exists("./Data"):
            os.makedirs("./Data")

        if not os.path.exists("./Key"):
            os.makedirs("./Key")

        if DB_name != "":
            DB_path = "./Data/" + DB_name + ".db"
            self.db.modify_database_path(DB_path)
        return self.db.init_table()

    def update_signature(self,sign_path:str,private_path:str,DB_path:str)->bool:
        """
        更新签名

        :param sign_path: 签名路径
        :param private_path: 私钥路径
        :param DB_name: 数据库路径
        :return: 更新结果
        """
        try:
            data = self.db.select_verify_data()
            private_key = CryptoControl.load_rsa_private_key(private_path)
            sign = CryptoControl.sign_database(data,private_key)
            DB_name = os.path.basename(DB_path).split(".")[0]

            CryptoControl.save_signature(sign,DB_name)
            return True
        except:
            return False

    def verify_private_key(self,sign_path:str,private_path:str)->bool:
        """
        验证私钥

        :param sign_path: 签名路径
        :param private_path: 私钥路径
        :return: 验证结果
        """
        try:
            private_key = CryptoControl.load_rsa_private_key(private_path)
            new_sign = CryptoControl.sign_database(self.db.select_verify_data(),private_key)

            public_key = self.db.select_public_key()
            if public_key != False:
                res = CryptoControl.verify_signature(new_sign,self.db.select_verify_data(),public_key)
                if res == True:
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

    def keyword_query(self,condition:Union[bool,str])->list:
        """
        按指定参数查询结果并返回

        :param: condition:全查询或关键字查询（True表示全查询，否则就是关键字）
        :return: 结果集
        """
        res = self.db.select_data(condition)
        return res


    def insert_data(self,data:list,private_path:str)->tuple:
        """
        向数据库插入数据

        :param data: 数据列表 [分类，应用名，账号，密码，备注]
        :param private_path: 私钥路径
        :return: （插入结果，提示语句）
        """
        class_value, name, account, password, note = data
        if class_value == "":
            return False,"分类不能为空"
        if name == "":
            return False,"应用名不能为空"
        if account == "":
            return False,"账号不能为空"
        if password == "":
            return False,"密码不能为空"
        return self.db.insert_data(data,private_path),"插入失败"


    def delete_data(self,id_value:int)->bool:
        """
        删除数据库中的指定数据

        :param id_value: 删除的id号
        :return: 删除结果
        """
        return self.db.delete_data(id_value)

    def modify_data(self,id_value:int,col:int,new_data:str)->bool:
        """
        修改数据

        :param row: ID值
        :param col: 列
        :param new_data: 新数据
        :return: 是否修改成功
        """
        return self.db.modify_data(id_value,col,new_data)


    def decode_password(self,private_path:str,ciphertext:str)->str:
        """
        对指定密码进行解密

        :param private_path: 私钥路径
        :param ciphertext: 密文
        :return: 明文
        """
        if self.key is None:
            self.key = CryptoControl.make_key(private_path)
        return CryptoControl.de_AES(ciphertext,self.key)

    def encode_password(self,private_path:str,plaintext:str)->str:
        """
        对指定密码进行加密

        :param private_path: 私钥路径
        :param plaintext: 明文
        :return: 明文
        """
        if self.key is None:
            self.key = CryptoControl.make_key(private_path)
        return CryptoControl.en_AES(plaintext,self.key)
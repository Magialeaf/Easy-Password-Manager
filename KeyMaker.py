from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from typing import Union
import hashlib

class CryptoControl:
    """
    密钥相关函数
    """
    @staticmethod
    def generate_rsa_key_pair()->tuple:
        """
        生成RSA密钥对

        :return: （公钥，私钥）元组
        """
        # 使用默认的密钥长度 (2048 bits) 和默认的公钥指数 (65537) 来生成 RSA 密钥对
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # 从私钥中提取公钥
        public_key = private_key.public_key()

        # 将密钥对序列化为 PEM 格式
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return public_pem, private_pem

    @staticmethod
    def save_rsa_key_pair(DB_name:str,public_pem:bytes, private_pem:bytes)->None:
        """
        保存RSA密钥对到文件

        :param DB_name: 数据库名称，用于指定密钥对文件的路径或名称
        :param public_pem: 公钥对应的PEM格式字符串
        :param private_pem: 私钥对应的PEM格式字符串
        :return: 无返回值
        """
        # 将私钥写入 private.pem 文件
        privatePath =  "Key/" + DB_name +"Privatekey.pem"
        with open(privatePath, "wb") as private_file:
            private_file.write(private_pem)

        # 将公钥写入 public.pem 文件
        publicPath = "Key/" + DB_name + "Publickey.pem"
        with open(publicPath, "wb") as public_file:
            public_file.write(public_pem)

    @staticmethod
    def load_rsa_key_pair(public_key_path:str, private_key_path:str)-> Union[bool, tuple]:
        """
        从文件中加载RSA密钥对

        :param public_key_path: 公钥存储路径
        :param private_key_path: 私钥存储路径
        :return:加载成功返回（公钥，私钥）元组，失败返回False
        """
        try:
            # 加载私钥和公钥
            with open(public_key_path, 'rb') as f:
                public_key = f.read()
            with open(private_key_path, 'rb') as f:
                private_key = f.read()
            return public_key,private_key
        except:
            return False
    @staticmethod
    def load_rsa_private_key(private_key_path:str)-> Union[bool, bytes]:
        """
        载入RSA私钥
        :param private_key_path: 私钥存储路径
        :return: 私钥或False
        """
        try:
            with open(private_key_path, 'rb') as f:
                private_key = f.read()
            return private_key
        except:
            return False

    @staticmethod
    def sign_database(origin_data:str,private_key:bytes)->bytes:
        """
        为数据签名

        :param origin_data: 原始数据
        :param private_key: 私钥存储路径
        :return:签名后的结果
        """
        # 要签名的数据
        data = bytes(origin_data.encode("utf-8"))
        private_key = load_pem_private_key(private_key, password=None, backend=default_backend())

        # 使用私钥生成数字签名
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    @staticmethod
    def save_signature(signature:bytes,DB_name:str)->None:
        """
        保存签名到指定路径

        :param signature: 签名结果
        :param DB_name: 数据库名称
        :return:
        """
        # 打开文件以进行写入
        path = "Key/Sign" + DB_name + ".txt"
        with open(path, "wb") as file:
            # 将字节序列写入文件
            file.write(signature)

    @staticmethod
    def load_signature(path:str)-> bytes:
        """
        读取签名

        :param path: 签名文件路径
        :return: 读取签名的结果
        """
        signature = None
        try:
            # 打开文件以进行读取
            with open(path, "rb") as file:
                # 从文件中读取字节序列
                signature = file.read()
        except FileNotFoundError:
            return False
        return signature

    @staticmethod
    def verify_signature(signature:bytes,origin_data:str,public_key:bytes)->bool:
        """
        验证签名

        :param signature: 签名
        :param origin_data: 原始数据
        :param public_key: 公钥
        :return: 验证结果
        """

        # 要验证的数据
        data = bytes(origin_data.encode("utf-8"))
        public_key = public_key.encode('utf-8')
        public_key = load_pem_public_key(public_key, backend=default_backend())

        # 验证数字签名
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True

        except InvalidSignature:
            return False

    @staticmethod
    def hash(content:str)->bytes:
        """
        对数据进行hash

        :param content: 要hash的字符串
        :return: hash结果
        """
        # 使用SHA-256进行哈希
        sha256_hash = hashlib.sha256(content.encode()).digest()
        return sha256_hash

    @staticmethod
    def make_key(private_path:str)->bytes:
        private_key = CryptoControl.load_rsa_private_key(private_path)
        return CryptoControl.hash(str(private_key))

    @staticmethod
    def en_AES(plaintext:str, key:bytes)->str:
        """
        AES加密

        :param plaintext: 明文
        :param key: 密钥
        :return: 密文
        """
        # 生成 AES 密钥
        cipher = AES.new(key, AES.MODE_ECB)

        # 对明文进行填充并加密
        padded_plaintext = pad(plaintext.encode(), AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)

        # 对结果进行 Base64 编码
        encrypted_text = b64encode(ciphertext).decode()

        return encrypted_text

    @staticmethod
    def de_AES(encrypted_text:str, key:bytes)->str:
        """
        AES解密

        :param encrypted_text: 密文
        :param key: 密钥
        :return: 明文
        """
        # 生成 AES 密钥
        cipher = AES.new(key, AES.MODE_ECB)

        # 对密文进行解码和解密
        decoded_ciphertext = b64decode(encrypted_text)
        decrypted_data = cipher.decrypt(decoded_ciphertext)

        # 去除解密后的填充
        plaintext = unpad(decrypted_data, AES.block_size).decode()

        return plaintext


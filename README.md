# 密码管理器

## 一、基础配置

### 1 软件基础信息

> 目前版本：V0.9
>
> 存在问题：没有绑定父子元素。关闭主窗口后新开的窗口并不会关闭。建议在关闭父窗口后不要在子窗口进行数据增删改，防止出现BUG。



### 2 开发环境

> Python 3.10



### 3 使用包

```python
import json
import os
from typing import Union

import PyQt5

import Crypto
import base64
import cryptography
import hashlib
```



## 二、使用流程

### 1 注册

>在起始界面点击注册后就会进入注册界面。
>
>在注册界面输入数据库名称后就会生成5个文件（不输入默认名称是NewDatabase）
>
>（下列 `{}` 表示数据库名称）
>
>两个文件在Data文件夹下，分别是：数据库`{}.db`，配置文件`config.json`
>
>其他三个文件在Key文件夹下，分别是：公钥`{}Publickey.pem`，私钥`{}Privatekey.pem`，签名文件`Sign{}.txt`
>
>建议生成后将他们存入自定义的不同的文件夹下，使用时选定路径即可。其中私钥需要重点管理。



### 2 登录

>登录时选择数据库路径和签名所在路径后点击登录即可。
>
>验证通过将登录成功。验证不通过则可能是数据库损坏、数据库中（应用，账号，密码）数据被篡改、签名与数据库不对应。



### 3 增加数据

>登录成功后，点击左上角的加号即可添加数据。
>
>添加的数据中只有备注是可以为空，其他都不可以为空。
>
>首次登录进数据库并增加数据需要进行私钥验证。
>
>添加成功后即可看到添加的数据。



### 4 查询数据

>在搜索栏数据想搜索的数据点击搜索即可。
>
>未输入任何数据则会搜索出数据库中的全部数据。
>
>输入数据后会在数据库中进行数据搜索。规则是（ID，类别，应用名，账户，备注）任一属性中出现了类似数据的格式则会被显示。



### 5 修改数据

>双击数据可以进行修改。
>
>ID不可修改。
>
>应用名，账号，密码的修改需要验证一次私钥。
>
>密码修改还需要先对密码进行解密再进行修改。



### 6 删除数据

>双击删除按键进行删除。
>
>删除需要验证一次私钥。

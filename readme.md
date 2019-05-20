# UUIA SDK In Python3 

## 1.使用到的python第三方库
- Flask web框架

&#160; &#160; &#160; &#160;本SDK使用python的flask框架，对UUIA开源项目服务进行封装。

## 2.使用说明

&#160; &#160; &#160; &#160;clone 本项目，在本项目的app.py文件中实现获取数据的逻辑，即可完成UUIA子节点的开发。

### 1.导入UUIA到app.py

&#160; &#160; &#160; &#160;UUIA以Python包的形式存在于您的子节点项目中，其中主要功能实现于其中的Uuia类。

```Python3
from UUIA import Uuia
```

### 2.Uuia类实例化

&#160; &#160; &#160; &#160;在实现数据获取逻辑之前，您需要从UUIA包中导入Uuia类。并将其实例化，实例化时，需要传入UUIA配置信息。具体见下表：

| 配置名称 |类型| 必要性 | 含义 | 默认值 |
| --- | --- | --- | --- | --- |
| thread_name | | 必要 | flask项目监听的线程，一般都是直接传入__name__ | 无 |
| app_id | 字符串 | 必要 | 从UUIA中心服务器获取的app_id | 无 |
| app_token | 字符串 | 必要 | 从UUIA中心服务器获取的app_token | 无 |
| app_name | 字符串 | 非必要 | app项目的名称 | uuia |
| running_ip | 字符串 | 非必要 | 项目运行的网段 | 0.0.0.0 |
| running_port | 字符串 | 非必要 | 项目运行的端口 | 80 |
| running_domain | 字符串 | 非必要 | 项目运行的URL | /uuia |
| ssl_flag | 布尔 | 非必要 | 是否启用https加密 | False |
| ssl_crt | 字符串 | 非必要 | ssl证书.crt文件的路径，ssl_flag为True时必要，否则会抛出异常 | 无 |
| ssl_key | 字符串 | 非必要 | ssl证书的.key文件路径，ssl_flag为True时必要，否则会抛出异常| 无 |

示例代码：
```Python3
uuia = Uuia(
    thread_name=__name__,
    app_id="this_is_your_name",
    app_token="this_is_your_token",
    app_name="this_is_your_name",
    running_ip="127.0.0.1",
    running_port="443",
    running_domain="/uuia",
    ssl_flag=True,
    ssl_crt="this/is/the/path/to/crt_file",
    ssl_key="this/is/the/path/to/key_file"
)
```

### 3.注册动作（action）回调函数
&#160; &#160; &#160; &#160;正常情况下，服务器接收到的请求均为post请求，其post数据是json，且具有如下结构:
```json
{
    "uuid":"请求用户的唯一标识",
    "group":"请求用户的用户组",
    "action":"请求用户想要完成的动作",
    //......（其他完成该动作需要的参数）
}
```

&#160; &#160; &#160; &#160;服务器需要根据用户post来的action字段判断需要使用那个函数来完成对应的动作。此过程只需要您为action字段注册一个回调函数。** 注册绑定回调函数的方式是在被注册函数前面使用Uuia实例的bind_action_callback_function装饰器装饰包装。 **

&#160; &#160; &#160; &#160;注册回调装饰器需要传入以下两个必要参数：
| 参数名 | 参数类型 | 参数含义 | 参数示例 |
| --- | --- | --- | --- |
| groups | 列表 | 可以访问本回调函数的用户组 | groups=["base","user_group_1","user_group_2"] |
| actions | 列表 | 可以访问本回调函数的动作名 | actions=["action_1","action_2"] |

#### 3.1 回调函数传入参数
| 参数名 | 参数类型 | 参数含义 | 参数示例 |
| --- | --- | --- | --- |
| uuid | 字符串 | 请求用户的uuid | this_is_the_uuid_of_user |
|request_args | 字典 | post请求的请求参数 | {"uuid":"this_is_the_uuid_of_user","group":"base","action":"the_action_name","data":{}} |

#### 3.2 回调函数返回参数
&#160; &#160; &#160; &#160;回调函数的执行结果请以Python字典的格式返回给SDK，字典中需要有以下字段：
| 字段名 | 必要性 | 字段值类型 | 值的含义 | 示例 |
| --- | --- | --- | --- | --- |
| uuid | 必要 | 字符串 | 用户的uuid，如果返回值中没有此字段会抛出异常 | "this_is_the_uuid_of_user" |
| 其他 | 必要 | 不定 | 调用本动作的其他返回数据，根据接口实际情况而定 |  |

##### 3.3 示例代码
```Python3
@uuia.bind_action_callback_function(groups=["base","student"],actions=["action_1","action_2")
def get_data_callback(uuid,request_args):
    pass
    # TODO (UUIA) : 您需要在这里完成你获取数据的逻辑代码，并返回一个字典
```
&#160; &#160; &#160; &#160;上面示例代码的含义是当请求中的group字段是base或student且请求中的action字段是action_1或action_2时调用回调函数get_data_callback函数，并将Http请求的post参数和用户的uuid传入回调函数。

### 4. 基础接口的编写
&#160; &#160; &#160; &#160;基础接口的编写文档请参考 <a href="https://github.com/uuia/java-sdk#uuia-api-文档">UUIA Java SDK</a> 文档。值得注意的是，本SDK封装了http请求返回数据中的“code”字段和“message”字段，您的回调函数的结果将作为http请求数据中的“data”字段交给中心服务器。

### 5. 异常处理
&#160; &#160; &#160; &#160;SDK运行过程中可能会出现下面三种异常：
- Callback_exception ：用户请求的group和action无对应的回调函数处理
- Config_error_exception ：Uuia流泪实例化时的配置信息不合法
- Lack_necessary_info_exception ：用户请求Post data或者是回调函数返回值中缺少必要值

### 6.项目的启动
&#160; &#160; &#160; &#160;UUIA 项目完成后，调用uuia实例的run方法即可启动项目，run方法可以传入一个可选参数：

| 参数名称 | 必要性 | 参数类型 | 参数含义 | 默认值 |
| --- | --- | --- | --- |--- |
| flask_debug | 可选 | 布尔 | 是否开启flask框架的debug模式 | False |

&#160; &#160; &#160; &#160;开启flask_debug后，当代码发生修改后项目会自动重新装载，无需手动重启项目。

## 代码模板
```Python3
from UUIA import UUIA #导入Uuia类

#Uuia类实例化
uuia = Uuia(
    app_id="this_is_your_app_id",
    app_token="this_is_your_app_token",
    app_name="this_is_your_app_name",
    running_port=443, #运行端口
    running_ip="127.0.0.1", #运行ip
    thread_name=__name__, #监听线程
    running_domain="/uuia" #运行url
)

#使用uuia实例的bind_action_callback_funcion并传入groups和actions注册相应动作的回调函数
#基础功能1：获取需绑定账户的回调函数
@uuia.bind_action_callback_function(groups=["base"], actions=["bindType"])
def get_bind_types(uuid,request_args):
    pass
    # TODO :请在这里完成数据获取操作，并将结果以dict返回

#基础功能2：绑定账户的回调函数
@uuia.bind_action_callback_function(groups=["base"], actions=["bind"])
def bind_account(uuid,request_args):
    pass
    # TODO :请在这里完成数据获取操作，并将结果以dict返回
    
#基础功能3：获取用户成绩的回调函数
@uuia.bind_action_callback_function(groups=["base"], actions=["score"])
def get_score(uuid,request_args):
    pass
    # TODO :请在这里完成数据获取操作，并将结果以dict返回

#基础功能4：查询课表的回调函数
@uuia.bind_action_callback_function(groups=["base"], actions=["schedule"])
def get_schedule(uuid,request_args):
    pass
    # TODO :请在这里完成数据获取操作，并将结果以dict返回

#基础功能5：获取用户信息的回调函数
@uuia.bind_action_callback_function(groups=["base"], actions=["userInfo"])
def get_user_info(uuid,request_args):
    pass
    # TODO :请在这里完成数据获取操作，并将结果以dict返回
    
#基础功能6：获取用户一卡通信息的回调函数
@uuia.bind_action_callback_function(groups=["base"], actions=["eCard"])
def get_campus_card(uuid,request_args):
    pass
    # TODO :请在这里完成数据获取操作，并将结果以dict返回

#基础功能7：获取用户考试安排的回调函数
@uuia.bind_action_callback_function(groups=["base"], actions=["exam"])
def get_exams_arrangements(uuid,request_args):
    pass
    # TODO :请在这里完成数据获取操作，并将结果以dict返回

#如果您还有其他功能的回调函数，按照上面的格式，根据group和action注册实现功能的回调函数即可

if __name__ == '__main__':
    #调用uuia的run方法，启动项目，并开启flask_debug
    uuia.run(
        flask_debug=True
    )

```
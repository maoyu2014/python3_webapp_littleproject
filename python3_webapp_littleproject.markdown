# python3_webapp_littleproject

----------

这是用python3做的第一个小项目，根据liaoxuefeng的网站教程而来。

### 使用到的第三方库
aiomysql  
aiohttp  
jinja2  

### 项目内的文件结构关系
1. orm.py -> models.py，
**orm.py是我们基于aiomysql自己写的一个小ORM框架**
Model主要用来表示每一个实体，也就是User, Blog, Comment，创建了与数据库之间的关系。
利用orm框架，我们简化了对数据库的操作。
2. coroweb.py -> handlers.py，
**coroweb.py是我们基于aiohttp自己写的一个小web框架**
用来自动完成路由的设定、参数的获取、以及get和post的装饰器函数 等web功能。于是，所有的后续工作仅仅是简单的写一写handlers.py中的函数，让我们更加专注于业务。
3. app.py，
主要是启动服务，同时包括了将返回值转换成符合aiohttp格式的函数。
4. apis.py，
包含了我们人为定义的Error和一个用来分页使用的Page类
5. www/templates
该目录包含了所有的html页面，获取每个页面的url链接可以参看handlers.py文件。

### 重点
1. 第一个重点就是orm.py框架的编写。ORM 主要负责的是数据库方面的操作，可以方便的让python对象实现数据库的增删改查操作 该模块封装了aiomysql库
2. 第二个重点就是coroweb.py框架的编写。Web框架 主要负责的是接受http请求和处理请求并返回结果，有了该框架，开发者便可以在handlers.py中专注于业务实现。该模块封装了aiohttp库
3. 第三个也不能算重点，就是一个各种url的处理关系。我用笔纸整理出来一个图（有点丑），贴上将就看看吧。![url-relation](https://github.com/maoyu2014/python3_webapp_littleproject/blob/day-15/%E9%A1%B5%E9%9D%A2%E8%B0%83%E7%94%A8%E5%85%B3%E7%B3%BB%E5%9B%BE.jpg)
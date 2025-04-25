# 水域检测平台设计与实现

## 简介

本系统实现了一个水域检测平台，有文件管理模块、用户模块、文件分享模块、图像检测模块、在线检测模块。

本系统需要部署4个服务

1. 前端服务：使用Vue3+Element-Plus开发
2. 后端服务-业务：使用Django开发，需要有足够的存储空间
3. 后端服务-目标检测：使用Flask，检测模型为YOLO，需要部署于GPU服务器
4. nginx服务：用于接收推流

后端的配置文件抹除了部分敏感信息

[架构相关的图和模块流程图](https://gcnre8ma7k2f.feishu.cn/wiki/Rz4XwB6wbiK81Ok85CAcqkNxnWg)



## 开发环境版本

| 软件    | 版本   |
| ------- | ------ |
| node.js | 20.9.0 |
| python  | 3.10   |
| redis | 7.0.15|
| mysql | 8.0.41 |
| rabbitMQ| 4.0.7 |
|nginx| 1.26.3 |
|nginx-rtmp-module| 1.26 |
|ffmpeg| 7.1.1 |

python具体依赖包版本见requirements.txt

vue依赖见package.json



## 部署

water-detect-backend的运行环境为amdGPU，如果使用Nvidia，可能需要修改ffmpeg的解码器h264_amf为其他值

- 创建数据库db.sql（django的manager.py migrate不确定能不能用）
- 部署redis
- 部署rabbitMQ

    - 一个名为yolo-analyse的Queue

    - amq.direct给routingKey=analyse绑定yolo-analyse
- 搞个邮箱SMTP授权
- 修改配置water-detect-backend/waterDetect/settings.py
- 部署前后端主服务
- 目标检测
    - 如果目标检测与主后端服务不在同一台机器上：部署目标检测服务（配置调用IP）
    - 如果在后端服务跑YOLO：修改`water-detect-backend/yolo/yolo_model/analyse.py` USE_REMOTE=False
    - 如果不想实际调用YOLO，只是想有一个图像处理的转换，将USE_MOCK=True（将图像处理成灰度图，不确定是否可用）
- 在线检测
    - 修改nginx.conf rtmp下的http连接，部署nginx服务



## 项目预览

submitAttachment
|  media 		  **用于存储文件(该文件夹下应该有analyse_tmp, avatar, cuts, files, hls, thumbnail, tmp)**
│  nginx.conf		nginx配置文件
│  README.md		项目说明文件
│  
├─water-detect-backend	业务系统
│  │  manage.py		django项目管理脚本
│  │  requirements.txt	django项目依赖配置
│  │  
│  ├─account			用户模块
│  │          
│  ├─common			通用工具包，不依赖django包的工具
│  │          
│  ├─common_service		外部服务，redis，文件存储等
│  │          
│  ├─database		数据库，集成与数据库交互的逻辑
│  │          
│  ├─directory		文件系统模块，文件上传、管理等操作
│  │  ├─service		对接RabbitMQ
│  │          
│  ├─online_stream		在线检测模块，对接nginx回调与Web获取直播流
│  │          
│  ├─self_test		测试模块，临时测试使用
│  │          
│  ├─share_file		文件分享模块
│  │          
│  ├─waterDetect		项目配置
│  │          
│  └─yolo			文件检测消费
│      ├─yolo_model		对接目标检测模块
│              
├─water-detect-front		前端项目
│  └─src
│      │  App.vue
│      │  main.js
│      │  
│      ├─api			Ajax，HTTP请求实例
│      │      
│      ├─assets		图片，css资源
│      │              
│      ├─components		Vue组件
│      │          
│      ├─constants		定义常数
│      │      
│      ├─plugins		插件
│      │      
│      ├─router		定义路由器
│      │      
│      ├─utils		工具包
│      │      
│      └─views		视图
│          │  BaseHomePage.vue	
│          │  
│          ├─common		登录视图
│          │      
│          ├─models		登录后的各种视图
│          │      
│          └─share		文件分享模块视图
│                  
└─yolo-service		目标检测系统
    ├─detect-model		检测模型训练相关代码
    │      
    └─service-module		目标检测系统代码
        │  app.py		flask初始化提供接口
        │  requirements.txt	项目依赖
        │  
        └─service		对接YOLO模型，进行检测.py
            │  
            └─model		YOLO模型
                    
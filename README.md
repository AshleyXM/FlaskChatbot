# **[Demo-Video-Click-Here](https://youtu.be/J2aGm--ks6M)**

- 演示视频已上传到YouTube，国内需要用VPN来观看



# **Demo-Gif**

![demo-1.gif](https://github.com/AshleyXM/FlaskChatbot/blob/master/img/demo-1.gif)

![demo-2.gif](https://github.com/AshleyXM/FlaskChatbot/blob/master/img/demo-2.gif)



# **说明**

- 本项目实现的是以问询形式为基础的金融机器人，可以向机器人询问在某一时间段内某几种股票的OHLC价格以及成交量(Volume)，基于Rasa和NLTK来实现的。
- 该项目可以查询所有在NASDAQ Stock Exchange上市的股票。
- 会话管理使用的是rasa-nlu，rasa的pipeline配置如下：

```python
language: "en"

pipeline: "spacy_sklearn"
```

- Rasa训练数据集的构造：使用了[Chatito工具](https://rodrigopivi.github.io/Chatito/)



# **配置环境（python==3.6.2）**

1. 下载zip包或者git clone

2. 进入FlaskChatbot目录，打开Anaconda Prompt，激活环境

3. 在命令行中输入：

   ```python
   pip install -r requirements.txt
   ```

4. 确保NLTK已下载以下数据包（可以新建一个.py文件执行以下代码）：

   ```python
   nltk.download('punkt')
   nltk.download('averaged_perceptron_tagger')
   nltk.download('maxent_ne_chunker')
   nltk.download('words')
   nltk.download('treebank')
   ```

5. 友情提示：

- 建议使用国内镜像源安装第三方库，比如Tsinghua,USTC和Douban的都不错！

  ```
  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  或
  pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ -r requirements.txt
  或
  pip install -i http://pypi.douban.com/simple/ -r requirements.txt
  ```

- ​	当然，如果你会使用VPN上网，那么只需要开启你的全局代理即可。如下使用：

  ```python
  pip install 第三方库名 --proxy=地址:端口
  ```

6. 按照[nginx教程](https://www.cnblogs.com/jiangwangxiang/p/8481661.html)安装好nginx，并配置好nginx.conf文件，如果有租用的云服务器可以配置自己的云服务器的IP地址，如果没有可以把自己的电脑当做服务器，可以实现局域网上的访问。



# **爬取数据**

- 运用了scrapy库来爬取[EODDATA官网](http://www.eoddata.com/)上的所有NASDAQ股票，并将爬取的股票名和股票代码存储到数据库，以便实现之后的查询任务。
- 若想运行scrapy来爬取数据，可以运行项目scrapy_dir/scrapy_dir/spiders目录下的[stocks_spider.py](https://github.com/AshleyXM/FlaskChatbot/blob/master/scrapy_dir/scrapy_dir/spiders/stocks_spider.py)文件



# **运行bot**

1. 将克隆的项目用Pycharm打开，在Terminal中输入：

   ```
   python tornado_server.py
   ```

   

2. 启动这个项目需要一点时间，因为训练数据需要一定的时间来完成

3. 接下来，打开浏览器，输入自己配置的服务器IP地址就可以访问项目的主页了

# **参考**

[yfinance官方文档](https://pypi.org/project/yfinance/)

Yahoo Finance API[参考文档](https://aroussi.com/post/python-yahoo-finance)

[nginx安装配置教程](https://www.cnblogs.com/jiangwangxiang/p/8481661.html)

[eoddata数据](http://eoddata.com/stocklist/NASDAQ/A.htm)

[Scrapy 1.7教程](https://www.osgeo.cn/scrapy/intro/tutorial.html)

[前端界面参考](https://blog.csdn.net/weixin_41606022/article/details/100867167)

[Flask如何部署网页](https://www.jianshu.com/p/c8b321087eca)

# 域名扫描工具
###  <p><b><a href="README.md">English</a></b></p>
一个高效的多线程域名注册扫描工具，基于SOA记录。它可以用于高速查找有趣的域名组合。

其功能包括：

- 简单易用的界面；
- 快速的扫描速度；
- 支持IPv4和IPv6；
- 理论上支持所有后缀，包括二级及更高级别的后缀；
- 支持同时扫描多个后缀；
- 仅依赖Python内置库。

使用该工具，只需运行：

```bash
git clone https://github.com/loveoranges/DomainScanTool.git
cd DomainScanTool
python DomainScanTool.py 8.8.8.8 com dictionary.txt results.txt y
```
或者 
```bash
python DomainScanTool.py "8.8.8.8:53,8.8.4.4:53" "com,net" dictionary.txt results.txt y
```

已知限制：

- 无法区分保留域名，因为该工具依赖于DNS系统。
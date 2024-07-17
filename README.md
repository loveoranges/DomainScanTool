# Domain Scanning Tool
###  <p><b><a href="README_CN.md">简体中文</a></b></p>
An efficient multithreaded domain registration scanning tool. based on SOA record. It can be used to find nice domain hacks at high speed.

Its features include:

- Easy to use interface;
- Fast scanning speed;
- Supporting both IPv4 and IPv6
- (Theoretically) supporting all suffixes including secondary ones and even higher levels;
- Supporting scanning multiple suffixes at once;
- Only relying on Python built-in libraries.



To use this tool, simple run:

```bash
git clone https://github.com/loveoranges/DomainScanTool.git
cd DomainScanTool
python DomainScanTool.py 8.8.8.8 com dictionary.txt results.txt y
```
or 
```bash
python DomainScanTool.py "8.8.8.8:53,8.8.4.4:53" "com,net" dictionary.txt results.txt y
```






Known limitations:

- Can't distinguish reserved domains, as this tool relies on DNS system.

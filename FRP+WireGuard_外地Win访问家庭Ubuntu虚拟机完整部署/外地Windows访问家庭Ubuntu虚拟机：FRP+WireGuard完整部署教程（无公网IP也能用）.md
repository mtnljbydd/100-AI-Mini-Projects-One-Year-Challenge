# 外地 Windows 访问家庭 Ubuntu 虚拟机：FRP+WireGuard 完整部署教程（无公网 IP 也能用）

## 前言

日常远程办公、外出场景下，我需要从外地的 Windows 电脑访问家庭内网中的 Ubuntu 虚拟机（用于代码调试、文件访问、内网服务使用等）。由于家庭宽带无公网 IP，直接访问存在技术障碍，最终选择「FRP+WireGuard」方案 —— 通过云服务器作为公网中转节点，实现外地设备与家庭虚拟机的安全加密连接，整个链路稳定且无需依赖家庭公网 IP。

本文详细记录完整部署流程，包括云服务器配置、家庭虚拟机环境搭建、外地 Windows 客户端连接，以及部署过程中遇到的问题及解决方案，所有命令和配置均可直接复制使用。

## 一、方案架构

核心逻辑：通过 FRP（反向代理）打通公网中转通道，WireGuard（VPN）实现加密通信，解决两个内网（外地 Windows 所在网络、家庭内网）无法直接连通的问题。



```
外地Windows（WireGuard客户端） → 云服务器（FRP服务端+端口转发） → 家庭Ubuntu虚拟机（FRP客户端+WireGuard服务器）
```



* 云服务器：作为公网中转节点，转发 FRP 和 WireGuard 流量；

* FRP：实现内网穿透，让家庭虚拟机通过云服务器端口暴露在公网；

* WireGuard：建立加密 VPN 隧道，确保数据传输安全。

## 二、准备工作

### 1. 软硬件环境清单



| 设备 / 环境 | 配置详情                                                |
| ------- | --------------------------------------------------- |
| 云服务器    | 操作系统：Ubuntu/CentOS，公网 IP：123.45.67.89（示例 IP）        |
| 家庭虚拟机   | 操作系统：Ubuntu，局域网 IP：192.168.92.128，已部署 WireGuard 服务器 |
| 外地设备    | 操作系统：Windows 10/11，已安装 WireGuard 客户端                |
| 核心工具    | FRP（v0.54.0）、WireGuard（最新版）                         |

### 2. 云服务器端口开放（关键！）

登录云服务器控制台（阿里云 / 腾讯云 / 华为云），在安全组 / 防火墙中开放以下入方向端口：



| 协议  | 端口号   | 用途说明                 | 授权对象      |
| --- | ----- | -------------------- | --------- |
| TCP | 22    | 云服务器 SSH 管理端口（默认已开放） | 0.0.0.0/0 |
| TCP | 7000  | FRP 服务端核心端口（客户端连接）   | 0.0.0.0/0 |
| UDP | 51820 | WireGuard VPN 流量转发端口 | 0.0.0.0/0 |
| TCP | 6000  | 可选：虚拟机 SSH 转发备用端口    | 0.0.0.0/0 |

> 注：授权对象
>
> `0.0.0.0/0`
>
> 表示允许所有 IP 访问，若需限制仅外地 Windows 所在 IP，可修改为具体 IP 地址。

## 三、分步部署

### 阶段 1：云服务器部署 FRP 服务端

FRP 服务端运行在云服务器，负责接收家庭虚拟机 FRP 客户端的连接并转发流量。

#### 步骤 1：下载 FRP 服务端

登录云服务器（通过 SSH 工具，如 Xshell、Windows 终端）：



```
登录云服务器（替换为你的云服务器IP）

ssh root@123.45.67.89

下载FRP v0.54.0 Linux-amd64版本（与客户端版本一致）

wget https://github.com/fatedier/frp/releases/download/v0.54.0/frp\_0.54.0\_linux\_amd64.tar.gz

解压压缩包

tar -zxvf frp\_0.54.0\_linux\_amd64.tar.gz

cd frp\_0.54.0\_linux\_amd64
```

#### 步骤 2：配置 FRP 服务端（frps.ini）

##### ① 纯配置文本（可直接复制粘贴）



```
\[common]

FRP服务端监听端口（TCP）

bind\_port = 7000

连接密钥（需与家庭虚拟机FRP客户端一致）

token = 123456

日志配置（方便排查问题）

log\_level = info

log\_file = ./frps.log

允许转发的端口范围

allow\_ports = 51820,6000
```

##### ② 终端一键执行命令（直接复制创建配置文件）



```
备份默认配置，创建新的frps.ini

mv frps.ini frps.ini.bak

cat > frps.ini \<common]

FRP服务端监听端口（TCP）

bind\_port = 7000

连接密钥（需与家庭虚拟机FRP客户端一致）

token = 123456

日志配置（方便排查问题）

log\_level = info

log\_file = ./frps.log

允许转发的端口范围

allow\_ports = 51820,6000

EOF
```

保存退出验证：执行`cat frps.ini`，确认配置与上述一致。

#### 步骤 3：启动 FRP 服务端并设置自启



```
后台启动FRP服务端

nohup ./frps -c frps.ini &

验证启动状态（有输出即为运行成功）

ps -ef | grep frps | grep -v grep

设置开机自启（避免云服务器重启后失效）

cat > /etc/systemd/system/frps.service << EOF

\[Unit]

Description=FRP Server Service

After=network.target

\[Service]

Type=simple

User=root

WorkingDirectory=/root/frp\_0.54.0\_linux\_amd64

ExecStart=/root/frp\_0.54.0\_linux\_amd64/frps -c /root/frp\_0.54.0\_linux\_amd64/frps.ini

Restart=always

RestartSec=5

\[Install]

WantedBy=multi-user.target

EOF

启用并启动自启服务

sudo systemctl daemon-reload

sudo systemctl enable frps

sudo systemctl start frps

查看服务状态（显示active(running)即为成功）

sudo systemctl status frps
```

### 阶段 2：家庭 Ubuntu 虚拟机配置（FRP 客户端 + WireGuard 服务器）

家庭虚拟机已提前部署 WireGuard 服务器，此处重点配置 FRP 客户端，实现与云服务器的连接。

#### 步骤 1：下载 FRP 客户端（解决 GitHub 下载慢问题）



```
进入桌面目录（方便操作）

cd \~/Desktop

原始GitHub下载（带断点续传，中断后重新执行即可续传）

wget -c https://github.com/fatedier/frp/releases/download/v0.54.0/frp\_0.54.0\_linux\_amd64.tar.gz

解压压缩包

tar -zxvf frp\_0.54.0\_linux\_amd64.tar.gz

cd frp\_0.54.0\_linux\_amd64
```

> 若终端下载失败（如网络限制），直接用 Ubuntu 浏览器打开下载链接：
>
> `https://ghproxy.com/https://github.com/fatedier/frp/releases/download/v0.54.0/frp_0.54.0_linux_amd64.tar.gz`
>
> ，下载后拖到桌面并解压。

#### 步骤 2：配置 FRP 客户端（frpc.ini）

##### ① 纯配置文本（可直接复制粘贴）



```
\[common]

server\_addr = 123.45.67.89  # 云服务器示例IP

server\_port = 7000          # 与FRP服务端bind\_port一致

token = 123456              # 与FRP服务端token一致

WireGuard UDP端口转发（核心）

\[wireguard\_vpn]

type = udp

local\_ip = 127.0.0.1

local\_port = 51820          # 家庭虚拟机WireGuard监听端口

remote\_port = 51820         # 云服务器暴露的UDP转发端口

可选：SSH端口转发（无需VPN直接访问虚拟机）

\[ssh\_vm]

type = tcp

local\_ip = 127.0.0.1

local\_port = 22             # 虚拟机SSH端口

remote\_port = 6000          # 云服务器暴露的SSH转发端口
```

##### ② 终端一键执行命令（直接复制创建配置文件）



```
直接创建配置文件（避免手动编辑保存失败）

cat > frpc.ini <\[common]

server\_addr = 123.45.67.89

server\_port = 7000

token = 123456

\[wireguard\_vpn]

type = udp

local\_ip = 127.0.0.1

local\_port = 51820

remote\_port = 51820

\[ssh\_vm]

type = tcp

local\_ip = 127.0.0.1

local\_port = 22

remote\_port = 6000

EOF
```

#### 步骤 3：启动 FRP 客户端并后台运行



```
给FRP客户端添加执行权限

chmod +x frpc

前台启动测试（确认无错误）

./frpc -c frpc.ini
```

启动成功标志（终端输出）：



```
WARNING: ini format is deprecated...

2026/01/06 xx:xx:xx \[I] \[service.go:329] \[xxxxxx] login to server success

2026/01/06 xx:xx:xx \[I] \[proxy\_manager.go:144] \[xxxxxx] proxy \[wireguard\_vpn] start success

2026/01/06 xx:xx:xx \[I] \[proxy\_manager.go:144] \[xxxxxx] proxy \[ssh\_vm] start success
```

将客户端放到后台持久运行：



```
按Ctrl+Z暂停前台进程

后台运行并脱离终端

bg && disown

验证进程状态（有输出即为成功）

ps -ef | grep frpc | grep -v grep
```

### 阶段 3：外地 Windows 配置 WireGuard 客户端

WireGuard 客户端负责建立与家庭虚拟机 WireGuard 服务器的加密连接，实现外地访问。

#### 步骤 1：安装 WireGuard 客户端

下载 Windows 版 WireGuard 客户端：[WireGuard 官方下载](https://www.wireguard.com/install/)，双击安装即可。

#### 步骤 2：配置 WireGuard 连接

##### ① 纯配置文本（可直接复制粘贴到 WireGuard 客户端）



```
\[Interface]

PrivateKey = KNZDTqsznBSFZxGKMkNP9aiKIrUYeDPPZeRhhAh/Kms=  # Windows客户端私钥

Address = 10.0.0.2/32  # 客户端虚拟IP（与虚拟机WireGuard网段一致）

DNS = 223.5.5.5  # 国内DNS，避免解析失败

\[Peer]

PublicKey = H2UihMljoEM86xZUgVvKkCQbCQOMTSPLzwOpIrdbT2E=  # 家庭虚拟机WireGuard公钥

Endpoint = 123.45.67.89:51820  # 云服务器示例IP:WireGuard转发端口

AllowedIPs = 192.168.92.0/24, 10.0.0.0/24  # 仅访问家庭内网，不影响外地网络

PersistentKeepalive = 25  # 保持连接，避免超时断开
```

##### ② 配置操作步骤



1. 打开 WireGuard 客户端，点击「Add Tunnel」；

2. 将上述配置文本粘贴到弹出的编辑框中；

3. 点击「Save」保存配置。

## 四、测试连接（最终验证）

### 1. 启动 WireGuard 连接

在外地 Windows 的 WireGuard 客户端，点击配置右侧的「Activate」，状态变为绿色「Active」，说明 VPN 连接成功。

### 2. 测试网络连通性（终端可直接复制命令）



```
测试1：Ping家庭虚拟机局域网IP（验证网络打通）

ping 192.168.92.128

测试2：SSH登录家庭虚拟机（输入虚拟机用户名和密码）

ssh user@192.168.92.128

备用测试：无需VPN，通过FRP转发SSH登录

ssh user@123.45.67.89 -p 6000
```



* 若 Ping 命令显示「丢包率 0%」，SSH 能成功登录，说明整个链路完全打通。

## 五、常见问题排查（部署踩坑记录）

### 1. 云服务器 FRP 服务端启动失败（Exit 1）



* 错误日志：`invalid log level`

* 原因：`frps.ini`中`log_level`配置错误（需小写，如`info`，不可大写或拼写错误）

* 解决方案（终端一键执行）：



```
重新创建正确的frps.ini

cat > frps.ini \<common]

bind\_port = 7000

token = 123456

allow\_ports = 51820,6000

EOF

重启FRP服务端

pkill -9 frps && nohup ./frps -c frps.ini &
```

### 2. 家庭虚拟机 FRP 客户端提示「i/o timeout」



* 原因：云服务器 7000 端口不可达（FRP 服务端未运行或本地防火墙拦截）

* 解决方案（云服务器终端执行）：



```
重启FRP服务端

pkill -9 frps && nohup ./frps -c frps.ini &

关闭云服务器本地防火墙

sudo ufw disable

验证7000端口监听

netstat -tulpn | grep 7000
```

### 3. FRP 客户端提示「open frpc.ini: no such file or directory」



* 原因：当前目录下无`frpc.ini`配置文件（手动编辑未保存或路径错误）

* 解决方案（家庭虚拟机终端执行）：



```
cd \~/Desktop/frp\_0.54.0\_linux\_amd64

cat > frpc.ini << EOF

\[common]

server\_addr = 123.45.67.89

server\_port = 7000

token = 123456

\[wireguard\_vpn]

type = udp

local\_ip = 127.0.0.1

local\_port = 51820

remote\_port = 51820

\[ssh\_vm]

type = tcp

local\_ip = 127.0.0.1

local\_port = 22

remote\_port = 6000

EOF
```

### 4. Windows WireGuard 显示 Active 但 Ping 不通虚拟机



* 原因：家庭虚拟机 IP 转发未开启

* 解决方案（家庭虚拟机终端执行）：



```
sudo sysctl -w net.ipv4.ip\_forward=1

sudo wg-quick down wg0 && sudo wg-quick up wg0
```

### 5. GitHub 下载 FRP 速度慢或失败



* 解决方案（家庭虚拟机终端执行）：



```
国内镜像加速下载

curl -o frp\_0.54.0\_linux\_amd64.tar.gz https://ghproxy.com/https://github.com/fatedier/frp/releases/download/v0.54.0/frp\_0.54.0\_linux\_amd64.tar.gz

解压

tar -zxvf frp\_0.54.0\_linux\_amd64.tar.gz
```

## 六、资源领取与矩阵账号

本文涉及的所有软件（FRP v0.54.0、WireGuard 最新版）已全部收集完毕，无需复杂查找，**欢迎关注微信公众号【从 0 至 1】领取**，回复「FRP-WireGuard」即可获取打包好的安装包及配置模板。

### 我的内容矩阵（持续分享技术干货）



* 抖音：从 0 至 1（视频教程 + 问题排查直播）

* 微信公众号：从 0 至 1（图文教程 + 资源打包）

* 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（完整技术文档 + 案例拆解）

* GitHub：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源配置脚本 + 工具集合）

关注后可获取更多内网穿透、远程办公、服务器部署相关技术干货，如有具体问题也可通过矩阵账号留言交流～

## 七、总结

### 关键点回顾



1. 核心链路：外地 Windows → 云服务器（123.45.67.89）→ 家庭 Ubuntu 虚拟机，通过 FRP 转发 + WireGuard 加密实现安全访问；

2. 配置核心：FRP 服务端 / 客户端的`token`和端口需一致，WireGuard 的`Endpoint`指向云服务器转发端口；

3. 便捷使用：所有配置均提供「纯文本复制版」和「终端一键执行版」，无需手动逐行编辑。

### 日常使用流程



1. 云服务器 FRP 服务端已配置开机自启，无需手动操作；

2. 家庭虚拟机启动 FRP 客户端：`cd ~/Desktop/frp_0.54.0_linux_amd64 && ./frpc -c frpc.ini &`；

3. 外地 Windows 打开 WireGuard 客户端，点击「Activate」即可访问家庭虚拟机。

本方案无需家庭公网 IP，适配绝大多数家庭宽带环境，且数据传输全程加密，兼顾便捷性与安全性，可满足远程访问家庭内网设备的各类需求。

## 个人矩阵

> - 抖音账号：从 0 至 1（日常分享Python自动化实操、效率工具教程）
> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新Python实战教程、技术干货内容）
> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
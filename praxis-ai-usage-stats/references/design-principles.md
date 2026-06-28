# Design Principles

## 一份代码，多处部署
脚本平台无关，各 runtime 安装后均可使用。新增 runtime 只需在 `usage_stats.py` 中添加一个 `parse_<runtime>()` 函数。

## 本地只读
只扫描日志，不修改原始文件，不联网。

## 隐私优先
context 截断 60 字符，不输出完整 prompt 或工具参数。不采集或输出 API token 原文/后缀；如需区分账号，使用 provider/account label 或不可逆 fingerprint。

## 可扩展
新 runtime 加入时，在 `usage_stats.py` 中添加对应的 `parse_<runtime>()` 函数即可。

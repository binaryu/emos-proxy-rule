> emos 反代域名列表，推荐设置为直连。每天自动更新。

来源：[https://wiki.emos.best/proxy.html](https://wiki.emos.best/proxy.html)

## 规则链接

- **Loon**: `https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-loon.list`
- **Surge**: `https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-surge.list`
- **Shadowrocket**: `https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-shadowrocket.list`
- **Quantumult X**: `https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-quantumultx.list`
- **Mihomo rule-provider**: `https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-mihomo.yaml`
- **Mihomo rule-provider (mrs)**: `https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-mihomo.mrs`
- **Sing-box rule-set**: `https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-sing-box.json`

## 使用方法

<details>
<summary>Loon</summary>

```ini
[Rule]
https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-loon.list, DIRECT
```

</details>

<details>
<summary>Surge</summary>

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-surge.list,DIRECT
```

</details>

<details>
<summary>Shadowrocket</summary>

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-shadowrocket.list,DIRECT
```

</details>

<details>
<summary>Quantumult X</summary>

```ini
[filter_remote]
https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-quantumultx.list, tag=emos-proxy, enabled=true
```

</details>

<details>
<summary>Mihomo（rules）</summary>

把 `https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-mihomo.list` 的内容直接放进 `rules:` 段（该文件每条规则已带 `DIRECT`）。

</details>

<details>
<summary>Mihomo（rule-provider，推荐）</summary>

```yaml
rule-providers:
  emos_proxy:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-mihomo.yaml
    path: ./ruleset/emos-mihomo.yaml
    interval: 86400

#或者用mrs
  emos_proxy:
    type: http
    behavior: domain
    format: mrs
    url: https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-mihomo.mrs
    path: ./ruleset/emos-mihomo.mrs
    interval: 86400

rules:
  - RULE-SET,emos_proxy,DIRECT
```

如果不生效，可能是dns污染导致，可以修改一下dns配置，示例：

```yaml
dns:
  enable: true
  nameserver-policy:
    "rule-set:emos_proxy":
      - https://dns.alidns.com/dns-query
      - https://doh.pub/dns-query
```

</details>

<details>
<summary>Sing-box</summary>

```json
{
  "route": {
    "rule_set": [
      {
        "type": "remote",
        "tag": "emos_proxy",
        "format": "source",
        "url": "https://raw.githubusercontent.com/binaryu/emos-proxy-rule/main/rules/emos-sing-box.json",
        "download_detour": "direct"
      }
    ],
    "rules": [
      {
        "rule_set": [
          "emos_proxy"
        ],
        "outbound": "direct"
      }
    ]
  }
}
```

</details>

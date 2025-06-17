# 企业查询MCP
一站式解锁企业大数据全维度洞察！精准查询市场主体数据、工商照面详情，深挖股东与对外投资脉络，精准定位疑似实控人及受益所有人。一键扫描企业风险，量化科创实力，荣誉资质、资质证书尽在掌握，还能依企业或人名秒寻关联企业信息，为企业决策、合作把关，赋能商业每一步.

企业查询MCP,分Streamable-http版、SSE版和STDIO版
- Streamable-http版：部署于云端 https://data.shuidi.cn/mcp
- SSE版：部署于云端 https://mcp.shuidi.cn/sse
- STDIO版：部署于本地, 该版本无query_company_data功能
 
## 工具
- `query_company_data`:根据自然语言问题回答与企业主体相关的统计问题，并且可以根据要求可视化展示为地图、折线图、柱状图、饼图等
  - 参数:
      - `question` (string): 问题描述，例如：例如统计全国各省2024年成立的企业，并以地图可视化展示 
  
- `search_established_companies`:查询并统计某时间段成立的企业
  - 参数:
      - `province` (string): 省份,例如上海,新疆,江苏,为None时表示查询全国的企业。
      - `city` (string): 城市,地级市，例如杭州，苏州。
      - `district` (string): 区县,区县名称需完整,包含市、县、区,例如昆山市，浦东新区。
      - `establish_date` (string) : 成立期限，格式如yyyy-mm-dd@yyyy-mm-dd,
                                             2023-01-12@表示2023年1月12号及之后成立的企业, 
                                             @2023-11-11表示23年11月11日之前成立的公司, 
                                             为None时表示任意时间成立的企业。
    
- `search_established_selfemployed`:查询并统计某时间段成立的个体户
  - 参数:
     - `province` (string): 省份,例如上海,新疆,江苏,为None时表示查询全国的企业。
      - `city` (string): 城市,地级市，例如杭州，苏州。
      - `district` (string): 区县,区县名称需完整,包含市、县、区,例如昆山市，浦东新区。
      - `establish_date` (string) : 成立期限，格式如yyyy-mm-dd@yyyy-mm-dd,
                                             2023-01-12@表示2023年1月12号及之后成立的企业, 
                                             @2023-11-11表示23年11月11日之前成立的公司, 
                                             为None时表示任意时间成立的企业。
    
- `search_companies`:根据地区及企业状态查询并统计企业
  - 参数:
      - `province` (string): 省份,例如上海,新疆,江苏,为None时表示查询全国的企业。
      - `city` (string): 城市,地级市，例如杭州，苏州。
      - `district` (string): 区县,区县名称需完整,包含市、县、区,例如昆山市，浦东新区。
      - `company_status` (string) : 企业状态可以设为"正常"、"异常"、"在营"、"存续"、"在业"、"吊销"、"注销"、"迁入"、"迁出"、"撤销"、"清算"、"停业"、"其他",
                                    企业状态正常，包括了在营、存续、在业、迁入、迁出的企业,
                                    企业状态异常，包括了吊销、注销企业。
    
- `search_selfemployed`:根据地区及企业状态查询并统计个体户
  - 参数:
      - `province` (string): 省份,例如上海,新疆,江苏,为None时表示查询全国的企业。
      - `city` (string): 城市,地级市，例如杭州，苏州。
      - `district` (string): 区县,区县名称需完整,包含市、县、区,例如昆山市，浦东新区。
      - `company_status` (string) : 企业状态可以设为"正常"、"异常"、"在营"、"存续"、"在业"、"吊销"、"注销"、"迁入"、"迁出"、"撤销"、"清算"、"停业"、"其他",
                                    企业状态正常，包括了在营、存续、在业、迁入、迁出的企业,
                                    企业状态异常，包括了吊销、注销企业。
    
- `get_company_info`:查询企业基本信息（照面信息）
  - 参数:
      - `company_name` (string): 企业名称
    
- `get_company_partner`:查询企业股东信息
  - 参数:
      - `company_name` (string): 企业名称
    
- `get_stie_score`:评估企业科创能力
  - 参数:
      - `company_name` (string): 企业名称
    
- `search_company_risk`:查询企业风险信息，包括企业自身风险、周边风险、预警信息等
  - 参数:
      - `company_name` (string): 企业名称
    
- `get_company_honor`:查询企业荣誉
  - 参数:
      - `company_name` (string): 企业名称
    
- `get_company_contact`:查询企业联系方式
  - 参数:
      - `company_name` (string): 企业名称
    
- `get_company_investment`:查询企业对外投资信息
  - 参数:
      - `company_name` (string): 企业名称
    
- `get_company_cert`:查询企业资质证书
  - 参数:
      - `company_name` (string): 企业名称
    
- `get_person_related_company`:根据企业名称和人名查询企业人员的关联企业,包括其担任法人、股东、董监高的公司
  - 参数:
      - `company_name` (string): 企业名称
      - `person_name` (string): 人名
    
- `get_company_controller`:查询企业实控人
  - 参数:
      - `company_name` (string): 企业名称
    
- `get_company_benificalowner`:查询企业受益所有人
  - 参数:
      - `company_name` (string): 企业名称
    
## 可适配平台
cursor

## 安装部署
[请在此处提供详细的安装和部署说明，根据您的产品特性选择合适的描述方式。]
### Streamable-http版安装部署
- 在cursor setting中打开"Tools & Integrations"窗口(cursor v1.*以上版本支持)
- 单击 "New MCP Server"按钮，编辑mcp.json
- 在cursor中配置
```json
 "DataMcpServer":{
   "url": "https://data.shuidi.cn/mcp"  
 },
```

### SSE版安装部署
- 在cursor setting中打开MCP窗口
- 单击 "Add new global MCP Server"按钮，编辑mcp.json
- 在cursor中配置
```json
 "DataMcpServer":{
   "url": "https://mcp.shuidi.cn/sse"  
 },
```
### STDIO版安装部署

- 使用 uv
  - 使用 [`uv`](https://docs.astral.sh/uv/) 时无需特定安装. 我们将直接运行 uv src/mcp_server.py.

- 在cursor setting中打开MCP窗口
- 单击 "Add new global MCP Server"按钮，编辑mcp.json
- 在cursor中配置
```json
 "DataMcpServer":{
    "command": "uv",
      "args": [
        "--directory",
        "{workdir}",
        "run",
        "src/mcp_server.py"
      ],
      "env": {
        "shuidi_pname": "--在shuidi官网申请的pname--",
        "shuidi_pkey": "--在shuidi官网申请的pkey--"
      }
 },
``` 
### 说明
- workdir为工作目录
- shuidi_pname shuidi_pkey需到shuidi官网申请，目前可使用免费测试帐号
  - shuidi_pname: 2025041486173046
  - shuidi_pkey: 3303b6a7e64ac0b18b5f17aafde52c71

## Cursor使用示例
1. "统计一下全国各省的企业数据，并展示为地图"
2. "上海昨天有多少新成立的企业?"
3. "查一下*****有限公司的基本信息"
4. "*******有限公司有哪些股东？"
5. "*******有限公司的科技创新能力怎么样？"
6. "查一下*******有限公司的风险信息？"
7. "查一下*******有限公司的荣誉资质？"
8. "查一下*******有限公司的联系方式？"
9. "查一下*******有限公司的对外投资信息？"
10. "*******有限公司有哪些资质证书？"
11. "*******有限公司的王**还在哪些公司任职？"
12. "*******有限公司的实控人是谁？"
13. "*******有限公司有哪些受益所有人？"





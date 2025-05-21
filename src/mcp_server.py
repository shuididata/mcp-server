import asyncio
import inspect
import sys
from functools import wraps
from loguru import logger
from mcp.server import FastMCP

from api_tool import create_api_adapter, create_search_api_adapter
from normalizer import Area, CompanyStatus, DateRange, normalize_company_name

mcp = FastMCP(name='Shuidi DataMcpServer')

def create_bad_resonse(message) -> dict:
    return {'statusCode':99999, 'statusMessage': message}

def normalize_company(param_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response =  await func(*args, **kwargs)
            if response.get('statusCode') == 2:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if param_name in params:
                    param_index = params.index(param_name)
                    if kwargs.get(param_name):
                        company_name = kwargs.get(param_name)
                    else:
                        args = list(args)
                        company_name = args[param_index]
                    n_company_name = await normalize_company_name(company_name)
                    if n_company_name and company_name != n_company_name:
                        if kwargs.get(param_name):
                            kwargs[param_name] = n_company_name
                        else:
                            args[param_index] = n_company_name
                            args = tuple(args)
                        return await func(*args, **kwargs)
            return response
        return wrapper
    return decorator


@mcp.tool()
async def search_established_companies(province=None, city=None, district=None, establish_date=None) -> dict:
    """
    输入省份、城市、成立日期查询并统计某时间段成立的企业
    回答问题时结果中请先说明查询到的企业数，并以列表的形式列出查询到的前10条企业
    :param province String 省份,例如上海,新疆,江苏,为None时表示查询全国的企业
    :param city String 城市,地级市，例如杭州，苏州
    :param district String 区县,区县名称需完整,包含市、县、区,例如昆山市，浦东新区
    :param establish_date String 成立期限，格式如yyyy-mm-dd@yyyy-mm-dd
                                          2023-01-12@2023-11-11 表示2012年1月12日到2023年11月11日之间成立的企业,
                                          2023-01-12@2023-01-12 表示2012年1月12日成立的企业,
                                          2023-01-12@表示2023年1月12号及之后成立的企业,
                                          @2023-11-11表示23年11月11日之前成立的公司,
                                          为None时表示任意时间成立的企业。

    :return
    statusCode	int	1代表成功,其他表示失败
    data.num_found	String	返回的公司记录数

    companyName String 公司名称
    establishDate String 成立时间
    companyStatusStr String 公司状态,
    capital String 注册资本
    legalPerson String 法人
    creditNo String 统一信用码
    """

    try:
        area = Area(province=province, city=city, district=district)
        establish_date = DateRange(date_range=establish_date).date_range
        params = {'province': area.province, 'city': area.city, 'district': area.district, 'establishDate':establish_date, 'company_type':'有限责任公司,股份有限公司,股份合作公司,国有企业,央企,集体所有制,全民所有制,独资企业,有限合伙,普通合伙,外商投资企业,港、澳、台商投资企业,联营企业,私营企业'}
        adapter = create_search_api_adapter()
        return await adapter.invoke(params)
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"查询统计企业失败！{e}")


@mcp.tool()
async def search_established_selfemployed(province=None, city=None, district=None, establish_date=None) -> dict:
    """
    输入省份、城市、成立日期查询并统计某时间段成立的个体工商户
    回答问题时结果中请先说明查询到的记录数，并以列表的形式列出查询到的前10条个体工商户
    :param province String 省份,例如上海,新疆,江苏,为None时表示查询全国的企业
    :param city String 城市,地级市，例如杭州，苏州
    :param district String 区县,区县名称需完整,包含市、县、区,例如昆山市，浦东新区
    :param establish_date String 成立期限，格式如yyyy-mm-dd@yyyy-mm-dd
                                          2023-01-12@2023-11-11 表示2012年1月12日到2023年11月11日之间成立的企业,
                                          2023-01-12@2023-01-12 表示2012年1月12日成立的企业,
                                          2023-01-12@表示2023年1月12号及之后成立的企业,
                                          @2023-11-11表示23年11月11日之前成立的公司,
                                          为None时表示任意时间成立的企业。

    :return
    statusCode	int	状态码1代表成功,其他代表失败
    data.num_found	String	返回的记录数

    companyName String 公司名称
    establishDate String 成立时间
    companyStatusStr String 公司状态,
    capital String 注册资本
    legalPerson String 法人
    creditNo String 统一信用码
    """

    try:
        area = Area(province=province, city=city, district=district)
        establish_date = DateRange(date_range=establish_date).date_range
        params = {'province': area.province, 'city': area.city, 'district': area.district, 'establishDate':establish_date, 'company_type':'个体工商户'}
        adapter = create_search_api_adapter()
        return await adapter.invoke(params)
    except Exception as e:
        logger.error(e)
        return create_bad_resonse("查询统计个体户失败！{e}")

@mcp.tool()
async def search_companies(province=None, city=None, district=None, company_status=None) -> dict:
    """
    输入省份、城市、企业状态查询并统计企业
    回答问题时结果中请先说明查询到的记录数，并以列表的形式列出查询到的前10条企业
    :param province String 省份,例如上海,新疆,江苏,为None时表示查询全国的企业
    :param city String 城市,地级市，例如杭州，苏州
    :param district String 区县,区县名称需完整,包含市、县、区,例如昆山市，浦东新区
    :param company_status String 企业状态可以设为"正常"、"异常"、"在营"、"存续"、"在业"、"吊销"、"注销"、"迁入"、"迁出"、"撤销"、"清算"、"停业"、"其他"
                                 企业状态正常，包括了在营、存续、在业、迁入、迁出的企业
                                 企业状态异常，包括了吊销、注销企业
    :return
    statusCode	int	状态码1代表成功,其他代表失败
    data.num_found	String	返回的记录数

    companyName String 公司名称
    establishDate String 成立时间
    companyStatusStr String 公司状态,
    capital String 注册资本
    legalPerson String 法人
    creditNo String 统一信用码
    """

    try:
        area = Area(province=province, city=city, district=district)
        company_status = CompanyStatus(status=company_status).status
        params = {'province': area.province, 'city': area.city, 'district': area.district, 'company_status': company_status, 'company_type': '有限责任公司,股份有限公司,股份合作公司,国有企业,央企,集体所有制,全民所有制,独资企业,有限合伙,普通合伙,外商投资企业,港、澳、台商投资企业,联营企业,私营企业'}
        adapter = create_search_api_adapter()
        return await adapter.invoke(params)
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"查询统计企业失败！{e}")

@mcp.tool()
async def search_selfemployed(province=None, city=None, district=None, company_status=None) -> dict:
    """
    输入省份、城市、企业状态查询并统计个体户
    回答问题时结果中请先说明查询到的记录数，并以列表的形式列出查询到的前10条个体户
    :param province String 省份,例如上海,新疆,江苏,为None时表示查询全国的企业
    :param city String 城市,地级市，例如杭州，苏州
    :param district String 区县,区县名称需完整,包含市、县、区,例如昆山市，浦东新区
    :param company_status String 企业状态可以设为"正常"、"异常"、"在营"、"存续"、"在业"、"吊销"、"注销"、"迁入"、"迁出"、"撤销"、"清算"、"停业"、"其他"
                                 企业状态正常，包括了在营、存续、在业、迁入、迁出的企业
                                 企业状态异常，包括了吊销、注销企业
    :return
    statusCode	int	状态码1代表成功,其他代表失败
    data.num_found	String	返回的记录数

    companyName String 公司名称
    establishDate String 成立时间
    companyStatusStr String 公司状态,
    capital String 注册资本
    legalPerson String 法人
    creditNo String 统一信用码
    """
    try:
        area = Area(province=province, city=city, district=district)
        company_status = CompanyStatus(status=company_status).status
        params = {'province': area.province, 'city': area.city, 'district': area.district, 'company_status': company_status, 'company_type': '个体工商户'}
        adapter = create_search_api_adapter()
        return await adapter.invoke(params)
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"查询统计个体户失败!{e}")

@mcp.tool()
@normalize_company('company_name')
async def get_company_info(company_name: str) -> dict:
    """
    根据公司名查询公司的基础信息（也称营业执照照面信息），包括统一信用码、企业注册码、企业类型、法定代表人、成立时间、注册资本、企业地址、营业期限、经营范围、登记机关、登记状态、核准时间
    :param company_name: 公司名称
    :returns json格式的公司信息，具体返回参数如下：
        OperationStartDate	String	营业日期
        OperationEndDate	String	截止日期
        IssueDate	String	核准时间
        CompanyName	String	公司名称
        CompanyType	String	企业类型
        LegalPerson	String	法定代表人
        Capital	String	注册资本
        CompanyCode	String	注册码
        CompanyAddress	String	企业地址
        BusinessScope	String	经营范围
        Authority	String	登记机关
        CompanyStatus	String	登记状态
        EstablishDate	String	成立时间
        CreditNo	String	企业信用代码
    """

    try:
        adapter = create_api_adapter('http://api.shuidi.cn/utn/ic/Base/V1')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取企业[{company_name}]基础信息失败!{e}")


@mcp.tool()
@normalize_company('company_name')
async def get_company_partner(company_name:str) -> dict:
    """
    根据企业名称获取企业的股东信息
    :param company_name: 企业名称
    :return:
    total Number 股东总数
    items list 股东列表，每个股东包含:
        includeDate String 股东进入日期
        currency String 币种
        name String 股东名
        type Number 股东自然人标记： 0-机构 1-人 2-其它
        stockType String 工商股东类型
        stockProportion String 出资比例
        identifyType String 证照/证件类型
        identifyNo String 证照/证件编号
        stockRealCapital String 实缴出资额
        stockCapital String 认缴出资额
        holderNum String 持股数
    """
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/ic/Partners/V2')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取企业[{company_name}]股东信息失败!{e}")

@mcp.tool()
@normalize_company('company_name')
async def get_stie_score(company_name:str) -> dict:
    """
    评估企业科创能力，给出科创能力评分及等级
    :param company_name: 公司名称
    :return:
    company_name String 企业名称
    credit_no String 社会统一信用代码
    score Number 科创评分
    level String 科创评级
    ranking Object 科创排名
    rating_dimension Object 维度评分
    qualification Array 科技资质
    company_base_infos Object 企业基本信息

    history_names Array 曾用名
    establish_date String 成立日期
    legal_person String 法定代表人
    capital String 注册资本
    real_capital String 实缴资本
    company_type String 企业类型
    authority String 登记机关
    company_status String 登记状态
    staff_size String 人员规模
    insurance_num Number 参保人数
    nei_industry_l2_code String 国标行业码值（二级）
    nei_industry_l2_name String 国标行业名称（二级）
    sei_industry_l2_code String 战略新兴行业码值（二级）
    sei_industry_l2_name String 战略新兴行业名称（二级）
    company_nature String 企业性质
    company_address String 注册地址
    business_scope String 经营范围
    province String 省份
    scale String 企业规模

    nei_industry_l2_ranking Number 国标二级行业该科创等级排名（前%）
    sei_industry_l2_ranking Number 战略新兴二级行业排名（前%）
    nei_industry_l2_province_ranking Number 国标二级行业地域排名（前%）
    sei_industry_l2_province_ranking Number 战略新兴二级行业地域排名（前%）

    stii_invest_score_to_100 Number 创新投入评分（百分制）
    stii_output_score_to_100 Number 创新产出评分（百分制）
    stii_quality_score_to_100 Number 创新质量评分（百分制）
    stii_influence_score_to_100 Number 创新影响评分（百分制）
    stii_develop_score_to_100 Number 创新成长评分（百分制）
    """

    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/stie/score')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"评估企业[{company_name}]科创能力失败！{e}")


@mcp.tool()
@normalize_company('company_name')
async def search_company_risk(company_name:str) -> dict:
    """
    根据公司名称查询公司的相关风险信息，包括企业自身风险、周边风险、预警信息等
    :param company_name: 公司名称
    :return:
    风险列表，具体包括以下几种类型
        self_risk 自我风险
        self_contract_risk 合作风险
        relation_risk 关联风险
        self_notice 自身重要信息
        relation_notice 关联重要信息
        self_history_risk 自我历史风险
        relation_history_risk 关联历史风险
    每种类型的风险，包括 total Number 事件总数， name String 事件名称, list_data 风险事件列表
    风险事件，包括 event_count Number 该风险事件发生总数，company_cnt Number 该风险事件涉及企业数量，data_type 风险事件类型, desc 风险描述, company_events 该风险事件具体详情列表
        事件类型包括：{"n1":"法定代表人变更","n2":"主要人员变更","n3":"股东信息变更","n4":"注册资本变更","n5":"对外投资变更","n6":"新增联系电话","n7":"新增联系邮箱","n8":"联系地址变更","n9":"新增icp备案",
                    "t1":"被执行人","t1h":"历史被执行人","t2":"失信被执行","t3":"裁判文书","t4":"法院公告","t5":"开庭公告","t6":"立案信息","t7":"终本案件","t8":"限制高消费","t9":"行政处罚(其它)","t10":" 欠税公告",
                    "t11":"税收违法","t12":"送达公告","t13":"司法拍卖","t14":"询价评估结果","t15":"询价评估机构","t16":"破产重整","t17":"司法协助","t18":"经营异常","t19":"行政处罚-工商","t20":"严重违法",
                    "t21":"股权出质","t22":"清算信息","t23":"动产抵押","t24":"简易注销","t25":"知识产权出质","t26":"抽查检查","t27":"对外担保","c1":"裁判文书(合同纠纷)","c2":"开庭公告(合同纠纷)"}
        company_events 中包含 cid 企业id, company_name 企业名称, company_event_count 该企业发生次数, tip 与查询企业的关系（1 表示股东，2 表示对外投资，3 表示分支机构, 空值表示当前查询企业）
    """
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/risk/CompanyRiskInfo')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取企业[{company_name}]风险信息失败!{e}")

@mcp.tool()
@normalize_company('company_name')
async def get_company_honor(company_name:str) -> dict:
    """
    根据公司名称获取该公司的荣誉资质
    :param company_name: 公司名称
    :return:
    total 荣誉资质总数
    items 资质荣誉列表, 每个荣誉资质包括
        HonorName String 资质荣誉名称
        HonorClass String 资质荣誉等级
        PublishOrg String 发布单位名称
        PublishDate String 发布日期
        StartDate String 开始日期
        EndDate String 截止日期
    """
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/cf/Honor')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return  create_bad_resonse(f"获取企业[{company_name}]荣誉资质信息失败!{e}")


@mcp.tool()
@normalize_company('company_name')
async def get_company_contact(company_name:str) -> dict:
    """
    根据公司名称获取该公司的联系方式，包括电话、邮箱、网站等
    :param company_name: 公司名称
    :return:
    Name 企业名称
    Telephone List 联系电话列表, 每个联系电话包括
        Contact String 电话
        DataSource String 电话来源
    Emails List 邮箱列表,
    Websites List 网站列表, 每个网站包括
        Website String 网站域名
        Title String 网站名称
        Icp String 网站备案号
    """
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/ic/GetContacts')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取企业[{company_name}]联系方式失败!{e}")


@mcp.tool()
@normalize_company('company_name')
async def get_company_investment(company_name:str) -> dict:
    '''
    根据企业名称获取该企业对外投资信息
    :param company_name: 企业名称
    :return:
    Items 对外投资列表，每个投资信息包括：
        Name String 企业名称
        No String 注册号
        OperName String 法人名称
        RegistCapi String 注册资本
        StartDate String 成立日期
        Status String 状态
        CreditCode  String 社会统一信用代码
        EconKind String 企业类型
        FundedRatio String 出资比例
    '''
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/ic/Invest/V3')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取企业[{company_name}]对外投资信息失败!{e}")


@mcp.tool()
@normalize_company('company_name')
async def get_company_cert(company_name:str) -> dict:
    """
    根据企业名称获取该企业的资质证书
    :param company_name: 企业名称
    :return:
    total Number 资质证书总数
    items List  资质证书列表，每个证书包括：
        endDate String 结束时间
        startDate String 开始时间
        issueDate String 发证日期
        certNo  String 证书编号
        type    String  证书类型
        orgAn   String  发证单位
        status  String  证书状态
    """
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/ip/CertificateList/V2')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取企业[{company_name}]资质证书失败!{e}")

@mcp.tool()
@normalize_company('company_name')
async def get_person_related_company(company_name:str, person_name:str) -> dict:
    """
    通过公司名称和人名获取企业人员的所有相关公司，包括其担任法人、股东、董监高的公司信息
    :param company_name: 公司名称
    :param person_name: 人名
    :return:
    total Number 总数
    isAll Number 是否已全部返回。1全部返回，0已返回前1000个企业
    items List  任职相关信息，每条信息包括：
        estiblishTime Number 开业时间
        regStatus String 经营状态
        type String 类型，包括法人、股东、执行董事、高管等
        regCapital String 注册资本
        name String 公司名
        creditNo    String 统一信用代码
    """
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/cp/AllCompanys')
        return await adapter.invoke({'name': company_name, 'humanName':person_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取[{company_name}:{person_name}]的关联公司信息失败!{e}")


@mcp.tool()
@normalize_company('company_name')
async def get_company_controller(company_name:str) -> dict:
    """
    根据企业名称获取该企业的实控人信息,并显示控制路径
    :param company_name: 企业名称
    :return:
    ControllerData Array<Object> 实控人数据详情,有可能是多人,每个实控人信息包括：
        AcName String 实控人名称
        IsPersonal String 0非自然人，1自然人
        VotePercent String 表决权（百分比）
        beneficiaProportion String 最终持股比例
        Paths List<List<Object>> 控制路径,每条控制路径包括以下信息:
            StartName String 起始节点名称
            StartNodeType String 起始节点类型。0非自然人，1自然人
            EndNode String 结束节点id
            EndName String 结束节点名称
            EndNodeType String  结束节点类型。0非自然人，1自然人
            Type String 关系类型。INVEST 投资关系，OWN法定代表人关系，BRANCH 分总公司
            Sequence Integer 路径序号。从0开始，依次向下穿透
            Proportion  String  持股比例（百分比）
            StartNode String 起始节点id
    """
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/pic/ActualController')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取企业[{company_name}]的实控人信息失败!{e}")

@mcp.tool()
@normalize_company('company_name')
async def get_company_benificalowner(company_name:str) -> dict:
    """
    根据企业名称查询该企业的受益所有人信息
    :param company_name: 企业名称
    :return:
    Total Integer 受益所有人数量
    BeneficialOwnerData List<Object> 受益所有人列表，每个受益所有人信息包括：
        BoName String 受益人名称
        IsPersonal String 0为非自然人，1为自然人
        StockPercent String 受益股份
        BoType String 受益类型（1直接或间接持股，3关键决策人员，4法定代表人/负责人）。同时符合多个的，中间用英文逗号隔开，如：1,3,4。
        Position String 受益人担任的职位
        Paths List<Object> 全部受益路径，每个受益路径包括：
            StartNode String 起始节点id
            StartName String 起始节点名称
            StartNodeType String 起始节点类型。1自然人，2非自然人
            EndNode String  结束节点
            EndName String  结束节点名称
            EndNodeType String  结束节点类型。1自然人，2非自然人
            Type    String 关系类型。 INVEST 投资关系，OWN法定代表人关系，BRANCH 分总公司
            Sequence Integer 路径序号。从0开始，依次向下穿透
            Proportion String 持股比例
    """
    try:
        adapter = create_api_adapter('https://api.shuidi.cn/utn/pic/BeneficialOwner')
        return await adapter.invoke({'keyword': company_name})
    except Exception as e:
        logger.error(e)
        return create_bad_resonse(f"获取企业[{company_name}]受益所有人信息失败!{e}")


def init_logger():
    # 移除默认handler
    logger.remove()

    # 日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # 添加标准输出
    logger.add(sys.stdout, format=log_format, level="INFO", enqueue=True)
    # 设置异常处理
    logger.add(sys.stderr, format=log_format, level="ERROR", enqueue=True)


def main():
    init_logger()
    mcp.run(transport='stdio')

def test():
    info = asyncio.run(get_company_info(company_name='凭安征信'))
    print(info)


if __name__ == '__main__':
    main()
import re
from datetime import datetime
from typing import Optional, ClassVar, Literal


from pydantic.v1 import BaseModel
from pydantic.v1 import validator


class Area(BaseModel):
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

    PROVINCE_MAPPING: ClassVar[dict] = {
        "北京": "北京",
        "北京市": "北京",
        "天津": "天津",
        "天津市": "天津",
        "河北": "河北",
        "河北省": "河北",
        "山西": "山西",
        "山西省": "山西",
        "内蒙古": "内蒙古",
        "内蒙古自治区": "内蒙古",
        "辽宁": "辽宁",
        "辽宁省": "辽宁",
        "吉林": "吉林",
        "吉林省": "吉林",
        "黑龙江": "黑龙江",
        "黑龙江省": "黑龙江",
        "上海": "上海",
        "上海市": "上海",
        "江苏": "江苏",
        "江苏省": "江苏",
        "浙江": "浙江",
        "浙江省": "浙江",
        "安徽": "安徽",
        "安徽省": "安徽",
        "福建": "福建",
        "福建省": "福建",
        "江西": "江西",
        "江西省": "江西",
        "山东": "山东",
        "山东省": "山东",
        "河南": "河南",
        "河南省": "河南",
        "湖北": "湖北",
        "湖北省": "湖北",
        "湖南": "湖南",
        "湖南省": "湖南",
        "广东": "广东",
        "广东省": "广东",
        "广西": "广西",
        "广西壮族自治区": "广西",
        "海南": "海南",
        "海南省": "海南",
        "重庆": "重庆",
        "重庆市": "重庆",
        "四川": "四川",
        "四川省": "四川",
        "贵州": "贵州",
        "贵州省": "贵州",
        "云南": "云南",
        "云南省": "云南",
        "西藏": "西藏",
        "西藏自治区": "西藏",
        "陕西": "陕西",
        "陕西省": "陕西",
        "甘肃": "甘肃",
        "甘肃省": "甘肃",
        "青海": "青海",
        "青海省": "青海",
        "宁夏": "宁夏",
        "宁夏回族自治区": "宁夏",
        "新疆": "新疆",
        "新疆维吾尔自治区": "新疆",
        "台湾": "台湾",
        "台湾省": "台湾",
        "香港": "香港",
        "香港特别行政区": "香港",
        "澳门": "澳门",
        "澳门特别行政区": "澳门"
    }

    MUNICIPALITIES: ClassVar[list] = ['北京', '上海', '天津', '重庆']

    @validator('province')
    def normalize_province(cls, v) -> str:
        return cls.PROVINCE_MAPPING.get(v, v)

    @validator('city')
    def normalize_city(cls, v, values) -> str:
        city = v
        province = values.get('province')
        if province in cls.MUNICIPALITIES:
            city = province
            if v and city.find(v) == -1:
                district = v
                if not district.endswith('区'):
                    district = f"{district}区"
                values['district'] = district


        if city and not city.endswith('市'):
            city = f"{city}市"

        return city

    @validator('district')
    def normalize_district(cls, v, values) -> str:
        district = values.get('district', v)
        return district


class CompanyStatus(BaseModel):

    status: Optional[Literal['正常', '异常', '存续', '在营', '在业', '吊销', '注销', '迁入', '迁出', '撤销', '清算', '停业', '其他']] = None

    @validator('status')
    def normalize_status(cls, v) -> str:

        if v in ['存续', '在营', '在业']:
            return '存续,在业'

        if v == '正常':
            return '存续,在业,迁入,迁出'

        if v == '异常':
            return '吊销,注销'

        if v == '其他':
            return '撤销,清算,停业,其他'

        return v


class DateRange(BaseModel):

    date_range: Optional[str] = None

    @validator('date_range')
    def validate_date_range(cls, v):
        if v is None:
            return v

        # 检查基本格式
        pattern = r'^(?:\d{4}-\d{2}-\d{2})?@(?:\d{4}-\d{2}-\d{2})?$'
        if not re.match(pattern, v):
            raise ValueError('日期格式必须为 yyyy-mm-dd@yyyy-mm-dd 或其变体')

        start_date_str, end_date_str = v.split('@')

        # 验证日期格式
        def is_valid_date(date_str: str) -> bool:
            if not date_str:
                return True
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False

        if not is_valid_date(start_date_str) or not is_valid_date(end_date_str):
            raise ValueError('无效的日期格式')

        # 如果两个日期都存在，验证开始日期不大于结束日期
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            if start_date > end_date:
                raise ValueError('开始日期不能大于结束日期')

        return v

    def get_date_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """获取日期范围的辅助方法"""
        if not self.date_range:
            return None, None

        start_str, end_str = self.date_range.split('@')

        start_date = datetime.strptime(start_str, '%Y-%m-%d') if start_str else None
        end_date = datetime.strptime(end_str, '%Y-%m-%d') if end_str else None

        return start_date, end_date

def main():
    try:
        area = Area(province='江苏', city=None, district=None)
        print(f"{area.province}, {area.city}, {area.district}")

        company = CompanyStatus(status='异常')
        print(company.status)

        establish_date = DateRange(date_range='2023-01-02@2023-01-02')
        print(establish_date.date_range)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
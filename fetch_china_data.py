import yfinance as yf

# Chinese Stock Info Mapping (Name and Description)
CHINA_STOCK_INFO = {
    "600519.SS": {"name": "贵州茅台", "desc": "中国最大的白酒生产企业，主产茅台酒，被誉为国酒，拥有强大的品牌护城河和定价权。"},
    "300750.SZ": {"name": "宁德时代", "desc": "全球领先的锂离子电池研发制造公司，专注于新能源汽车动力电池系统、储能系统的研发、生产和销售。"},
    "601318.SS": {"name": "中国平安", "desc": "中国领先的个人金融服务集团，业务涵盖保险、银行、投资等领域，致力于成为国际领先的个人金融生活服务提供商。"},
    "600036.SS": {"name": "招商银行", "desc": "中国领先的零售银行，以其优质的服务和金融科技创新能力著称，拥有庞大的高净值客户群。"},
    "002594.SZ": {"name": "比亚迪", "desc": "中国领先的新能源汽车制造商，同时在手机部件及组装、二次充电电池及光伏业务方面具备全球领先地位。"},
    "600276.SS": {"name": "恒瑞医药", "desc": "中国最大的抗肿瘤药、手术用药和造影剂的研究和生产基地之一，拥有强大的研发管线。"},
    "000858.SZ": {"name": "五粮液", "desc": "中国著名的白酒制造商，主产五粮液酒，是中国浓香型白酒的典型代表。"},
    "600900.SS": {"name": "长江电力", "desc": "中国最大的电力上市公司，主要从事水力发电业务，拥有三峡、葛洲坝等大型水电站。"},
    "000333.SZ": {"name": "美的集团", "desc": "全球领先的消费电器、暖通空调、机器人及工业自动化系统、智能供应链（物流）的科技集团。"},
    "601888.SS": {"name": "中国中免", "desc": "中国最大的免税运营商，主要从事免税商品的批发和零售业务，受益于消费回流政策。"},
    "603288.SS": {"name": "海天味业", "desc": "中国最大的调味品生产企业，主打酱油、蚝油、调味酱等产品，拥有强大的渠道掌控力。"},
    "300015.SZ": {"name": "爱尔眼科", "desc": "中国最大的眼科医疗连锁机构，提供全眼科医疗服务，拥有广泛的医院网络。"},
    "000651.SZ": {"name": "格力电器", "desc": "中国领先的家电企业，以空调业务为核心，同时布局智能装备、通信设备等领域。"},
    "601012.SS": {"name": "隆基绿能", "desc": "全球最大的单晶硅光伏产品制造商，致力于推动光伏发电成本下降，促进清洁能源普及。"},
    "600030.SS": {"name": "中信证券", "desc": "中国领先的证券公司，业务涵盖证券经纪、投行、资产管理等全方位金融服务。"},
    "002415.SZ": {"name": "海康威视", "desc": "全球领先的以视频为核心的物联网解决方案提供商，提供安防、智能家居、机器人等产品。"},
    "600887.SS": {"name": "伊利股份", "desc": "中国规模最大、产品线最全的乳制品企业，位居全球乳业五强。"},
    "600309.SS": {"name": "万华化学", "desc": "全球领先的MDI生产商，业务涵盖聚氨酯、石化、精细化学品及新兴材料。"},
    "002475.SZ": {"name": "立讯精密", "desc": "中国领先的精密制造企业，主要服务于消费电子、通信、汽车等领域，是苹果公司的核心供应商。"},
    "601166.SS": {"name": "兴业银行", "desc": "中国主要的股份制商业银行之一，以绿色金融和同业业务见长。"},
    "600000.SS": {"name": "浦发银行", "desc": "中国主要的股份制商业银行，总部位于上海，提供全面的商业银行服务。"},
    "000001.SZ": {"name": "平安银行", "desc": "中国平安集团旗下的股份制商业银行，致力于打造中国最卓越、全球领先的智能化零售银行。"},
    "601398.SS": {"name": "工商银行", "desc": "中国最大的商业银行，也是全球资产规模最大的银行之一，提供广泛的金融产品和服务。"},
    "601288.SS": {"name": "农业银行", "desc": "中国主要的商业银行之一，拥有庞大的网点网络，服务于广泛的城乡客户。"},
    "601939.SS": {"name": "建设银行", "desc": "中国主要的商业银行之一，在基础设施建设贷款和住房按揭贷款领域具有优势。"},
    "601988.SS": {"name": "中国银行", "desc": "中国国际化程度最高的商业银行，拥有广泛的海外分支机构。"},
    "601857.SS": {"name": "中国石油", "desc": "中国最大的油气生产商和销售商之一，业务涵盖石油天然气勘探开发、炼油化工等。"},
    "600028.SS": {"name": "中国石化", "desc": "中国最大的炼油商和石化产品生产商之一，拥有庞大的加油站网络。"},
    "601088.SS": {"name": "中国神华", "desc": "中国最大的煤炭上市公司，业务涵盖煤炭生产、电力、铁路、港口等一体化能源业务。"},
    "300760.SZ": {"name": "迈瑞医疗", "desc": "中国领先的医疗器械制造商，产品涵盖生命信息与支持、体外诊断、医学影像等领域。"},
}

def get_china_tickers():
    """
    Returns a curated list of top Chinese A-share stocks (Blue Chips).
    """
    return list(CHINA_STOCK_INFO.keys())

def get_china_stock_info(ticker):
    """
    Returns the Chinese name and description for a given ticker.
    """
    return CHINA_STOCK_INFO.get(ticker, {"name": ticker, "desc": "暂无简介"})


def get_stock_data(ticker):
    """
    Fetches data for a single stock using yfinance.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Test
    tickers = get_china_tickers()
    print(f"Found {len(tickers)} tickers.")
    print("Fetching data for first ticker...")
    data = get_stock_data(tickers[0])
    if data:
        print(f"Name: {data.get('longName')}")
        print(f"Market Cap: {data.get('marketCap')}")

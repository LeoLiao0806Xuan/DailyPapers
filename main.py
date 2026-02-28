import requests
import json
from datetime import datetime, timedelta
import time
import config

# 关闭SSL警告（避免证书问题）
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ------------------------------
# 多轮抓取论文（修复400错误）
# ------------------------------
def crawl_papers():
    papers = []
    print(f"🔍 开始抓取【{config.SEARCH_KEYWORDS}】领域近{config.TIME_RANGE_DAYS}天论文（多轮抓取）...")
    
    # 时间过滤条件（格式严格符合CrossRef要求）
    from_date = (datetime.now() - timedelta(days=config.TIME_RANGE_DAYS)).strftime("%Y-%m-%d")
    base_url = "https://api.crossref.org/works"
    
    # 多轮抓取：拆分总数量为多个批次
    total_batches = config.TOTAL_CRAWL_COUNT // config.CRAWL_BATCH_SIZE
    for batch in range(total_batches):
        offset = batch * config.CRAWL_BATCH_SIZE
        
        # 修复：分步构建filter参数，避免格式错误
        filter_parts = [
            f"from-pub-date:{from_date}",
            "type:journal-article"
        ]
        # 仅当语言参数非空时添加（避免空值导致格式错误）
        if config.LANGUAGE_SCOPE.strip():
            filter_parts.append(f"language:{config.LANGUAGE_SCOPE.strip()}")
        
        # 通用查询参数（修复格式问题）
        params = {
            "query": config.SEARCH_KEYWORDS.strip(),  # 去除首尾空格
            "filter": ",".join(filter_parts),         # 正确拼接filter
            "sort": "is-referenced-by-count",         # 按引用量降序
            "order": "desc",
            "rows": config.CRAWL_BATCH_SIZE,
            "offset": offset,
            "mailto": "your-email@example.com"        # 添加mailto，避免API限流（可选）
        }
        
        try:
            # 发送请求（简化Header，避免被拦截）
            response = requests.get(
                base_url,
                params=params,
                timeout=25,
                headers={"User-Agent": "Mozilla/5.0"},
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                batch_items = data.get('message', {}).get('items', [])
                print(f"📌 第{batch+1}轮：抓取到 {len(batch_items)} 篇基础论文")
                
                # 提取论文核心信息（通用字段）
                for item in batch_items:
                    # 处理发表时间（兼容不同格式）
                    pub_date_parts = item.get('published', {}).get('date-parts', [['未知时间']])[0]
                    pub_date = '-'.join([str(p) for p in pub_date_parts[:3]])  # 取年-月-日
                    
                    papers.append({
                        "title": item.get('title', ['未知标题'])[0],
                        "link": item.get('URL', '#'),
                        "journal": item.get('container-title', ['未知期刊'])[0],
                        "citations": item.get('is-referenced-by-count', 0),
                        "published": pub_date,
                        "authors": ", ".join([f"{auth.get('family', '')} {auth.get('given', '')}".strip() 
                                             for auth in item.get('author', [])[:3]]) or "未知作者"
                    })
            else:
                print(f"❌ 第{batch+1}轮：请求失败（状态码: {response.status_code}）")
                print(f"❌ 错误详情：{response.text[:200]}")  # 打印错误详情，方便排查
                break
            
            # 轮次间延迟，避免API限流
            time.sleep(config.CRAWL_DELAY)
        
        except Exception as e:
            print(f"❌ 第{batch+1}轮：抓取异常 - {str(e)[:60]}")
            break
    
    # 本地筛选：优先高影响因子期刊 + 按引用量排序
    high_impact_papers = [p for p in papers if p['journal'] in config.HIGH_IMPACT_JOURNALS]
    other_papers = [p for p in papers if p['journal'] not in config.HIGH_IMPACT_JOURNALS]
    
    # 合并排序：高影响因子期刊在前，同组内按引用量降序
    sorted_papers = sorted(high_impact_papers, key=lambda x: x['citations'], reverse=True) + \
                    sorted(other_papers, key=lambda x: x['citations'], reverse=True)
    
    print(f"✅ 总计筛选出 {len(sorted_papers)} 篇相关论文（高影响因子期刊优先）")
    return sorted_papers

# ------------------------------
# 主流程（通用逻辑）
# ------------------------------
if __name__ == "__main__":
    # 打印抓取信息
    print("="*60)
    print(f"📅 通用论文抓取 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 领域：{config.SEARCH_KEYWORDS} | 近{config.TIME_RANGE_DAYS}天 | 引用量≥{config.MIN_CITATION_THRESHOLD}")
    print("="*60)

    # 1. 多轮抓取论文
    all_papers = crawl_papers()
    if not all_papers:
        print("\n❌ 未抓取到符合条件的论文")
        exit()

    # 2. 筛选高引用论文（≥阈值）
    high_citation_papers = [p for p in all_papers if p['citations'] >= config.MIN_CITATION_THRESHOLD]
    print(f"\n📊 引用量≥{config.MIN_CITATION_THRESHOLD}的论文：{len(high_citation_papers)} 篇")

    # 3. 选择指定数量论文
    selected_papers = high_citation_papers[:config.PAPER_COUNT] if high_citation_papers else all_papers[:config.PAPER_COUNT]

    # 4. 生成GitHub Issue内容
    print(f"\n🚀 推送 {len(selected_papers)} 篇高影响力论文到GitHub...")
    issue_title = f"[{config.SEARCH_KEYWORDS}] 高引用论文推荐 {datetime.now().strftime('%Y-%m-%d')}"
    issue_body = f"""# {config.SEARCH_KEYWORDS} 领域高影响力论文推荐 ({datetime.now().strftime('%Y-%m-%d')})

### 📚 筛选规则
- **领域**：{config.SEARCH_KEYWORDS}
- **时间**：近 {config.TIME_RANGE_DAYS} 天发表
- **来源**：优先高影响因子期刊（{len(config.HIGH_IMPACT_JOURNALS)}个核心刊）
- **门槛**：引用量≥{config.MIN_CITATION_THRESHOLD}
- **排序**：高影响因子期刊优先，同期刊内按引用量降序

---
"""

    # 拼接论文列表
    for i, paper in enumerate(selected_papers):
        issue_body += f"""
## {i+1}. {paper['title']}
> 期刊：{paper['journal']} | 发表时间：{paper['published']} | 引用量：{paper['citations']} | 作者：{paper['authors']}
- 原文链接：{paper['link']}

---
"""

    # 5. 推送至GitHub Issue
    try:
        response = requests.post(
            f"https://api.github.com/repos/{config.REPO_OWNER}/{config.REPO_NAME}/issues",
            headers={
                "Authorization": f"token {config.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "title": issue_title,
                "body": issue_body
            }),
            timeout=25,
            verify=False
        )
        
        if response.status_code == 201:
            res_json = response.json()
            print(f"🎉 推送成功！Issue地址：{res_json['html_url']}")
        else:
            print(f"❌ 推送失败（状态码: {response.status_code}）")
            print(f"❌ 错误详情：{response.text[:200]}")
    except Exception as e:
        print(f"❌ 推送异常：{str(e)[:60]}")
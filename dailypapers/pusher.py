import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from .utils import setup_logger

logger = setup_logger('pusher')

class PaperPusher:
    """
    论文推送类，负责将论文推送至 GitHub Issue 和邮件
    """
    
    def __init__(self, github_token, repo_owner, repo_name):
        """
        初始化推送器
        
        Args:
            github_token (str): GitHub 个人访问令牌
            repo_owner (str): GitHub 仓库所有者
            repo_name (str): GitHub 仓库名称
        """
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
    
    def push_to_github(self, papers, keywords, time_range_days, min_citation_threshold, high_impact_journals):
        """
        推送论文到 GitHub Issue
        
        Args:
            papers (list): 论文列表
            keywords (str or list): 关键词
            time_range_days (int): 时间范围（天）
            min_citation_threshold (int): 最低引用量阈值
            high_impact_journals (list): 高影响因子期刊列表
            
        Returns:
            str: Issue URL（如果成功）
        """
        if not papers:
            logger.error("没有论文可推送")
            return None
        
        keywords_display = keywords if isinstance(keywords, str) else "多个关键词"
        logger.info(f"推送 {len(papers)} 篇高影响力论文到GitHub...")
        
        # 生成 Issue 内容
        issue_title = f"[{keywords_display}] 高引用论文推荐 {datetime.now().strftime('%Y-%m-%d')}"
        issue_body = f"""# {keywords_display} 领域高影响力论文推荐 ({datetime.now().strftime('%Y-%m-%d')})

### 📚 筛选规则
- **领域**：{keywords_display}
- **时间**：近 {time_range_days} 天发表
- **来源**：优先高影响因子期刊（{len(high_impact_journals)}个核心刊）
- **门槛**：引用量≥{min_citation_threshold}
- **排序**：高影响因子期刊优先，同期刊内按引用量降序

---
"""

        # 拼接论文列表
        for i, paper in enumerate(papers):
            issue_body += f"""
## {i+1}. {paper['title']}
> 期刊：{paper['journal']} | 发表时间：{paper['published']} | 引用量：{paper['citations']} | 作者：{paper['authors']}
- 原文链接：{paper['link']}

---
"""

        # 推送 GitHub
        try:
            response = requests.post(
                f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues",
                headers={
                    "Authorization": f"token {self.github_token}",
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
                issue_url = res_json['html_url']
                logger.info(f"推送成功！Issue地址：{issue_url}")
                return issue_url
            else:
                logger.error(f"推送失败（状态码: {response.status_code}）")
                logger.error(f"错误详情：{response.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"推送异常：{str(e)[:60]}")
            return None
    
    def send_email(self, papers, keywords, to_email, smtp_config, time_range_days, min_citation_threshold):
        """
        发送邮件
        
        Args:
            papers (list): 论文列表
            keywords (str or list): 关键词
            to_email (str): 收件人邮箱
            smtp_config (dict): SMTP 配置
            time_range_days (int): 时间范围（天）
            min_citation_threshold (int): 最低引用量阈值
            
        Returns:
            bool: 是否发送成功
        """
        if not papers:
            logger.error("没有论文可发送")
            return False
        
        try:
            # 生成邮件内容
            keywords_display = keywords if isinstance(keywords, str) else "多个关键词"
            subject = f"[{keywords_display}] 高引用论文推荐 {datetime.now().strftime('%Y-%m-%d')}"
            
            # 构建邮件正文
            body = f"# {keywords_display} 领域高影响力论文推荐\n\n"
            body += f"**日期：** {datetime.now().strftime('%Y-%m-%d')}\n\n"
            body += "## 筛选规则\n"
            body += f"- **领域**：{keywords_display}\n"
            body += f"- **时间**：近 {time_range_days} 天发表\n"
            body += f"- **来源**：优先高影响因子期刊\n"
            body += f"- **门槛**：引用量≥{min_citation_threshold}\n\n"
            body += "## 推荐论文\n\n"
            
            for i, paper in enumerate(papers):
                body += f"### {i+1}. {paper['title']}\n"
                body += f"- **期刊**：{paper['journal']}\n"
                body += f"- **发表时间**：{paper['published']}\n"
                body += f"- **引用量**：{paper['citations']}\n"
                body += f"- **作者**：{paper['authors']}\n"
                body += f"- **原文链接**：{paper['link']}\n\n"
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = smtp_config.get('from_email')
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'markdown'))
            
            # 发送邮件
            with smtplib.SMTP(smtp_config.get('smtp_server'), smtp_config.get('smtp_port')) as server:
                server.starttls()
                server.login(smtp_config.get('smtp_username'), smtp_config.get('smtp_password'))
                server.send_message(msg)
            
            logger.info(f"邮件发送成功，收件人：{to_email}")
            return True
        except Exception as e:
            logger.error(f"邮件发送失败：{str(e)[:60]}")
            return False

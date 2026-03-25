import os
import requests
import time

# 1. 从 GitHub 保险箱获取密钥
SESSION = os.environ.get('LEETCODE_SESSION')
CSRF = os.environ.get('LEETCODE_CSRF_TOKEN')

HEADERS = {
    'Cookie': f'LEETCODE_SESSION={SESSION}; csrftoken={CSRF}',
    'X-CSRFToken': CSRF,
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

def fetch_data():
    url = "https://leetcode.cn/graphql/"
    
    # 2. 查询最近 15 次通过的提交记录
    query_submissions = """
    query {
        recentAcSubmissions(limit: 15) {
            submissionId
            question { title }
        }
    }
    """
    print("正在连接力扣中文站...")
    try:
        response = requests.post(url, json={"query": query_submissions}, headers=HEADERS)
        submissions = response.json().get('data', {}).get('recentAcSubmissions', [])
        
        if not submissions:
            print("未能获取到记录，可能是 Cookie 失效。")
            return
            
        if not os.path.exists("my-leetcode-code"):
            os.makedirs("my-leetcode-code")
            
        # 3. 循环获取每一题的具体代码
        for sub in submissions:
            sub_id = sub['submissionId']
            title = sub['question']['title']
            print(f"正在同步: {title}")
            
            query_code = """
            query submissionDetails($submissionId: ID!) {
                submissionDetail(submissionId: $submissionId) {
                    code
                    lang
                }
            }
            """
            res_code = requests.post(url, json={"query": query_code, "variables": {"submissionId": sub_id}}, headers=HEADERS)
            detail = res_code.json().get('data', {}).get('submissionDetail', {})
            
            if detail:
                code = detail.get('code', '')
                lang = detail.get('lang', 'txt')
                
                # 自动匹配你常用的语言后缀
                ext = "py" if "python" in lang else "cpp" if lang == "cpp" else "txt"
                
                with open(f"my-leetcode-code/{title}.{ext}", "w", encoding="utf-8") as f:
                    f.write(code)
            time.sleep(1) # 礼貌性延迟，防止请求过快被拦截
            
        print("所有代码抓取完成！")
    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    fetch_data()

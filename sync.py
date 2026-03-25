import os
import requests
import time

# 从 GitHub 保险箱获取密钥
SESSION = os.environ.get('LEETCODE_SESSION')
CSRF = os.environ.get('LEETCODE_CSRF_TOKEN')

# 全副武装：模拟真实的浏览器请求头
HEADERS = {
    'Cookie': f'LEETCODE_SESSION={SESSION}; csrftoken={CSRF}',
    'x-csrftoken': CSRF, # 注意这里改成了小写，有些服务器严格区分大小写
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', # 伪装成真实的 Chrome 浏览器
    'Origin': 'https://leetcode.cn',
    'Referer': 'https://leetcode.cn/',
}

def fetch_data():
    url = "https://leetcode.cn/graphql/"
    
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
        
        # 【核心调试代码】：把服务器真实的脸色打印出来！
        print(f"力扣服务器返回状态码: {response.status_code}")
        print(f"力扣服务器返回详细内容: {response.text}")
        
        data = response.json()
        submissions = data.get('data', {}).get('recentAcSubmissions')
        
        # 针对不同错误情况的判断
        if submissions is None:
            print("❌ 错误：返回的数据格式不对，或者请求被拦截了。请看上面的详细内容。")
            return
        if not submissions:
            print("⚠️ 警告：请求成功了，但是近期没有通过的提交记录。")
            return
            
        if not os.path.exists("my-leetcode-code"):
            os.makedirs("my-leetcode-code")
            
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
                ext = "py" if "python" in lang else "cpp" if lang == "cpp" else "txt"
                with open(f"my-leetcode-code/{title}.{ext}", "w", encoding="utf-8") as f:
                    f.write(code)
            time.sleep(1.5) 
            
        print("所有代码抓取完成！")
    except Exception as e:
        print(f"代码运行崩溃报错: {e}")

if __name__ == "__main__":
    fetch_data()

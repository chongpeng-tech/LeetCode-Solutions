import os
import requests
import time

# 1. 从 GitHub 保险箱获取密钥
SESSION = os.environ.get('LEETCODE_SESSION')
CSRF = os.environ.get('LEETCODE_CSRF_TOKEN')

HEADERS = {
    'Cookie': f'LEETCODE_SESSION={SESSION}; csrftoken={CSRF}',
    'x-csrftoken': CSRF,
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Origin': 'https://leetcode.cn',
    'Referer': 'https://leetcode.cn/',
}

def fetch_data():
    # 步骤一：获取“快递清单”（只包含题目基本信息和 ID）
    list_url = "https://leetcode.cn/api/submissions/?offset=0&limit=20"
    print("正在获取提交记录清单...")
    
    try:
        response = requests.get(list_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"获取清单失败，状态码: {response.status_code}")
            return
            
        submissions = response.json().get('submissions_dump', [])
        
        if not submissions:
            print("清单为空，请检查是否有近期的提交记录。")
            return
            
        if not os.path.exists("my-leetcode-code"):
            os.makedirs("my-leetcode-code")
            
        graphql_url = "https://leetcode.cn/graphql/"
        
        # 步骤二：拿着清单里的 ID，挨个去“提货”（抓取真实代码）
        for sub in submissions:
            if sub.get('status_display') != 'Accepted':
                continue # 忽略没通过的代码
                
            title = sub.get('title', 'Unknown').replace(" ", "").replace("/", "_")
            sub_id = sub.get('id') # 这是提取代码的关键凭证
            
            print(f"找到题目: {title}, 准备提货代码...")
            
            # 向提货窗口发送的暗号
            query_code = """
            query submissionDetails($submissionId: ID!) {
                submissionDetail(submissionId: $submissionId) {
                    code
                    lang
                }
            }
            """
            res_code = requests.post(
                graphql_url, 
                json={"query": query_code, "variables": {"submissionId": str(sub_id)}}, 
                headers=HEADERS
            )
            
            detail = res_code.json().get('data', {}).get('submissionDetail', {})
            
            if detail and detail.get('code'):
                code = detail['code']
                lang = detail['lang']
                
                # 自动匹配后缀名
                ext = "py" if "python" in lang else "cpp" if lang == "cpp" else "txt"
                
                with open(f"my-leetcode-code/{title}.{ext}", "w", encoding="utf-8") as f:
                    f.write(code)
                print(f"✅ {title} 代码保存成功！")
            else:
                print(f"❌ {title} 代码提货失败。")
                
            # 休息 1.5 秒，做个讲文明懂礼貌的机器人，防止被力扣封杀
            time.sleep(1.5) 
            
        print("🎉 所有代码完美搬运进仓库！")
        
    except Exception as e:
        print(f"程序运行中途遇到小挫折: {e}")

if __name__ == "__main__":
    fetch_data()

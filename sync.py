import os
import requests
import time

# 从 GitHub 保险箱获取密钥
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
    print("准备解除封印，开始全量翻页抓取...")
    
    offset = 0
    limit = 40 # 每次拿40条记录，像翻书一样
    all_submissions = []
    
    # 【新增功能 1：自动翻页】
    while True:
        list_url = f"https://leetcode.cn/api/submissions/?offset={offset}&limit={limit}"
        print(f"正在查看第 {offset} 到 {offset+limit} 条历史记录...")
        
        response = requests.get(list_url, headers=HEADERS)
        if response.status_code != 200:
            print("获取清单失败，停止翻页。")
            break
            
        page_data = response.json().get('submissions_dump', [])
        if not page_data:
            break # 翻到底了，没有数据了，退出循环
            
        all_submissions.extend(page_data)
        offset += limit
        time.sleep(1) # 翻页停顿一下，防止被封
        
    print(f"清单整理完毕！一共找到了 {len(all_submissions)} 条历史记录！")
    
    if not os.path.exists("my-leetcode-code"):
        os.makedirs("my-leetcode-code")
        
    graphql_url = "https://leetcode.cn/graphql/"
    
    # 【新增功能 2：去重小本本】记录已经下载过的题目
    saved_titles = set()

    for sub in all_submissions:
        if sub.get('status_display') != 'Accepted':
            continue # 没通过的跳过
            
        title = sub.get('title', 'Unknown').replace(" ", "").replace("/", "_")
        
        # 如果这道题已经在小本本上了，就跳过
        if title in saved_titles:
            continue

        sub_id = sub.get('id') 
        print(f"准备提取代码: {title} ...")
        
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
            
            ext = "py" if "python" in lang else "cpp" if lang == "cpp" else "txt"
            
            with open(f"my-leetcode-code/{title}.{ext}", "w", encoding="utf-8") as f:
                f.write(code)
            print(f"✅ {title} 保存成功！")
            
            # 记录到小本本上，下次遇到同名的就不抓了
            saved_titles.add(title)
        else:
            print(f"❌ {title} 提货失败。")
            
        time.sleep(1.5) 
        
    print(f"🎉 任务圆满结束！一共成功保存了 {len(saved_titles)} 道题目的代码！")

if __name__ == "__main__":
    fetch_data()

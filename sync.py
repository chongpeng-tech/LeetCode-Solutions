import os
import requests
import time

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
    print("准备开始全量抓取...")
    
    offset = 0
    limit = 40
    all_submissions = []
    
    # 1. 翻页获取清单（加了防崩溃保护）
    while True:
        list_url = f"https://leetcode.cn/api/submissions/?offset={offset}&limit={limit}"
        print(f"正在查看第 {offset} 到 {offset+limit} 条历史记录...")
        try:
            # timeout=10 表示如果等了 10 秒力扣还不理我，就放弃，别死等
            response = requests.get(list_url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                break
            page_data = response.json().get('submissions_dump', [])
            if not page_data:
                break
            all_submissions.extend(page_data)
            offset += limit
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ 获取清单时网络波动: {e}")
            break
            
    print(f"清单整理完毕！一共找到了 {len(all_submissions)} 条历史记录！")
    
    if not os.path.exists("my-leetcode-code"):
        os.makedirs("my-leetcode-code")
        
    graphql_url = "https://leetcode.cn/graphql/"
    
    # 2. 【核心升级：断点续传】看看文件夹里已经有哪些题了
    saved_titles = set()
    for filename in os.listdir("my-leetcode-code"):
        # 把 ".py" 或 ".cpp" 后缀去掉，只留题目名字
        name_without_ext = os.path.splitext(filename)[0]
        saved_titles.add(name_without_ext)

    print(f"发现本地已经保存了 {len(saved_titles)} 道题目，将自动跳过它们。")

    # 3. 开始挨个抓取代码
    for sub in all_submissions:
        if sub.get('status_display') != 'Accepted':
            continue
            
        title = sub.get('title', 'Unknown').replace(" ", "").replace("/", "_")
        
        # 如果已经下载过了，直接跳过！
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
        
        # 【核心升级：给单次抓取穿上防弹衣】
        try:
            res_code = requests.post(
                graphql_url, 
                json={"query": query_code, "variables": {"submissionId": str(sub_id)}}, 
                headers=HEADERS,
                timeout=10 # 最多等 10 秒
            )
            
            detail = res_code.json().get('data', {}).get('submissionDetail', {})
            
            if detail and detail.get('code'):
                code = detail['code']
                lang = detail['lang']
                
                ext = "py" if "python" in lang else "cpp" if lang == "cpp" else "txt"
                
                with open(f"my-leetcode-code/{title}.{ext}", "w", encoding="utf-8") as f:
                    f.write(code)
                print(f"✅ {title} 保存成功！")
                saved_titles.add(title) # 存完记到小本本上
            else:
                print(f"❌ {title} 提货失败。")
                
        except Exception as e:
            # 如果这道题超时了，只打印警告，绝不崩溃，继续下一道！
            print(f"⚠️ {title} 抓取时网络超时，先跳过: {e}")
            
        # 把休息时间稍微延长到 2 秒，对力扣服务器温柔一点
        time.sleep(2) 
        
    print("🎉 本次运行结束！")

if __name__ == "__main__":
    fetch_data()

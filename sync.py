import os
import requests

# 1. 从 GitHub 保险箱获取密钥
SESSION = os.environ.get('LEETCODE_SESSION')
CSRF = os.environ.get('LEETCODE_CSRF_TOKEN')

HEADERS = {
    'Cookie': f'LEETCODE_SESSION={SESSION}; csrftoken={CSRF}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def fetch_data():
    # 这是一条力扣中文站更底层的秘密通道，直接返回你的提交记录和代码
    url = "https://leetcode.cn/api/submissions/?offset=0&limit=20"
    
    print("正在连接力扣中文站的底层数据通道...")
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"服务器返回状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"获取失败，服务器脸色不对，返回了: {response.text}")
            return
            
        data = response.json()
        submissions = data.get('submissions_dump', [])
        
        if not submissions:
            print("⚠️ 警告：没找到代码记录。有可能是 Cookie 昨天到现在过期了，如果一直这样提示，请重新去网页复制一次 Cookie。")
            return
            
        if not os.path.exists("my-leetcode-code"):
            os.makedirs("my-leetcode-code")
            
        # 2. 开始拆快递包裹
        for sub in submissions:
            # 我们只保存“通过 (Accepted)”的代码，忽略解答错误和编译错误的
            if sub.get('status_display') != 'Accepted':
                continue
                
            # 清理一下题目名字里的特殊符号，防止存文件时报错
            title = sub['title'].replace(" ", "").replace("/", "_") 
            lang = sub['lang']
            code = sub['code']
            
            print(f"✅ 成功抓取: {title} (语言: {lang})")
            
            # 你平时主要练 C++ 和 Python，这里自动帮你匹配后缀名
            ext = "py" if "python" in lang else "cpp" if lang == "cpp" else "txt"
            with open(f"my-leetcode-code/{title}.{ext}", "w", encoding="utf-8") as f:
                f.write(code)
            
        print("🎉 所有代码完美搬运进仓库！")
        
    except Exception as e:
        print(f"程序运行中途遇到小挫折: {e}")

if __name__ == "__main__":
    fetch_data()

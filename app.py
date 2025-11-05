"""
Flask应用主入口
"""

import os
from app import create_app
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 从环境变量获取配置，如果没有则使用默认值
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    # 启动应用
    app.run(debug=debug, host=host, port=port)
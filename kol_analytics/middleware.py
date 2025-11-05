from django.http import JsonResponse
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware:
    """
    全局异常处理中间件，捕获并处理应用程序中发生的异常
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            # 处理404错误
            if response.status_code == 404:
                return render(request, 'errors/404.html', status=404)
            # 处理500错误
            elif response.status_code == 500:
                return render(request, 'errors/500.html', status=500)
            return response
        except Exception as e:
            # 记录异常日志
            logger.exception("发生未处理的异常")
            
            # 如果是AJAX请求，返回JSON错误响应
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': '发生服务器错误',
                    'detail': str(e) if settings.DEBUG else '请联系管理员'
                }, status=500)
            
            # 否则渲染500错误页面
            return render(request, 'errors/500.html', {'error': str(e) if settings.DEBUG else '服务器内部错误'}, status=500)


# 导入设置
from django.conf import settings
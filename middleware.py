from flask import request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import time
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

def init_middleware(app):
    """Initialize all middleware components"""
    limiter.init_app(app)
    cache.init_app(app)
    
    @app.before_request
    def log_request():
        g.start_time = time.time()
        logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    @app.after_request
    def log_response(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.info(f"Response: {response.status_code} in {duration:.3f}s")
        return response
    
    # Error handling middleware
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': e.retry_after
        }), 429
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong. Please try again later.'
        }), 500
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found.'
        }), 404


def rate_limit_by_user(limit_string):
    """Rate limit decorator that uses user ID from JWT token"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            
            user_id = None
            if 'Authorization' in request.headers:
                try:
                    import jwt
                    from flask import current_app
                    token = request.headers['Authorization'].split(' ')[1]
                    data = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
                    user_id = data.get('user_id')
                except:
                    pass
            
            
            key = f"user:{user_id}" if user_id else get_remote_address()
            
            
            cache_key = f"rate_limit:{key}"
            current_requests = cache.get(cache_key) or 0
            
            if current_requests >= 50:  
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                }), 429
            
            cache.set(cache_key, current_requests + 1, timeout=3600)  # 1 hour
            return f(*args, **kwargs)
        return wrapped
    return decorator


def cache_response(timeout=300):
    """Cache response decorator"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
           
            cache_key = f"{f.__name__}:{request.path}:{request.args}"
            
            
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            
            response = f(*args, **kwargs)
            cache.set(cache_key, response, timeout=timeout)
            return response
        return wrapped
    return decorator


def security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response 
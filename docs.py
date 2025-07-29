from flask import Blueprint, render_template, jsonify
from auth import token_required

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/api-docs')
def api_documentation():
    """Main API documentation page"""
    return render_template('api_docs.html')

@docs_bp.route('/api-docs/json')
def api_docs_json():
    """API documentation in JSON format"""
    docs = {
        "title": "AI Website Builder API Documentation",
        "version": "1.0.0",
        "description": "Complete API for AI-driven website generation and management",
        "base_url": "http://localhost:5000",
        "endpoints": {
            "authentication": {
                "signup": {
                    "method": "POST",
                    "url": "/signup",
                    "description": "Register a new user",
                    "request_body": {
                        "email": "user@example.com",
                        "password": "password123",
                        "role": "Editor"
                    },
                    "response": {
                        "token": "jwt_token_here"
                    }
                },
                "login": {
                    "method": "POST", 
                    "url": "/login",
                    "description": "Login user and get JWT token",
                    "request_body": {
                        "email": "user@example.com",
                        "password": "password123"
                    },
                    "response": {
                        "token": "jwt_token_here"
                    }
                }
            },
            "admin": {
                "list_roles": {
                    "method": "GET",
                    "url": "/roles",
                    "description": "List all roles (Admin only)",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    }
                },
                "create_role": {
                    "method": "POST",
                    "url": "/roles", 
                    "description": "Create a new role (Admin only)",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    },
                    "request_body": {
                        "name": "Moderator",
                        "permissions": ["view_websites", "edit_own_website"]
                    }
                },
                "assign_role": {
                    "method": "PUT",
                    "url": "/users/<user_id>/role",
                    "description": "Assign role to user (Admin only)",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    },
                    "request_body": {
                        "role_id": "role_object_id"
                    }
                }
            },
            "websites": {
                "create_website": {
                    "method": "POST",
                    "url": "/websites",
                    "description": "Create a new website (Admin/Editor)",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    },
                    "request_body": {
                        "data": {
                            "title": "My Website",
                            "hero_section": {
                                "heading": "Welcome",
                                "subheading": "Subtitle"
                            }
                        }
                    }
                },
                "get_websites": {
                    "method": "GET",
                    "url": "/websites",
                    "description": "Get all websites (filtered by role)",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    }
                },
                "get_website": {
                    "method": "GET", 
                    "url": "/websites/<website_id>",
                    "description": "Get specific website",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    }
                },
                "update_website": {
                    "method": "PUT",
                    "url": "/websites/<website_id>",
                    "description": "Update website (Admin/Owner)",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    },
                    "request_body": {
                        "data": {
                            "title": "Updated Website"
                        }
                    }
                },
                "delete_website": {
                    "method": "DELETE",
                    "url": "/websites/<website_id>",
                    "description": "Delete website (Admin/Owner)",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    }
                }
            },
            "ai_generation": {
                "generate_website": {
                    "method": "POST",
                    "url": "/generate-website",
                    "description": "Generate website content using AI",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    },
                    "request_body": {
                        "business_type": "Restaurant",
                        "industry": "Food & Beverage",
                        "description": "Italian restaurant",
                        "model": "gemini"
                    },
                    "response": {
                        "msg": "Website generated successfully",
                        "website_id": "generated_website_id",
                        "content": "generated_content",
                        "ai_model_used": "gemini"
                    }
                }
            },
            "preview": {
                "preview_website": {
                    "method": "GET",
                    "url": "/preview/<website_id>",
                    "description": "Preview website (public)",
                    "response": "HTML page"
                },
                "preview_website_auth": {
                    "method": "GET", 
                    "url": "/preview-auth/<website_id>",
                    "description": "Preview website (authenticated)",
                    "headers": {
                        "Authorization": "Bearer <jwt_token>"
                    },
                    "response": "HTML page"
                }
            },
            "health": {
                "health_check": {
                    "method": "GET",
                    "url": "/health",
                    "description": "API health check",
                    "response": {
                        "status": "healthy",
                        "message": "AI Website Builder API is running"
                    }
                }
            }
        },
        "authentication": {
            "type": "JWT",
            "header": "Authorization: Bearer <token>",
            "token_expiry": "24 hours"
        },
        "rate_limiting": {
            "default": "200 requests per day, 50 per hour",
            "authenticated": "50 requests per hour per user",
            "ai_generation": "10 requests per hour per user"
        },
        "roles": {
            "Admin": {
                "permissions": ["manage_users", "manage_websites", "full_access"],
                "description": "Full system access"
            },
            "Editor": {
                "permissions": ["create_website", "edit_own_website", "view_websites"],
                "description": "Can create and edit their own websites"
            },
            "Viewer": {
                "permissions": ["view_websites"],
                "description": "Can only view websites"
            }
        },
        "ai_models": {
            "openai": {
                "model": "gpt-3.5-turbo",
                "description": "OpenAI's GPT-3.5 Turbo model"
            },
            "gemini": {
                "model": "gemini-2.5-flash", 
                "description": "Google's Gemini 2.5 Flash model"
            }
        }
    }
    return jsonify(docs) 
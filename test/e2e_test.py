"""
端到端测试脚本
测试完整的科研工作流
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
}

class E2ETest:
    def __init__(self):
        self.token = None
        self.test_results = []
    
    def log_result(self, name, passed, message=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "name": name,
            "passed": passed,
            "message": message
        })
        print(f"{status}: {name} - {message}")
    
    def test_register(self):
        """测试用户注册"""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register/",
                json=TEST_USER
            )
            passed = response.status_code in [200, 201]
            self.log_result("用户注册", passed, f"状态码: {response.status_code}")
            return passed
        except Exception as e:
            self.log_result("用户注册", False, str(e))
            return False
    
    def test_login(self):
        """测试用户登录"""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            if response.status_code == 200:
                self.token = response.json().get("access")
                self.log_result("用户登录", True, "获取token成功")
                return True
            else:
                self.log_result("用户登录", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("用户登录", False, str(e))
            return False
    
    def test_chat(self):
        """测试聊天功能"""
        if not self.token:
            self.log_result("聊天功能", False, "未登录")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"message": "你好，请介绍一下自己"}
            )
            passed = response.status_code == 200
            self.log_result("聊天功能", passed, f"响应: {response.json().get('response', '')[:50]}...")
            return passed
        except Exception as e:
            self.log_result("聊天功能", False, str(e))
            return False
    
    def test_agent_chat(self):
        """测试Agent聊天"""
        if not self.token:
            self.log_result("Agent聊天", False, "未登录")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/agent/chat/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"message": "现在几点了？"}
            )
            passed = response.status_code == 200
            self.log_result("Agent聊天", passed, f"响应: {response.json().get('response', '')[:50]}...")
            return passed
        except Exception as e:
            self.log_result("Agent聊天", False, str(e))
            return False
    
    def test_document_upload(self):
        """测试文档上传"""
        if not self.token:
            self.log_result("文档上传", False, "未登录")
            return False
        
        try:
            # 创建测试文件
            with open("test.pdf", "wb") as f:
                f.write(b"%PDF-1.4 test content")
            
            with open("test.pdf", "rb") as f:
                response = requests.post(
                    f"{BASE_URL}/documents/upload/",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files={"file": f},
                    data={"title": "测试文档"}
                )
            
            import os
            os.remove("test.pdf")
            
            passed = response.status_code in [200, 201]
            self.log_result("文档上传", passed, f"状态码: {response.status_code}")
            return passed
        except Exception as e:
            self.log_result("文档上传", False, str(e))
            return False
    
    def test_literature_chat(self):
        """测试文献助手"""
        if not self.token:
            self.log_result("文献助手", False, "未登录")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/literature/chat/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"message": "帮我找一下关于深度学习的文献"}
            )
            passed = response.status_code == 200
            self.log_result("文献助手", passed, f"状态码: {response.status_code}")
            return passed
        except Exception as e:
            self.log_result("文献助手", False, str(e))
            return False
    
    def test_collaboration(self):
        """测试协作研究"""
        if not self.token:
            self.log_result("协作研究", False, "未登录")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/collaboration/review/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"question": "如何提高深度学习模型准确率"}
            )
            passed = response.status_code == 200
            self.log_result("协作研究", passed, f"状态码: {response.status_code}")
            return passed
        except Exception as e:
            self.log_result("协作研究", False, str(e))
            return False
    
    def test_paper_create(self):
        """测试论文创建"""
        if not self.token:
            self.log_result("论文创建", False, "未登录")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/writing/papers/create/",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"title": "测试论文", "topic": "AI测试"}
            )
            passed = response.status_code == 200
            self.log_result("论文创建", passed, f"状态码: {response.status_code}")
            return passed
        except Exception as e:
            self.log_result("论文创建", False, str(e))
            return False
    
    def run_all(self):
        """运行所有测试"""
        print("\n" + "="*50)
        print("开始端到端测试")
        print("="*50 + "\n")
        
        # 注册和登录
        self.test_register()
        self.test_login()
        
        if not self.token:
            print("\n登录失败，停止测试")
            return
        
        # 功能测试
        self.test_chat()
        self.test_agent_chat()
        self.test_document_upload()
        self.test_literature_chat()
        self.test_collaboration()
        self.test_paper_create()
        
        # 输出汇总
        print("\n" + "="*50)
        print("测试汇总")
        print("="*50)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = len(self.test_results) - passed
        
        print(f"总计: {len(self.test_results)} | ✅ 通过: {passed} | ❌ 失败: {failed}")
        
        if failed > 0:
            print("\n失败的测试:")
            for r in self.test_results:
                if not r["passed"]:
                    print(f"  - {r['name']}: {r['message']}")
        
        return failed == 0

if __name__ == "__main__":
    test = E2ETest()
    success = test.run_all()
    exit(0 if success else 1)
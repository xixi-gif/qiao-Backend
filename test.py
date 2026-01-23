import requests
import json

# 配置后端接口地址（根据你的实际地址修改）
BASE_URL = "http://localhost:8090"


def test_login():
    """测试登录接口，获取 Token"""
    login_url = f"{BASE_URL}/api/auth/login"
    # 登录参数（替换为你实际的测试账号密码）
    login_data = {
        "phone": "15563326277",  # 你的测试手机号
        "password": "123456"  # 你的测试密码
    }

    try:
        print("=== 测试登录接口 ===")
        response = requests.post(
            login_url,
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"请求状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

        # 修复：适配你的返回字段（access_token 而非 accessToken）
        if response.status_code == 200:
            result = response.json()
            # 优先找 access_token，兼容 accessToken
            token = result.get("access_token") or result.get("accessToken")
            if token:
                print(f"\n✅ 登录成功，获取到 Token: {token[:20]}...")
                return token
            else:
                print("❌ 登录成功，但未返回 Token")
                return None
        else:
            print("❌ 登录失败")
            return None
    except Exception as e:
        print(f"❌ 登录接口请求异常: {str(e)}")
        return None


def test_profile(token):
    """测试 profile 接口（携带 Token）"""
    profile_url = f"{BASE_URL}/api/auth/profile"
    # 请求头携带 Token（注意：token_type 是 bearer，需拼接）
    headers = {
        "Authorization": f"bearer {token}",  # 适配你的 token_type
        "Content-Type": "application/json"
    }

    try:
        print("\n=== 测试 Profile 接口 ===")
        response = requests.get(
            profile_url,
            headers=headers,
            timeout=10
        )
        print(f"请求状态码: {response.status_code}")
        # 关键：先打印原始响应内容（无论是否是JSON）
        print(f"原始响应内容: {response.text}")

        # 尝试解析JSON
        try:
            resp_json = response.json()
            print(f"响应 JSON: {json.dumps(resp_json, ensure_ascii=False, indent=2)}")
        except:
            print("❌ JSON 解析失败（响应不是有效JSON）")

        if response.status_code == 200:
            print("✅ Profile 接口请求成功")
        else:
            print("❌ Profile 接口请求失败")
    except Exception as e:
        print(f"❌ Profile 接口请求异常: {str(e)}")


def test_profile_no_token():
    """测试 profile 接口（不携带 Token，预期返回 401）"""
    profile_url = f"{BASE_URL}/api/auth/profile"

    try:
        print("\n=== 测试 Profile 接口（无 Token）===")
        response = requests.get(
            profile_url,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"请求状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

        if response.status_code == 401:
            print("✅ 无 Token 时返回 401，符合预期")
        else:
            print("❌ 无 Token 时未返回 401，不符合预期")
    except Exception as e:
        print(f"❌ Profile 接口（无 Token）请求异常: {str(e)}")


if __name__ == "__main__":
    # 执行测试流程
    print("开始测试接口...\n")

    # 1. 测试登录
    token = test_login()

    # 2. 测试无 Token 的 profile 接口
    test_profile_no_token()

    # 3. 测试有 Token 的 profile 接口（如果登录成功）
    if token:
        test_profile(token)
    else:
        print("\n❌ 未获取到有效 Token，跳过带 Token 的 Profile 测试")

    print("\n接口测试完成！")
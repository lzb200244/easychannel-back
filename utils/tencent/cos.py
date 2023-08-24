import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sts.v20180813 import sts_client, models

import os

policy_map = {
    "img": json.dumps({
        "statement": [
            {
                "action": [
                    "name/cos:*"
                ],
                "effect": "Allow",
                "principal": {
                    "qcs": [
                        "qcs::cam::anyone:anyone"
                    ]
                },
                "resource": [
                    "qcs::cos:ap-nanjing:uid/1311013567:chat-1311013567/*"
                ],
                "sid": "any"
            }
        ],
        "version": "2.0"
    }),
    "file": json.dumps({
        "statement": [
            {
                "action": [
                    "name/cos:*"
                ],
                "effect": "Allow",
                "principal": {
                    "qcs": [
                        "qcs::cam::anyone:anyone"
                    ]
                },
                "resource": [
                    "qcs::cos:ap-nanjing:uid/1311013567:chat-file-1311013567/*"
                ],
                "sid": "costs-1691044220000000157454-6634-6"
            }
        ],
        "version": "2.0"
    })
}


def get_temp_credict(policy,region='ap-nanjing'):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(os.getenv("TENCENT_KEY"), os.getenv("TENCENT_PWD"))
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "sts.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = sts_client.StsClient(cred, region, clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.GetFederationTokenRequest()
        # {
        #     "Statement": [
        #         {
        #             "Action": [
        #                 "name/cos:*"
        #             ],
        #             "Effect": "Allow",
        #             "Principal": {
        #                 "qcs": [
        #                     "qcs::cam::anyone:anyone"
        #                 ]
        #             },
        #             "Resource": [
        #                 "qcs::cos:ap-nanjing:uid/1311013567:chat-file-1311013567/*"
        #             ],
        #             "Sid": "costs-1691044220000000157454-6634-6"
        #         }
        #     ],
        #     "version": "2.0"
        # }
        # params = {
        #     "Name": "chat",
        #     "Policy": json.dumps({
        #         "statement": [
        #             {
        #                 "action": [
        #                     "name/cos:*"
        #                 ],
        #                 "effect": "Allow",
        #                 "principal": {
        #                     "qcs": [
        #                         "qcs::cam::anyone:anyone"
        #                     ]
        #                 },
        #                 "resource": [
        #                     "qcs::cos:ap-nanjing:uid/1311013567:chat-1311013567/*"
        #                 ],
        #                 "sid": "any"
        #             }
        #         ],
        #         "version": "2.0"
        #     }),
        #     "DurationSeconds": 1800
        # }
        params = {
            "Name": "chat",
            "Policy": policy_map.get(policy),
            "DurationSeconds": 1800
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个GetFederationTokenResponse的实例，与请求对象对应
        resp = client.GetFederationToken(req)
        # 输出json格式的字符串回包
        return json.loads(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)


def get_temp_avatar_credict(region='ap-nanjing'):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(os.getenv('TENCENT_KEY'), os.getenv('TENCENT_PWD'))
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "sts.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = sts_client.StsClient(cred, region, clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.GetFederationTokenRequest()
        params = {
            "Name": "chat-avatar",
            "Policy": json.dumps({
                "statement": [
                    {
                        "action": [
                            "name/cos:*"
                        ],
                        "effect": "Allow",
                        "principal": {
                            "qcs": [
                                "qcs::cam::anyone:anyone"
                            ]
                        },
                        "resource": [
                            "qcs::cos:ap-nanjing:uid/1311013567:chat-avatar-1311013567/*"
                        ],
                        "sid": "costs-1689775236000000263047-36338-4"
                    }
                ],
                "version": "2.0"
            }),
            "DurationSeconds": 1800
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个GetFederationTokenResponse的实例，与请求对象对应
        resp = client.GetFederationToken(req)
        # 输出json格式的字符串回包
        return json.loads(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)

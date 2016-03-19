# coding: utf-8

import config, requests, json

# https://leancloud.cn/docs/rest_sms_api.html
# https://leancloud.cn/docs/sms_guide-js.html

headers = {"X-LC-Id": config.LC_APP_ID , "X-LC-Key": config.LC_APP_KEY, 'Content-Type': 'application/json'}

class SmsUtil():
    @staticmethod
    def requestCode(mobilePhoneNumber):
        data = {"mobilePhoneNumber": mobilePhoneNumber}
        result = requests.post(config.LC_REQUEST_SMS_CODE_API, data=json.dumps(data), headers=headers)
        # print result.status_code
        # print result.json()
        if (result.status_code == 204 or result.status_code == 200):
            return json.dumps({"error": 0})
        else:
            return json.dumps({"error": result.status_code})

    @staticmethod
    def verifyCode(mobilePhoneNumber, smsCode):
        api = "{}/{}?mobilePhoneNumber={}".format(config.LC_VERIFY_SMS_CODE_API, smsCode, mobilePhoneNumber)
        print api
        result = requests.post(api, headers=headers)
        # print result.status_code
        # print result.json()
        if (result.status_code == 204 or result.status_code == 200):
            return json.dumps({"error": 0})
        else:
            return json.dumps({"error": result.status_code})    
